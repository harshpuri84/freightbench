"""Tests for the benchmark itself.

A benchmark that is not tested is an opinion with a percentage sign attached.
The properties that matter here are determinism, ground-truth correctness for
each pathology, and that the scorer keeps its outcome categories distinct.
"""

import json
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from freightbench.generate import Generator  # noqa: E402
from freightbench.naive import predictions as naive_predictions  # noqa: E402
from freightbench.pathologies import PATHOLOGIES  # noqa: E402
from freightbench.schema import CRITICAL_FIELDS, SCHEMA  # noqa: E402
from freightbench.score import (  # noqa: E402
    ABSTAINED_OK, CORRECT, HALLUCINATED, MISSED, WRONG,
    score_corpus, score_record, values_match,
)


class TestDeterminism(unittest.TestCase):
    def test_same_seed_same_corpus(self):
        a = [d.to_json() for d in Generator(99).corpus(33)]
        b = [d.to_json() for d in Generator(99).corpus(33)]
        self.assertEqual(a, b)

    def test_different_seed_differs(self):
        a = [d.body for d in Generator(1).corpus(11)]
        b = [d.body for d in Generator(2).corpus(11)]
        self.assertNotEqual(a, b)

    def test_every_pathology_represented(self):
        docs = Generator(5).corpus(len(PATHOLOGIES))
        self.assertEqual({d.pathology for d in docs}, {p.key for p in PATHOLOGIES})


class TestGroundTruth(unittest.TestCase):
    """Each pathology must encode the *correct behaviour*, not the stated text."""

    def setUp(self):
        self.docs = Generator(4242).corpus(len(PATHOLOGIES) * 4)
        self.by_key = {}
        for d in self.docs:
            self.by_key.setdefault(d.pathology, []).append(d)

    def test_missing_critical_expects_null(self):
        for d in self.by_key["missing_critical"]:
            self.assertIsNone(d.shipments[0]["incoterm"])
            self.assertNotIn("Incoterm:", d.body)

    def test_weight_conflict_is_contested_not_guessed(self):
        for d in self.by_key["weight_conflict"]:
            self.assertIn("gross_weight_kg", d.contested_fields)
            self.assertIsNone(d.shipments[0]["gross_weight_kg"])

    def test_unit_ambiguity_truth_is_kilograms(self):
        for d in self.by_key["unit_ambiguity"]:
            self.assertIn("lbs", d.body)
            kg = d.shipments[0]["gross_weight_kg"]
            lbs = float(d.body.split("Gross weight: ")[1].split(" lbs")[0])
            self.assertAlmostEqual(kg, lbs / 2.20462, places=0)

    def test_multi_shipment_has_two_records(self):
        for d in self.by_key["multi_shipment"]:
            self.assertEqual(len(d.shipments), 2)

    def test_dg_inferred_despite_sender_denial(self):
        for d in self.by_key["dg_undeclared"]:
            self.assertIn("No dangerous goods", d.body)
            self.assertTrue(d.shipments[0]["dangerous_goods"])
            self.assertIsNotNone(d.shipments[0]["un_number"])

    def test_ambiguous_port_resolves_by_mode(self):
        for d in self.by_key["ambiguous_port"]:
            rec = d.shipments[0]
            expected = "CNPVG" if rec["mode"] == "AIR" else "CNSHA"
            self.assertEqual(rec["origin_location"], expected)

    def test_origin_never_equals_destination(self):
        for d in self.docs:
            for rec in d.shipments:
                self.assertNotEqual(rec["origin_location"], rec["destination_location"])

    def test_trailing_correction_truth_is_the_correction(self):
        for d in self.by_key["trailing_correction"]:
            self.assertIn("correction", d.body.lower())
            corrected = int(d.shipments[0]["gross_weight_kg"])
            self.assertIn(f"should be {corrected} kg", d.body)


