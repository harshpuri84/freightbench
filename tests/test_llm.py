"""Tests for the LLM harness pieces that are part of the benchmark definition.

The prompt is versioned because it is part of what a published score means.
The parser is lenient because refusing to parse a model's fenced JSON would
report a formatting quirk as an extraction failure.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from freightbench.generate import Generator  # noqa: E402
from freightbench.llm import PROMPT_VERSION, build_prompt, parse_response  # noqa: E402
from freightbench.schema import SCHEMA  # noqa: E402


class TestBuildPrompt(unittest.TestCase):
    def setUp(self):
        self.doc = Generator(7).corpus(1)[0].to_json()

    def test_prompt_names_every_schema_field(self):
        p = build_prompt(self.doc)
        for f in SCHEMA:
            self.assertIn(f.name, p)

    def test_prompt_contains_the_document(self):
        p = build_prompt(self.doc)
        self.assertIn(self.doc["subject"], p)
        self.assertIn(self.doc["body"], p)

    def test_prompt_states_null_and_order_rules(self):
        p = build_prompt(self.doc)
        self.assertIn("null", p)
        self.assertIn("order they appear", p)

    def test_prompt_does_not_leak_ground_truth(self):
        p = build_prompt(self.doc)
        self.assertNotIn("ground_truth", p)
        self.assertNotIn("pathology", p)

    def test_version_exists(self):
        self.assertTrue(PROMPT_VERSION)


class TestParseResponse(unittest.TestCase):
    def test_clean_array(self):
        out = parse_response('[{"mode": "AIR"}, {"mode": "LCL"}]')
        self.assertEqual(out, [{"mode": "AIR"}, {"mode": "LCL"}])

    def test_fenced_json_with_prose(self):
        text = 'Here is the extraction:\n```json\n[{"mode": "AIR"}]\n```\nDone.'
        self.assertEqual(parse_response(text), [{"mode": "AIR"}])

    def test_single_object_becomes_one_record(self):
        self.assertEqual(parse_response('{"mode": "FCL"}'), [{"mode": "FCL"}])

    def test_shipments_wrapper_unwrapped(self):
        text = '{"shipments": [{"mode": "AIR"}, {"mode": "AIR"}]}'
        self.assertEqual(parse_response(text), [{"mode": "AIR"}, {"mode": "AIR"}])

    def test_garbage_returns_none(self):
        self.assertIsNone(parse_response("I could not find a booking here."))

    def test_empty_returns_none(self):
        self.assertIsNone(parse_response(""))


if __name__ == "__main__":
    unittest.main()
