"""The LLM harness pieces that are part of the benchmark definition.

Two things live here and both are versioned in the repo on purpose.

The **prompt** is part of what a published score means: two models scored with
different prompts are not comparable, so there is exactly one canonical prompt
and it changes only with PROMPT_VERSION. It states the schema and the output
contract. It does not coach any pathology beyond rules the README already
declares to be correct behaviour for every extractor.

The **parser** is lenient about wrappers (code fences, prose, a top-level
object instead of an array) because refusing to read a model's fenced JSON
would report a formatting quirk as an extraction failure. A response with no
recoverable JSON returns None so the caller can count parse failures
separately instead of silently scoring them as abstention.
"""

from __future__ import annotations

import json
import re
from typing import Any, Optional

from .schema import SCHEMA

PROMPT_VERSION = "2"

_RULE_HINT = {
    "exact": "exact code",
    "casefold": "text",
    "numeric": "number",
    "date": "date as YYYY-MM-DD",
    "code": "code",
    "boolean": "true/false",
}

_FENCE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL)


def _field_lines() -> str:
    return "\n".join(
        f"- {f.name} ({_RULE_HINT[f.compare]}): {f.description}" for f in SCHEMA
    )


def build_prompt(doc: dict[str, Any]) -> str:
    return f"""You are extracting structured booking data from a freight-forwarding email.

Read the email below and return the booking(s) it contains as a JSON array.
Each shipment becomes one object with exactly these keys:

{_field_lines()}

Rules:
- Use null for any field the email does not state. Do not guess.
- If the email states two conflicting values for the same field, return null for that field rather than choosing one.
- If the email contains more than one distinct shipment, return one object per shipment, in the order they appear. Never merge them.
- Weights in kilograms, volumes in cubic metres, dates as YYYY-MM-DD, locations as UN/LOCODE, countries as ISO-2.
- Two exceptions to "do not guess", because these follow from the goods rather than from what the sender writes. Derive them even when the email does not state them, and do not treat the sender's opinion as authoritative:
  - dangerous_goods and un_number follow from the commodity. If the commodity is regulated, say so and give the UN number even when the sender says no declaration is needed.
  - origin_location and destination_location are UN/LOCODEs derived from the named place and the mode. A city's seaport and airport are different entities.
- Return only the JSON array. No commentary.

Subject: {doc["subject"]}

{doc["body"]}"""


def parse_response(text: str) -> Optional[list[dict[str, Any]]]:
    """Recover a list of shipment records from a model response, or None."""
    if not text or not text.strip():
        return None
    candidates = [text.strip()]
    candidates += [m.strip() for m in _FENCE.findall(text)]
    # First [...] or {...} span in the raw text, for JSON wrapped in prose.
    for opener, closer in (("[", "]"), ("{", "}")):
        start, end = text.find(opener), text.rfind(closer)
        if start != -1 and end > start:
            candidates.append(text[start : end + 1])
    for c in candidates:
        try:
            value = json.loads(c)
        except ValueError:
            continue
        if isinstance(value, dict) and isinstance(value.get("shipments"), list):
            value = value["shipments"]
        if isinstance(value, dict):
            value = [value]
        if isinstance(value, list) and all(isinstance(r, dict) for r in value):
            return value
    return None