class TestComparisons(unittest.TestCase):
    def test_numeric_tolerance_absorbs_rounding_not_unit_error(self):
        self.assertTrue(values_match("gross_weight_kg", 1000.0, 1000.4))
        self.assertFalse(values_match("gross_weight_kg", 1000.0, 2204.6))

    def test_company_suffix_ignored_identity_is_not(self):
        self.assertTrue(values_match("shipper_name", "Vantage Components BV", "Vantage Components"))
        self.assertFalse(values_match("shipper_name", "Vantage Components BV", "Vantage Holdings"))

    def test_code_comparison_is_case_insensitive(self):
        self.assertTrue(values_match("origin_location", "CNSHA", "cnsha"))
        self.assertFalse(values_match("origin_location", "CNSHA", "CNPVG"))

    def test_boolean_strictness(self):
        self.assertTrue(values_match("dangerous_goods", True, True))
        self.assertFalse(values_match("dangerous_goods", True, False))


class TestScoring(unittest.TestCase):
    """The outcome categories must not collapse into each other."""

    def _truth(self, **kw):
        rec = {f.name: None for f in SCHEMA}
        rec.update(kw)
        return rec

    def test_hallucination_distinct_from_wrong(self):
        truth = self._truth(incoterm=None, mode="AIR")
        pred = {"incoterm": "FOB", "mode": "AIR"}
        outcomes = {r.field: r.outcome for r in score_record("d", truth, pred)}
        self.assertEqual(outcomes["incoterm"], HALLUCINATED)
        self.assertEqual(outcomes["mode"], CORRECT)

    def test_missed_distinct_from_wrong(self):
        truth = self._truth(mode="AIR", incoterm="FOB")
        pred = {"mode": None, "incoterm": "CIF"}
        outcomes = {r.field: r.outcome for r in score_record("d", truth, pred)}
        self.assertEqual(outcomes["mode"], MISSED)
        self.assertEqual(outcomes["incoterm"], WRONG)

    def test_correct_abstention_is_rewarded(self):
        truth = self._truth(un_number=None)
        outcomes = {r.field: r.outcome for r in score_record("d", truth, {"un_number": None})}
        self.assertEqual(outcomes["un_number"], ABSTAINED_OK)

    def test_contested_fields_excluded_from_scoring(self):
        truth = self._truth(gross_weight_kg=None, mode="AIR")
        results = score_record("d", truth, {"gross_weight_kg": 500.0, "mode": "AIR"},
                               contested=("gross_weight_kg",))
        self.assertNotIn("gross_weight_kg", {r.field for r in results})

    def test_empty_extractor_scores_above_zero_but_fails_critical(self):
        docs = [d.to_json() for d in Generator(11).corpus(22)]
        preds = {d["doc_id"]: [{} for _ in d["ground_truth"]["shipments"]] for d in docs}
        report = score_corpus(docs, preds)
        self.assertGreater(report.pass_rate(), 0.0)
        self.assertLess(report.pass_rate("critical"), 0.10)
        self.assertEqual(report.counts().get(HALLUCINATED, 0), 0)

    def test_naive_beats_empty_but_is_far_from_solved(self):
        docs = [d.to_json() for d in Generator(11).corpus(44)]
        empty = score_corpus(docs, {d["doc_id"]: [{}] for d in docs})
        naive = score_corpus(docs, naive_predictions(docs))
        self.assertGreater(naive.pass_rate("critical"), empty.pass_rate("critical"))
        self.assertLess(naive.pass_rate("critical"), 0.95)


class TestSchema(unittest.TestCase):
    def test_no_duplicate_fields(self):
        names = [f.name for f in SCHEMA]
        self.assertEqual(len(names), len(set(names)))

    def test_critical_fields_present(self):
        self.assertIn("incoterm", CRITICAL_FIELDS)
        self.assertIn("gross_weight_kg", CRITICAL_FIELDS)
        self.assertGreaterEqual(len(SCHEMA), 30)


class TestCLI(unittest.TestCase):
    def test_generate_and_baseline_run(self):
        root = Path(__file__).resolve().parents[1]
        out = root / "tests" / "_tmp_corpus.jsonl"
        try:
            subprocess.run([sys.executable, "-m", "freightbench", "generate",
                            "--n", "11", "--out", str(out)],
                           cwd=root, check=True, capture_output=True)
            lines = out.read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(lines), 11)
            json.loads(lines[0])
            r = subprocess.run([sys.executable, "-m", "freightbench", "naive",
                                "--corpus", str(out)],
                               cwd=root, check=True, capture_output=True, text=True)
            self.assertIn("pass rate by pathology", r.stdout)
        finally:
            out.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
