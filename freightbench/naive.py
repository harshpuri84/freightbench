"""A deliberately naive rule-based extractor, included as a reference point.

It reads the labelled lines and copies what it finds. It does not resolve
entities, convert units, reconcile duplicates, or abstain. It is roughly the
thing a competent engineer writes in an afternoon and then discovers is wrong
in production, and it is here so the benchmark has a floor that is not zero and
so the pathology breakdown has something to discriminate.

Its failures are the interesting part: run `freightbench compare` and look at
which pathologies it collapses on.
"""

from __future__ import annotations

import re
from typing import Any, Optional

from .reference import LOCATIONS
from .schema import SCHEMA

_LABEL = {
    "mode": "Mode",
    "commodity_description": "Commodity",
    "volume_cbm": "Volume",
    "incoterm": "Incoterm",
    "freight_terms": "Freight terms",
    "customer_reference": "Our reference",
    "cargo_ready_date": "Cargo ready",
}


def _line(body: str, label: str) -> Optional[str]:
    m = re.search(rf"^{re.escape(label)}:\s*(.+)$", body, re.M)
    return m.group(1).strip() if m else None


def _city_to_locode(city_text: str, mode: Optional[str]) -> Optional[str]:
    key = city_text.strip().casefold()
    for k, (sea, air, _, display) in LOCATIONS.items():
        if key == k or key == display.casefold():
            # The naive bug: defaults to the seaport, ignoring mode entirely.
            return sea
    return None


def extract(doc: dict[str, Any]) -> list[dict[str, Any]]:
    body = doc["body"]
    rec: dict[str, Any] = {f.name: None for f in SCHEMA}

    for field_name, label in _LABEL.items():
        rec[field_name] = _line(body, label)

    if rec["volume_cbm"]:
        m = re.match(r"([\d.]+)", rec["volume_cbm"])
        rec["volume_cbm"] = float(m.group(1)) if m else None

    m = re.search(r"^Gross weight:\s*([\d.,]+)\s*(kg|lbs)?", body, re.M | re.I)
    if m:
        # The naive bug: takes the number as-is, whatever the unit said.
        rec["gross_weight_kg"] = float(m.group(1).replace(",", ""))

    m = re.search(r"^Pieces:\s*(\d+)\s*(\w+)?", body, re.M)
    if m:
        rec["pieces"] = int(m.group(1))
        rec["packaging_type"] = m.group(2)

    rec["shipper_name"] = _line(body, "Shipper")
    rec["consignee_name"] = _line(body, "Consignee")

    for f, label in (("origin_location", "Origin"), ("destination_location", "Destination")):
        v = _line(body, label)
        if v:
            rec[f] = _city_to_locode(v, rec.get("mode"))

    m = re.search(r"\bBK-\d{5}\b", doc.get("subject", "") + " " + body)
    if m:
        rec["booking_reference"] = m.group(0)

    # The naive bug: hazard is read from what the sender claims, not the commodity.
    if re.search(r"no dangerous goods", body, re.I):
        rec["dangerous_goods"] = False
    elif re.search(r"dangerous goods|hazmat|UN\d{4}", body, re.I):
        rec["dangerous_goods"] = True
    else:
        rec["dangerous_goods"] = False

    # The naive bug: one record per email, always.
    return [rec]


def predictions(corpus: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    return {doc["doc_id"]: extract(doc) for doc in corpus}
