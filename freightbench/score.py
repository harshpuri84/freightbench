"""Scoring.

Two design decisions worth arguing with:

1. **A wrong value and a missing value are not the same error.** They are counted
   separately, because they have opposite operational consequences. A null routes
   the booking to a human. A confident wrong value goes straight through and gets
   discovered when someone is invoiced for it. Any metric that averages the two
   into one "accuracy" number is hiding the expensive failure inside the cheap one.

2. **The headline number is per-field, not per-document.** Document-level exact
   match is too brittle to steer on: it cannot tell you whether you have one
   systematic failure or thirty scattered ones.
"""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field as dc_field
from typing import Any, Optional

from .schema import FIELDS_BY_NAME, SCHEMA

# Outcome taxonomy. The whole point is that these stay distinct.
CORRECT = "correct"
WRONG = "wrong"            # a value was produced and it is not the truth
MISSED = "missed"          # truth had a value, prediction is null
HALLUCINATED = "hallucinated"  # truth is null, prediction invented a value
ABSTAINED_OK = "abstained_ok"  # truth is null, prediction is null


@dataclass
class FieldResult:
    doc_id: str
    field: str
    outcome: str
    expected: Any
    got: Any
    criticality: str


@dataclass
class Report:
    results: list[FieldResult] = dc_field(default_factory=list)

    # -- aggregate views ----------------------------------------------------

    def counts(self) -> dict[str, int]:
        c: dict[str, int] = defaultdict(int)
        for r in self.results:
            c[r.outcome] += 1
        return dict(c)

    def pass_rate(self, criticality: Optional[str] = None) -> float:
        rows = [r for r in self.results
                if criticality is None or r.criticality == criticality]
        if not rows:
            return 0.0
        ok = sum(1 for r in rows if r.outcome in (CORRECT, ABSTAINED_OK))
        return ok / len(rows)

    def hallucination_rate(self) -> float:
        """Of the fields that were legitimately absent, how many were invented."""
        absent = [r for r in self.results
                  if r.outcome in (HALLUCINATED, ABSTAINED_OK)]
        if not absent:
            return 0.0
        return sum(1 for r in absent if r.outcome == HALLUCINATED) / len(absent)

    def by_field(self) -> dict[str, dict[str, int]]:
        out: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
        for r in self.results:
            out[r.field][r.outcome] += 1
        return {k: dict(v) for k, v in out.items()}

    def worst_fields(self, n: int = 8) -> list[tuple[str, float, int]]:
        rows: list[tuple[str, float, int]] = []
        for name, outcomes in self.by_field().items():
            total = sum(outcomes.values())
            ok = outcomes.get(CORRECT, 0) + outcomes.get(ABSTAINED_OK, 0)
            rows.append((name, ok / total if total else 0.0, total))
        return sorted(rows, key=lambda t: t[1])[:n]


# -- comparison rules -------------------------------------------------------

_WS = re.compile(r"\s+")
_PUNCT = re.compile(r"[^\w\s]")


def _norm_text(v: Any) -> str:
    s = _PUNCT.sub("", str(v).casefold())
    return _WS.sub(" ", s).strip()


def _company_key(v: Any) -> str:
    """Company names differ by legal suffix far more often than by identity.

    'Vantage Components BV' and 'Vantage Components' are the same party, and an
    extractor should not be penalised for the suffix. 'Vantage Components' and
    'Vantage Holdings' are not.
    """
    s = _norm_text(v)
    for suffix in (" bv", " gmbh", " ltd", " limited", " inc", " pte ltd",
                   " pte", " pvt ltd", " pvt", " co", " nv", " sa", " ag"):
        if s.endswith(suffix):
            s = s[: -len(suffix)]
    return s.strip()


def values_match(field_name: str, expected: Any, got: Any) -> bool:
    rule = FIELDS_BY_NAME[field_name].compare
    if rule == "numeric":
        try:
            e, g = float(expected), float(got)
        except (TypeError, ValueError):
            return False
        # 0.5% tolerance absorbs unit-conversion rounding, not unit confusion.
        return abs(e - g) <= max(abs(e) * 0.005, 0.01)
    if rule == "boolean":
        return bool(expected) is bool(got)
    if rule in ("exact", "code"):
        return str(expected).strip().upper() == str(got).strip().upper()
    if rule == "date":
        return str(expected).strip()[:10] == str(got).strip()[:10]
    if rule == "casefold":
        if field_name.endswith("_name"):
            return _company_key(expected) == _company_key(got)
        return _norm_text(expected) == _norm_text(got)
    raise ValueError(f"unknown compare rule {rule!r}")


def _is_null(v: Any) -> bool:
    return v is None or (isinstance(v, str) and not v.strip())


def score_record(doc_id: str, expected: dict[str, Any], got: dict[str, Any],
                 contested: tuple[str, ...] = ()) -> list[FieldResult]:
    out: list[FieldResult] = []
    for f in SCHEMA:
        # A contested field has no assertable truth. Scoring it either way would
        # reward guessing, so it is excluded from the denominator entirely and
        # judged separately by the conflict-detection check.
        if f.name in contested:
            continue
        e, g = expected.get(f.name), got.get(f.name)
        if _is_null(e) and _is_null(g):
            outcome = ABSTAINED_OK
        elif _is_null(e):
            outcome = HALLUCINATED
        elif _is_null(g):
            outcome = MISSED
        else:
            outcome = CORRECT if values_match(f.name, e, g) else WRONG
        out.append(FieldResult(doc_id, f.name, outcome, e, g, f.criticality))
    return out


def score_corpus(expected_docs: list[dict[str, Any]],
                 predictions: dict[str, list[dict[str, Any]]]) -> Report:
    """expected_docs: the generated corpus as JSON. predictions: doc_id -> records."""
    report = Report()
    for doc in expected_docs:
        doc_id = doc["doc_id"]
        gt = doc["ground_truth"]
        contested = tuple(gt.get("contested_fields", []))
        truth_records = gt["shipments"]
        pred_records = predictions.get(doc_id, [])

        for i, truth in enumerate(truth_records):
            pred = pred_records[i] if i < len(pred_records) else {}
            report.results.extend(
                score_record(f"{doc_id}#{i}", truth, pred, contested)
            )
    return report


def render(report: Report) -> str:
    c = report.counts()
    total = sum(c.values())
    lines = [
        "FreightBench results",
        "=" * 60,
        f"fields scored          {total}",
        f"pass rate (all)        {report.pass_rate():.1%}",
        f"pass rate (critical)   {report.pass_rate('critical'):.1%}",
        "",
        "outcome breakdown",
        "-" * 60,
    ]
    for k in (CORRECT, ABSTAINED_OK, WRONG, MISSED, HALLUCINATED):
        n = c.get(k, 0)
        lines.append(f"  {k:<16} {n:>6}  {n / total:>6.1%}" if total else f"  {k:<16} {n:>6}")
    lines += [
        "",
        f"hallucination rate     {report.hallucination_rate():.1%}",
        "  (of fields that were legitimately absent, the share invented anyway)",
        "",
        "weakest fields",
        "-" * 60,
    ]
    for name, rate, n in report.worst_fields():
        lines.append(f"  {name:<28} {rate:>6.1%}  (n={n})")
    return "\n".join(lines)
