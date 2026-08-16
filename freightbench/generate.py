"""Deterministic generator for synthetic booking-request emails.

Given a seed, the corpus is byte-identical on every machine. That matters more
than it sounds: an eval whose inputs drift cannot tell you whether a score moved
because the model changed or because the data did.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field as dc_field
from datetime import date, timedelta
from typing import Any, Optional

from .reference import (
    COMMODITIES, COMPANIES, CURRENCIES, FIRST_NAMES, FORWARDING_AGENTS,
    INCOTERMS, LAST_NAMES, LOCATIONS, PACKAGING, SERVICE_LEVELS,
)
from .pathologies import PATHOLOGIES
from .schema import SCHEMA

BASE_DATE = date(2026, 3, 2)


@dataclass
class Document:
    doc_id: str
    pathology: str
    subject: str
    body: str
    shipments: list[dict[str, Any]] = dc_field(default_factory=list)
    contested_fields: list[str] = dc_field(default_factory=list)
    note: str = ""

    def to_json(self) -> dict[str, Any]:
        return {
            "doc_id": self.doc_id,
            "pathology": self.pathology,
            "subject": self.subject,
            "body": self.body,
            "ground_truth": {
                "shipments": self.shipments,
                "contested_fields": self.contested_fields,
            },
            "note": self.note,
        }


def _blank_record() -> dict[str, Any]:
    return {f.name: None for f in SCHEMA}


def _fmt_date(d: date, style: str) -> str:
    return {
        "iso": d.isoformat(),
        "eu": d.strftime("%d/%m/%Y"),
        "us": d.strftime("%m/%d/%Y"),
        "long": d.strftime("%d %b %Y"),
    }[style]


class Generator:
    """Builds one document per call. Pathology is chosen by the caller."""

    def __init__(self, seed: int = 20260811):
        self.rng = random.Random(seed)

    # -- building blocks ----------------------------------------------------

    def _person(self) -> str:
        return f"{self.rng.choice(FIRST_NAMES)} {self.rng.choice(LAST_NAMES)}"

    def _base(self, mode: Optional[str] = None) -> dict[str, Any]:
        r = _blank_record()
        mode = mode or self.rng.choice(["AIR", "LCL", "FCL"])
        o_key, d_key = self.rng.sample(list(LOCATIONS), 2)
        shipper, shipper_cc = self.rng.choice(COMPANIES)
        consignee, consignee_cc = self.rng.choice([c for c in COMPANIES if c[0] != shipper])
        commodity = self.rng.choice(list(COMMODITIES))
        hs, is_dg, un, _ = COMMODITIES[commodity]

        weight = float(self.rng.randrange(200, 12000, 50))
        r.update(
            booking_reference=f"BK-{self.rng.randint(10000, 99999)}",
            customer_reference=f"PO{self.rng.randint(100000, 999999)}",
            mode=mode,
            service_level=self.rng.choice(SERVICE_LEVELS),
            shipper_name=shipper,
            shipper_country=shipper_cc,
            consignee_name=consignee,
            consignee_country=consignee_cc,
            origin_location=self._locode(o_key, mode),
            destination_location=self._locode(d_key, mode),
            pieces=self.rng.randint(2, 40),
            gross_weight_kg=weight,
            volume_cbm=round(weight / self.rng.uniform(150, 320), 2),
            commodity_description=commodity,
            hs_code=hs,
            dangerous_goods=is_dg,
            un_number=un,
            packaging_type=self.rng.choice(PACKAGING),
            incoterm=self.rng.choice(INCOTERMS),
            freight_terms=self.rng.choice(["PREPAID", "COLLECT"]),
            currency=self.rng.choice(CURRENCIES),
            cargo_ready_date=(BASE_DATE + timedelta(days=self.rng.randint(3, 40))).isoformat(),
            pickup_required=self.rng.random() < 0.6,
            delivery_required=self.rng.random() < 0.5,
            temperature_controlled=False,
            stackable=self.rng.random() < 0.7,
            insurance_required=self.rng.random() < 0.3,
        )
        # The draws above keep the RNG stream stable, but a truth value is only
        # assertable if the rendered document evidences it. These fields are
        # never rendered by any template, so their truth is null: an extractor
        # that returns a value here is guessing, and the scorer should say so.
        for unrendered in ("service_level", "shipper_country", "consignee_country",
                           "hs_code", "currency", "pickup_required",
                           "delivery_required", "temperature_controlled",
                           "stackable", "insurance_required"):
            r[unrendered] = None
        r["_o"] = o_key
        r["_d"] = d_key
        return r

    @staticmethod
    def _locode(city_key: str, mode: str) -> str:
        sea, air, _, _ = LOCATIONS[city_key]
        return air if mode == "AIR" else sea

    @staticmethod
    def _clean(r: dict[str, Any]) -> dict[str, Any]:
        return {k: v for k, v in r.items() if not k.startswith("_")}

    def _block(self, r: dict[str, Any], *, weight_text: Optional[str] = None,
               ready_text: Optional[str] = None, origin_text: Optional[str] = None,
               omit: tuple[str, ...] = ()) -> str:
        o_city = LOCATIONS[r["_o"]][3]
        d_city = LOCATIONS[r["_d"]][3]
        wt = weight_text if weight_text is not None else f"{int(r['gross_weight_kg'])} kg"
        rd = ready_text if ready_text is not None else r["cargo_ready_date"]
        lines = [
            f"Mode: {r['mode']}",
            f"Origin: {origin_text or o_city}",
            f"Destination: {d_city}",
            f"Shipper: {r['shipper_name']}",
            f"Consignee: {r['consignee_name']}",
            f"Commodity: {r['commodity_description']}",
            f"Pieces: {r['pieces']} {r['packaging_type']}",
            f"Gross weight: {wt}",
            f"Volume: {r['volume_cbm']} cbm",
        ]
        if "incoterm" not in omit:
            lines.append(f"Incoterm: {r['incoterm']}")
        if "cargo_ready_date" not in omit:
            lines.append(f"Cargo ready: {rd}")
        lines += [
            f"Freight terms: {r['freight_terms']}",
            f"Our reference: {r['customer_reference']}",
        ]
        return "\n".join(lines)

    def _sig(self, name: Optional[str] = None, company: Optional[str] = None) -> str:
        return f"\n\nBest regards,\n{name or self._person()}\n{company or ''}".rstrip()

    # -- pathology builders -------------------------------------------------

    def clean(self, doc_id: str) -> Document:
        r = self._base()
        body = ("Hi,\n\nPlease quote and book the following shipment.\n\n"
                + self._block(r) + self._sig(company=r["shipper_name"]))
        return Document(doc_id, "clean", f"Booking request {r['booking_reference']}",
                        body, [self._clean(r)])

    def ambiguous_port(self, doc_id: str) -> Document:
        # Force a city where sea and air LOCODEs genuinely differ.
        r = self._base(mode=self.rng.choice(["AIR", "LCL"]))
        if r["_d"] == "shanghai":
            r["_d"] = "rotterdam"
            r["destination_location"] = self._locode("rotterdam", r["mode"])
        r["_o"] = "shanghai"
        r["origin_location"] = self._locode("shanghai", r["mode"])
        body = ("Hello,\n\nWe need this moved as below. Origin is Shanghai.\n\n"
                + self._block(r, origin_text="Shanghai")
                + "\n\nPlease confirm the terminal you will use."
                + self._sig(company=r["shipper_name"]))
        note = ("'Shanghai' is a city, not a location. Mode is the disambiguating "
                f"constraint: {r['mode']} means {r['origin_location']}.")
        return Document(doc_id, "ambiguous_port",
                        f"Shipment ex Shanghai - {r['booking_reference']}",
                        body, [self._clean(r)], note=note)

    def weight_conflict(self, doc_id: str) -> Document:
        r = self._base()
        stated = int(r["gross_weight_kg"])
        other = stated + self.rng.randrange(150, 900, 50)
        body = ("Hi,\n\nBooking request below, packing list attached.\n\n"
                + self._block(r)
                + f"\n\n--- attached packing list (transcribed) ---\n"
                  f"Total pieces: {r['pieces']}\nTotal gross weight: {other} kg\n"
                + self._sig(company=r["shipper_name"]))
        gt = self._clean(r)
        gt["gross_weight_kg"] = None  # contested, so the value is not assertable
        note = (f"Body says {stated} kg, attachment says {other} kg. Correct behaviour "
                "is to flag the conflict, not to silently prefer one source.")
        return Document(doc_id, "weight_conflict",
                        f"Booking + packing list {r['booking_reference']}",
                        body, [gt], contested_fields=["gross_weight_kg"], note=note)

    def unit_ambiguity(self, doc_id: str) -> Document:
        r = self._base()
        kg = float(self.rng.randrange(500, 6000, 50))
        r["gross_weight_kg"] = kg
        lbs = round(kg * 2.20462, 1)
        body = ("Hi team,\n\nPlease arrange the shipment below.\n\n"
                + self._block(r, weight_text=f"{lbs} lbs")
                + self._sig(company=r["shipper_name"]))
        note = (f"Stated as {lbs} lbs. Correct extraction normalises to {kg} kg. "
                "Copying the number verbatim is wrong by a factor of 2.2.")
        return Document(doc_id, "unit_ambiguity",
                        f"Booking {r['booking_reference']}", body,
                        [self._clean(r)], note=note)

    def date_ambiguity(self, doc_id: str) -> Document:
        r = self._base()
        d = BASE_DATE + timedelta(days=self.rng.randint(4, 11))
        r["cargo_ready_date"] = d.isoformat()
        # Another unambiguous EU-format date in the thread fixes the convention.
        anchor = BASE_DATE + timedelta(days=25)  # day > 12, so DD/MM is provable
        body = ("Hello,\n\nAs discussed, please book:\n\n"
                + self._block(r, ready_text=_fmt_date(d, "eu"))
                + f"\n\nFor reference our previous shipment departed "
                  f"{_fmt_date(anchor, 'eu')}, same arrangement please."
                + self._sig(company=r["shipper_name"]))
        note = (f"{_fmt_date(d, 'eu')} is ambiguous alone. The second date "
                f"({_fmt_date(anchor, 'eu')}) has a day above 12, which proves the "
                "sender writes DD/MM.")
        return Document(doc_id, "date_ambiguity",
                        f"Re: booking {r['booking_reference']}", body,
                        [self._clean(r)], note=note)

    def agent_not_shipper(self, doc_id: str) -> Document:
        r = self._base()
        agent = self.rng.choice(FORWARDING_AGENTS)
        body = (f"Dear colleagues,\n\nOn behalf of our client we would like to book "
                f"the following.\n\n" + self._block(r)
                + "\n\nPlease send the quote to me directly and invoice our office."
                + self._sig(company=agent))
        note = (f"The sender's company is {agent}, an agent. The shipper is "
                f"{r['shipper_name']}, named in the body.")
        return Document(doc_id, "agent_not_shipper",
                        f"Booking on behalf of client - {r['booking_reference']}",
                        body, [self._clean(r)], note=note)

    def multi_shipment(self, doc_id: str) -> Document:
        a = self._base()
        b = self._base()
        b["shipper_name"] = a["shipper_name"]
        b["shipper_country"] = a["shipper_country"]
        body = ("Hi,\n\nTwo separate shipments this week, please quote both.\n\n"
                "=== SHIPMENT 1 ===\n" + self._block(a)
                + "\n\n=== SHIPMENT 2 ===\n" + self._block(b)
                + "\n\nThey must not be consolidated."
                + self._sig(company=a["shipper_name"]))
        # The subject line carries no reference and neither block renders one,
        # so the booking references are not evidenced anywhere.
        gt_a, gt_b = self._clean(a), self._clean(b)
        gt_a["booking_reference"] = None
        gt_b["booking_reference"] = None
        return Document(doc_id, "multi_shipment",
                        "Two bookings this week", body,
                        [gt_a, gt_b],
                        # "They must not be consolidated." is in the body; whether
                        # it belongs in special_instructions is judgment, not fact.
                        contested_fields=["special_instructions"],
                        note="Two records expected. Blending them into one is the failure.")

    def forwarded_thread(self, doc_id: str) -> Document:
        r = self._base()
        final_pieces = r["pieces"]
        old_pieces = final_pieces + self.rng.randint(3, 15)
        old = dict(r)
        old["pieces"] = old_pieces
        body = ("Hi,\n\nUpdated details below, please use these.\n\n"
                + self._block(r)
                + "\n\n-----Original Message-----\n"
                  "From: planning\nSubject: booking draft\n\n"
                + self._block(old)
                + self._sig(company=r["shipper_name"]))
        note = (f"The quoted original says {old_pieces} pieces; the newest message "
                f"says {final_pieces}. Newest wins.")
        return Document(doc_id, "forwarded_thread",
                        f"RE: booking {r['booking_reference']}", body,
                        [self._clean(r)], note=note)

    def trailing_correction(self, doc_id: str) -> Document:
        r = self._base()
        corrected = r["gross_weight_kg"]
        wrong = corrected + self.rng.randrange(200, 1200, 50)
        body = ("Hi,\n\nPlease book as follows.\n\n"
                + self._block(r, weight_text=f"{int(wrong)} kg")
                + f"\n\nApologies, correction: the gross weight above is wrong. "
                  f"It should be {int(corrected)} kg. Everything else stands."
                + self._sig(company=r["shipper_name"]))
        note = (f"First states {int(wrong)} kg, then corrects to {int(corrected)} kg. "
                "The correction is the answer.")
        return Document(doc_id, "trailing_correction",
                        f"Booking {r['booking_reference']} (corrected)", body,
                        [self._clean(r)], note=note)

    def missing_critical(self, doc_id: str) -> Document:
        r = self._base()
        r["incoterm"] = None
        body = ("Hello,\n\nPlease quote the below.\n\n"
                + self._block(r, omit=("incoterm",))
                + self._sig(company=r["shipper_name"]))
        note = ("No incoterm is stated anywhere. The correct extraction is null. "
                "A plausible guess routes a wrong term downstream instead of a human.")
        return Document(doc_id, "missing_critical",
                        f"Quote request {r['booking_reference']}", body,
                        [self._clean(r)], note=note)

    def dg_undeclared(self, doc_id: str) -> Document:
        r = self._base()
        dg_items = [c for c, v in COMMODITIES.items() if v[3]]
        commodity = self.rng.choice(dg_items)
        hs, _, un, _ = COMMODITIES[commodity]
        r.update(commodity_description=commodity,
                 dangerous_goods=True, un_number=un)
        body = ("Hi,\n\nStandard booking, nothing special.\n\n"
                + self._block(r)
                + "\n\nNo dangerous goods declaration needed for this one."
                + self._sig(company=r["shipper_name"]))
        note = (f"The sender explicitly says no DG declaration is needed. They are "
                f"wrong: {commodity} is {un}. Hazard follows from the commodity, "
                "not from the sender's assertion.")
        return Document(doc_id, "dg_undeclared",
                        f"Booking {r['booking_reference']}", body,
                        [self._clean(r)], note=note)

    # -- corpus -------------------------------------------------------------

    BUILDERS = {
        "clean": "clean",
        "ambiguous_port": "ambiguous_port",
        "weight_conflict": "weight_conflict",
        "unit_ambiguity": "unit_ambiguity",
        "date_ambiguity": "date_ambiguity",
        "agent_not_shipper": "agent_not_shipper",
        "multi_shipment": "multi_shipment",
        "forwarded_thread": "forwarded_thread",
        "trailing_correction": "trailing_correction",
        "missing_critical": "missing_critical",
        "dg_undeclared": "dg_undeclared",
    }

    def corpus(self, n: int = 200) -> list[Document]:
        """Round-robin across pathologies so every failure mode is represented."""
        keys = [p.key for p in PATHOLOGIES]
        docs: list[Document] = []
        for i in range(n):
            key = keys[i % len(keys)]
            builder = getattr(self, self.BUILDERS[key])
            docs.append(builder(f"fb-{i + 1:04d}"))
        return docs
