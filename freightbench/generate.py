"""Deterministic generator for synthetic booking-request emails.

Given a seed, the corpus is byte-identical on every machine. That matters more
than it sounds: an eval whose inputs drift cannot tell you whether a score moved
because the model changed or because the data did.

v0.3 draws an email Texture (register, layout, furniture) orthogonally to
pathology. The semantic payload of each pathology is unchanged; what varies is
the skin around it. Same seed still means byte-identical output.
"""

from __future__ import annotations

import re
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

REGISTERS = ("formal_esl", "terse_ops", "casual_internal", "newbie")
LAYOUTS = ("block", "prose", "bullets", "table")  # + one_liner, clean-only

GREETINGS = {
    "formal_esl": ("Respected Sir/ Madam,", "Dear Sir/Madam,", "Dear Sirs,"),
    "terse_ops": ("", "Hi -"),
    "casual_internal": ("Dear Freight Team,", "Hi team,", "Hi both,"),
    "newbie": ("Hello,", "Hi,", "Dear Sir/Madam,"),
}

INTROS = {
    "formal_esl": (
        "We kindly request you to quote and book the following shipment at your earliest convenience.",
        "Please find the shipment details below. We shall be grateful for your confirmation.",
    ),
    "terse_ops": (
        "",
        "Pls quote:",
    ),
    "casual_internal": (
        "Could you quote the below?",
        "Please confirm receipt and provide an itemized quote with transit times by EOD.",
    ),
    "newbie": (
        "We have learned about your company's freight services, and I am writing this email to request a quotation for our first export.",
        "This is our first export shipment and I wanted to ask: do we need any special paperwork for this?",
    ),
}

SIGNOFFS = {
    "formal_esl": ("Thank you,", "Sincerely,", "Yours faithfully,"),
    "terse_ops": ("Rgds", "Thx", ""),
    "casual_internal": ("Thanks,", "Regards,"),
    "newbie": ("Thank you very much in advance,",),
}

TITLES = (
    "Logistics Coordinator",
    "Export Manager",
    "Shipping Executive",
    "Supply Chain Officer",
)

DISCLAIMER = (
    "This email and any attachments are intended only for the use of the individual "
    "or entity to which they are addressed and may contain confidential information. "
    "If you have received this email in error, please notify the sender."
)

ON_BEHALF = (
    "On behalf of our client we would like to book the following.",
    "We act as forwarding agents for {shipper_name} and would like to place the booking below.",
    "Our principal {shipper_name} has asked us to arrange the following shipment.",
)

PACKING_LIST_INTROS = (
    "--- attached packing list (transcribed) ---",
    "Packing list (attached) shows:",
    "From the attached PL:",
)

TRAILING_CORRECTIONS = (
    "Apologies, correction: the gross weight above is wrong. It should be {kg} kg. Everything else stands.",
    "Quick correction - please ignore the weight in the details above; it should be {kg} kg.",
    "One correction before you book: the gross weight should be {kg} kg, not the figure above.",
)

_PHONE_PREFIX = {
    "NL": "+31", "GB": "+44", "SG": "+65", "DE": "+49", "US": "+1", "IN": "+91",
}

_CC_BY_COMPANY = {name: cc for name, cc in COMPANIES}
_CC_BY_COMPANY.update({
    "Halcyon Freight Services": "GB",
    "Pathfinder Logistics BV": "NL",
    "Kingsgate Forwarding Ltd": "GB",
})

_LABEL_POOLS = {
    "mode": ("Mode", "Transport", "Service"),
    "origin": ("Origin", "Ex", "From", "POL"),
    "destination": ("Destination", "To", "POD"),
    "shipper": ("Shipper", "SHPR", "From party"),
    "consignee": ("Consignee", "Cnee", "CNEE"),
    "commodity": ("Commodity", "Cargo", "Goods"),
    "pieces": ("Pieces", "Qty", "Count"),
    "weight": ("Gross weight", "Gross wt", "GW", "Weight"),
    "ready": ("Cargo ready", "Cargo ready date", "Ready", "CRD"),
    "ref": ("Our reference", "Our ref", "Ref"),
    "vol": ("Volume", "Vol", "CBM"),
    "incoterm": ("Incoterm", "Incoterms", "Terms"),
    "freight": ("Freight terms", "Freight", "Frt"),
}


@dataclass(frozen=True)
class Texture:
    register: str        # voice: greeting, connective phrasing, sign-off
    layout: str          # how the field values are physically arranged
    subject_style: str   # ref | rfq | request_for | lane | thread | useless | two_bookings
    sig_style: str       # "full" | "name_company" | "mobile"
    footer: bool         # confidentiality disclaimer paragraph
    header_block: bool   # pasted To:/From:/Cc:/Subject: preamble
    cc_count: int        # 0..2 names in the Cc line (only if header_block)


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


def _company_slug(company: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", company.lower()).strip("-")


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

    # -- texture draw (MUST be first rng consumption in every builder) ------

    def _texture(self, pathology: str) -> Texture:
        """Draw order is: texture -> base record -> pathology-specific draws."""
        if pathology == "clean":
            layout = self.rng.choices(
                ("block", "prose", "bullets", "table", "one_liner"),
                weights=(30, 25, 20, 13, 12))[0]
        elif pathology == "multi_shipment":
            # Spec 2.4: two delimited segments; layouts block, bullets, prose.
            layout = self.rng.choices(
                ("block", "prose", "bullets"),
                weights=(35, 25, 25))[0]
        else:
            layout = self.rng.choices(
                ("block", "prose", "bullets", "table"),
                weights=(35, 25, 25, 15))[0]
        register = self.rng.choices(REGISTERS, weights=(25, 30, 30, 15))[0]
        sig_style = self.rng.choices(("full", "name_company", "mobile"),
                                     weights=(40, 40, 20))[0]
        if sig_style == "mobile" and register in ("formal_esl", "newbie"):
            sig_style = "name_company"
        header = self.rng.random() < 0.20
        return Texture(
            register=register,
            layout=layout,
            subject_style=self._subject_style(pathology),
            sig_style=sig_style,
            footer=self.rng.random() < 0.35,
            header_block=header,
            cc_count=self.rng.choices((0, 1, 2), weights=(55, 30, 15))[0] if header else 0,
        )

    def _subject_style(self, pathology: str) -> str:
        if pathology == "forwarded_thread":
            return "thread"
        if pathology == "multi_shipment":
            return "two_bookings"
        styles = ["ref", "rfq", "request_for", "lane", "useless"]
        if pathology == "date_ambiguity":
            # Must not carry any date; rfq templates often include Ready {date}.
            styles = ["ref", "request_for", "lane", "useless"]
        return self.rng.choice(styles)

    # -- evidence-safe value helpers (the only formatters renderers may use)

    def _wt_text(self, r: dict[str, Any], unit: str = "kg") -> str:
        v = r["gross_weight_kg"]
        if unit == "lbs":
            return f"{round(v * 2.20462, 1):g} lbs"
        return f"{int(v)} kg"

    def _vol_text(self, r: dict[str, Any]) -> str:
        return f"{r['volume_cbm']:g} cbm"

    def _ready_text(self, r: dict[str, Any], style: str) -> str:
        return _fmt_date(date.fromisoformat(r["cargo_ready_date"]), style)

    def _city(self, r: dict[str, Any], which: str) -> str:
        return LOCATIONS[r[which]][3]

    def _email_addr(self, name: str, company: str) -> str:
        parts = name.lower().split()
        local = f"{parts[0][0]}.{parts[-1]}" if parts else "ops"
        return f"{local}@{_company_slug(company)}.com"

    def _phone(self, company: Optional[str]) -> str:
        cc = _CC_BY_COMPANY.get(company or "", "NL")
        prefix = _PHONE_PREFIX.get(cc, "+31")
        if prefix == "+1":
            return (f"+1 {self.rng.randint(200, 999)} "
                    f"{self.rng.randint(200, 999)} {self.rng.randint(1000, 9999)}")
        return (f"{prefix} {self.rng.randint(2, 9)}{self.rng.randint(0, 9)}"
                f"{self.rng.randint(0, 9)}{self.rng.randint(0, 9)} "
                f"{self.rng.randint(1000, 9999)}")

    # -- layout renderers ---------------------------------------------------

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

    def _block_syn(self, r: dict[str, Any], *, weight_text: Optional[str] = None,
                   ready_text: Optional[str] = None, origin_text: Optional[str] = None,
                   omit: tuple[str, ...] = ()) -> str:
        o_city = origin_text or LOCATIONS[r["_o"]][3]
        d_city = LOCATIONS[r["_d"]][3]
        wt = weight_text if weight_text is not None else self._wt_text(r)
        rd = ready_text if ready_text is not None else r["cargo_ready_date"]
        lines = [
            f"Mode: {r['mode']}",
            f"Ex: {o_city}",
            f"To: {d_city}",
            f"Shipper: {r['shipper_name']}",
            f"Consignee: {r['consignee_name']}",
            f"Commodity: {r['commodity_description']}",
            f"Pieces: {r['pieces']} {r['packaging_type']}",
            f"Gross wt: {wt}",
            f"Vol: {self._vol_text(r)}",
        ]
        if "incoterm" not in omit:
            lines.append(f"Incoterm: {r['incoterm']}")
        if "cargo_ready_date" not in omit:
            lines.append(f"Cargo ready date: {rd}")
        lines += [
            f"Freight terms: {r['freight_terms']}",
            f"Ref: {r['customer_reference']}",
        ]
        return "\n".join(lines)

    def _prose(self, r: dict[str, Any], tex: Texture, *,
               weight_text: Optional[str] = None, ready_text: Optional[str] = None,
               origin_text: Optional[str] = None, omit: tuple[str, ...] = ()) -> str:
        o = origin_text or LOCATIONS[r["_o"]][3]
        d = LOCATIONS[r["_d"]][3]
        wt = weight_text or self._wt_text(r)
        vol = self._vol_text(r)
        mode = r["mode"]
        pcs = f"{r['pieces']} {r['packaging_type']}"
        commodity = r["commodity_description"]
        shipper = r["shipper_name"]
        consignee = r["consignee_name"]
        custref = r["customer_reference"]
        freight = r["freight_terms"].lower()
        ready = None
        if "cargo_ready_date" not in omit and r.get("cargo_ready_date"):
            ready = ready_text or self._ready_text(r, "long")
        incoterm = r["incoterm"] if "incoterm" not in omit and r.get("incoterm") else None
        reg = tex.register

        if reg == "terse_ops":
            bits = [
                f"{mode} ex {o} to {d}.",
                f"{pcs}, {wt} / {vol}, {commodity}.",
                f"Shipper {shipper} / cnee {consignee}.",
            ]
            tail = []
            if ready:
                tail.append(f"Ready {ready}")
            if incoterm:
                tail.append(incoterm)
            tail.append(f"freight {freight}")
            bits.append(", ".join(tail) + ".")
            bits.append(f"Ref {custref}.")
            return " ".join(bits)

        if reg == "formal_esl":
            parts = [
                f"We kindly request you to arrange movement of {pcs} of {commodity} "
                f"({wt}, {vol}) by {mode} from {o} to {d}.",
                f"Shipper is {shipper}, consignee {consignee}.",
            ]
            tail = []
            if ready:
                tail.append(f"cargo ready {ready}")
            if incoterm:
                tail.append(f"{incoterm} terms")
            tail.append(f"freight {freight}")
            parts.append(", ".join(tail).capitalize() + ".")
            parts.append(f"Our reference is {custref}. We shall be grateful for your confirmation.")
            return " ".join(parts)

        if reg == "newbie":
            parts = [
                f"We need to ship {commodity} from {o} to {d} by {mode} - this is our first export.",
                f"There are {pcs}, weighing {wt}, volume {vol}.",
                f"The shipper is {shipper} and the consignee is {consignee}.",
            ]
            if ready:
                parts.append(f"Cargo is ready {ready}.")
            if incoterm:
                parts.append(f"Commercial terms are {incoterm}, freight {freight}.")
            else:
                parts.append(f"Freight {freight}.")
            parts.append(f"Our reference is {custref}. Do we need any special paperwork for this?")
            return " ".join(parts)

        # casual_internal
        parts = [
            f"We need to move {pcs} of {commodity} ({wt}, {vol}) by {mode} from {o} to {d}.",
            f"Shipper is {shipper}, consignee {consignee}.",
        ]
        tail = []
        if ready:
            tail.append(f"cargo ready {ready}")
        if incoterm:
            tail.append(f"{incoterm} terms")
        tail.append(f"freight {freight}")
        parts.append(", ".join(tail).capitalize() + ".")
        parts.append(f"Our reference is {custref}.")
        return " ".join(parts)

    def _bullets(self, r: dict[str, Any], tex: Texture, *,
                 weight_text: Optional[str] = None, ready_text: Optional[str] = None,
                 origin_text: Optional[str] = None, omit: tuple[str, ...] = ()) -> str:
        del tex  # register is independent; bullets are a layout, not a voice
        pick = {k: self.rng.choice(v) for k, v in _LABEL_POOLS.items()}
        bullet = self.rng.choice(("- ", "* "))
        o = origin_text or LOCATIONS[r["_o"]][3]
        d = LOCATIONS[r["_d"]][3]
        wt = weight_text or self._wt_text(r)
        head = [
            f"{bullet}{pick['mode']}: {r['mode']}",
            f"{bullet}{pick['origin']}: {o}",
            f"{bullet}{pick['destination']}: {d}",
        ]
        mid = [
            f"{bullet}{pick['shipper']}: {r['shipper_name']}",
            f"{bullet}{pick['consignee']}: {r['consignee_name']}",
            f"{bullet}{pick['commodity']}: {r['commodity_description']}",
            f"{bullet}{pick['pieces']}: {r['pieces']} {r['packaging_type']}",
            f"{bullet}{pick['weight']}: {wt}",
            f"{bullet}{pick['vol']}: {self._vol_text(r)}",
        ]
        if "incoterm" not in omit and r.get("incoterm"):
            mid.append(f"{bullet}{pick['incoterm']}: {r['incoterm']}")
        if "cargo_ready_date" not in omit and r.get("cargo_ready_date"):
            rd = ready_text or self._ready_text(r, "long")
            mid.append(f"{bullet}{pick['ready']}: {rd}")
        mid.append(f"{bullet}{pick['freight']}: {r['freight_terms']}")
        mid.append(f"{bullet}{pick['ref']}: {r['customer_reference']}")
        self.rng.shuffle(mid)
        return "\n".join(head + mid)

    def _table(self, r: dict[str, Any], tex: Texture, *,
               weight_text: Optional[str] = None, ready_text: Optional[str] = None,
               origin_text: Optional[str] = None, omit: tuple[str, ...] = ()) -> str:
        del tex
        o = origin_text or LOCATIONS[r["_o"]][3]
        d = LOCATIONS[r["_d"]][3]
        wt = weight_text or self._wt_text(r)
        route = f"Route: {o} -> {d} ({r['mode']})"
        extras = []
        if "incoterm" not in omit and r.get("incoterm"):
            extras.append(r["incoterm"])
        extras.append(f"freight {r['freight_terms'].lower()}")
        route = route + ", " + ", ".join(extras)
        parties = f"Shipper: {r['shipper_name']} / Consignee: {r['consignee_name']}"
        commodity = f"Cargo: {r['commodity_description']}"
        header = "pcs   packaging   gross wt   volume"
        row = (f"{r['pieces']:<5} {r['packaging_type']:<12} {wt:<12} "
               f"{self._vol_text(r)}")
        tail_bits = []
        if "cargo_ready_date" not in omit and r.get("cargo_ready_date"):
            rd = ready_text or self._ready_text(r, "long")
            tail_bits.append(f"Cargo ready {rd}")
        tail_bits.append(f"Ref {r['customer_reference']}")
        tail = ". ".join(tail_bits) + "."
        return f"{route}\n{parties}\n{commodity}\n\n{header}\n{row}\n\n{tail}"

    def _render(self, r: dict[str, Any], tex: Texture, **kw: Any) -> str:
        kw = dict(kw)
        omit = kw.get("omit") or ()
        if (kw.get("ready_text") is None
                and "cargo_ready_date" not in omit
                and r.get("cargo_ready_date")):
            kw["ready_text"] = self._ready_text(r, self.rng.choice(("iso", "long")))
        layout = tex.layout
        if layout == "block":
            layout = self.rng.choice(("block", "block_syn"))
        if layout == "block":
            return self._block(r, **kw)
        if layout == "block_syn":
            return self._block_syn(r, **kw)
        if layout == "prose":
            return self._prose(r, tex, **kw)
        if layout == "bullets":
            return self._bullets(r, tex, **kw)
        if layout == "table":
            return self._table(r, tex, **kw)
        raise ValueError(f"unhandled layout {layout!r}")

    # -- furniture ----------------------------------------------------------

    def _header_block(self, tex: Texture, r: dict[str, Any], subject: str,
                      name: str, company: str) -> str:
        del r
        lines = [
            f"From: {name} <{self._email_addr(name, company)}>",
            f"To: bookings@{_company_slug(FORWARDING_AGENTS[0])}.com",
        ]
        if tex.cc_count:
            ccs = []
            for _ in range(tex.cc_count):
                cc_name = self._person()
                ccs.append(f"{cc_name} <{self._email_addr(cc_name, company)}>")
            lines.append("Cc: " + ", ".join(ccs))
        lines.append(f"Subject: {subject}")
        return "\n".join(lines) + "\n\n"

    def _open(self, tex: Texture, r: dict[str, Any], subject: str, *,
              name: str, company: str, intro_override: Optional[str] = None) -> str:
        head = self._header_block(tex, r, subject, name, company) if tex.header_block else ""
        greeting = self.rng.choice(GREETINGS[tex.register])
        intro = intro_override if intro_override is not None else self.rng.choice(INTROS[tex.register])
        chunks = [p for p in (greeting, intro) if p]
        if not chunks:
            return head
        return f"{head}" + "\n\n".join(chunks) + "\n\n"

    def _sig(self, tex: Texture, name: Optional[str] = None,
             company: Optional[str] = None) -> str:
        name = name or self._person()
        closing = self.rng.choice(SIGNOFFS[tex.register])
        if tex.sig_style == "mobile":
            if closing:
                block = f"\n\n{closing}\n{name}\n\nSent from my iPhone"
            else:
                block = f"\n\n{name}\n\nSent from my iPhone"
        elif tex.sig_style == "full":
            title = self.rng.choice(TITLES)
            lines = [closing, name, title, company or "", self._phone(company)]
            lines = [ln for ln in lines if ln]
            block = "\n\n" + "\n".join(lines)
        else:
            lines = [closing, name, company or ""]
            lines = [ln for ln in lines if ln]
            block = "\n\n" + "\n".join(lines)
        if tex.footer:
            block += "\n\n" + DISCLAIMER
        return block

    def _subject(self, tex: Texture, r: dict[str, Any]) -> str:
        style = tex.subject_style
        o = self._city(r, "_o")
        d = self._city(r, "_d")
        commodity = r.get("commodity_description") or "cargo"
        bref = r.get("booking_reference")
        if style == "two_bookings":
            return self.rng.choice((
                "Two bookings this week",
                "Two shipments this week",
                "Please quote both",
            ))
        if style == "thread":
            options = ["FW: FW: booking draft", "RE: booking draft", "FW: booking draft"]
            if bref:
                options = [f"RE: booking {bref}", f"FW: booking {bref}",
                           f"RE: {bref}"] + options
            return self.rng.choice(options)
        if style == "useless":
            return self.rng.choice(("booking", "quote request", "shipment", "quick question"))
        if style == "request_for":
            return f"Requesting Freight Quotation for {commodity}"
        if style == "lane":
            return f"{o} to {d} - {commodity}"
        if style == "rfq":
            if r.get("mode") == "AIR":
                qty = ""
                if r.get("pieces") is not None:
                    qty = f"{r['pieces']} {r['packaging_type']} "
                return f"RFQ - Air Freight Quote: {qty}{o} to {d}".replace("  ", " ")
            ocean = "Ocean LCL" if r.get("mode") == "LCL" else "Ocean FCL"
            vol = self._vol_text(r) + " " if r.get("volume_cbm") is not None else ""
            ready = ""
            if r.get("cargo_ready_date"):
                ready = f", Ready {self._ready_text(r, 'long')}"
            return f"RFQ - {ocean} Quote: {vol}{o} to {d}{ready}"
        # ref
        if bref:
            return f"Booking request {bref}"
        return "Quote request"

    def _ref_line(self, subject: str, r: dict[str, Any]) -> str:
        bref = r.get("booking_reference")
        if not bref or bref in subject:
            return ""
        return f"\nOur ref {bref}."

    def _document(self, doc_id: str, pathology: str, tex: Texture, r: dict[str, Any],
                  inner: str, *, company: str, note: str = "",
                  contested: Optional[list[str]] = None,
                  extra_after: str = "", intro_override: Optional[str] = None,
                  name: Optional[str] = None,
                  shipments: Optional[list[dict[str, Any]]] = None) -> Document:
        name = name or self._person()
        subject = self._subject(tex, r)
        body = (
            self._open(tex, r, subject, name=name, company=company,
                       intro_override=intro_override)
            + inner
            + self._ref_line(subject, r)
            + extra_after
            + self._sig(tex, name=name, company=company)
        )
        return Document(
            doc_id, pathology, subject, body,
            shipments if shipments is not None else [self._clean(r)],
            contested_fields=list(contested or []),
            note=note,
        )

    def _quote_old(self, old_text: str, inner_subject: str) -> str:
        style = self.rng.choice((1, 2, 3))
        if style == 1:
            sent = _fmt_date(BASE_DATE, "long")
            return (
                f"\n\n-----Original Message-----\n"
                f"From: planning\n"
                f"Sent: {sent}\n"
                f"To: bookings\n"
                f"Subject: {inner_subject}\n\n"
                f"{old_text}"
            )
        if style == 2:
            person = self._person()
            long_d = _fmt_date(BASE_DATE, "long")
            quoted = "\n".join(("> " + line) if line else ">"
                               for line in old_text.splitlines())
            return f"\n\nOn {long_d}, {person} wrote:\n{quoted}"
        person = self._person()
        return (
            f"\n\n________________________________\n"
            f"From: {person}\n"
            f"Subject: {inner_subject}\n\n"
            f"{old_text}"
        )

    def _shipment_headers(self) -> tuple[str, str]:
        style = self.rng.choice(("banner", "label", "numbered"))
        if style == "banner":
            return "=== SHIPMENT 1 ===", "=== SHIPMENT 2 ==="
        if style == "label":
            return "Shipment 1:", "Shipment 2:"
        return "1)", "2)"

    # -- pathology builders -------------------------------------------------

    def clean(self, doc_id: str) -> Document:
        tex = self._texture("clean")
        r = self._base()
        if tex.layout == "one_liner":
            return self._clean_one_liner(doc_id, tex, r)
        return self._document(
            doc_id, "clean", tex, r, self._render(r, tex),
            company=r["shipper_name"],
        )

    def _clean_one_liner(self, doc_id: str, tex: Texture, r: dict[str, Any]) -> Document:
        o = LOCATIONS[r["_o"]][3]
        dest = LOCATIONS[r["_d"]][3]
        wt = self._wt_text(r)
        mode = r["mode"]
        commodity = r["commodity_description"]
        sender_company = r["shipper_name"]
        if mode == "AIR":
            mode_phrase = "AIR freight"
        elif mode == "LCL":
            mode_phrase = "LCL sea freight"
        else:
            mode_phrase = "FCL sea freight"
        for key in ("pieces", "packaging_type", "volume_cbm", "incoterm",
                    "freight_terms", "customer_reference", "booking_reference",
                    "consignee_name", "cargo_ready_date", "shipper_name"):
            r[key] = None
        name = self._person()
        subject = self._subject(tex, r)
        head = self._header_block(tex, r, subject, name, sender_company) if tex.header_block else ""
        greeting = self.rng.choice(GREETINGS[tex.register])
        ask = (f"can you give us a price for {mode_phrase} {o} to {dest}, "
               f"about {wt} of {commodity}? Ready end of the month.")
        if greeting:
            g = greeting.rstrip(" -,").rstrip()
            line = f"{g}, {ask}"
        else:
            line = ask[0].upper() + ask[1:]
        body = f"{head}{line}" + self._sig(tex, name=name, company=sender_company)
        return Document(doc_id, "clean", subject, body, [self._clean(r)])

    def ambiguous_port(self, doc_id: str) -> Document:
        tex = self._texture("ambiguous_port")
        # Force a city where sea and air LOCODEs genuinely differ.
        r = self._base(mode=self.rng.choice(["AIR", "LCL"]))
        if r["_d"] == "shanghai":
            r["_d"] = "rotterdam"
            r["destination_location"] = self._locode("rotterdam", r["mode"])
        r["_o"] = "shanghai"
        r["origin_location"] = self._locode("shanghai", r["mode"])
        note = ("'Shanghai' is a city, not a location. Mode is the disambiguating "
                f"constraint: {r['mode']} means {r['origin_location']}.")
        return self._document(
            doc_id, "ambiguous_port", tex, r,
            self._render(r, tex, origin_text="Shanghai"),
            company=r["shipper_name"],
            extra_after="\n\nPlease confirm the terminal you will use.",
            note=note,
        )

    def weight_conflict(self, doc_id: str) -> Document:
        tex = self._texture("weight_conflict")
        r = self._base()
        stated = int(r["gross_weight_kg"])
        other = stated + self.rng.randrange(150, 900, 50)
        intro = self.rng.choice(PACKING_LIST_INTROS)
        excerpt = (f"\n\n{intro}\n"
                   f"Total pieces: {r['pieces']}\n"
                   f"Total gross weight: {other} kg")
        gt = self._clean(r)
        gt["gross_weight_kg"] = None  # contested, so the value is not assertable
        note = (f"Body says {stated} kg, attachment says {other} kg. Correct behaviour "
                "is to flag the conflict, not to silently prefer one source.")
        return self._document(
            doc_id, "weight_conflict", tex, r, self._render(r, tex),
            company=r["shipper_name"], extra_after=excerpt,
            contested=["gross_weight_kg"], note=note, shipments=[gt],
        )

    def unit_ambiguity(self, doc_id: str) -> Document:
        tex = self._texture("unit_ambiguity")
        r = self._base()
        kg = float(self.rng.randrange(500, 6000, 50))
        r["gross_weight_kg"] = kg
        lbs = round(kg * 2.20462, 1)
        note = (f"Stated as {lbs} lbs. Correct extraction normalises to {kg} kg. "
                "Copying the number verbatim is wrong by a factor of 2.2.")
        return self._document(
            doc_id, "unit_ambiguity", tex, r,
            self._render(r, tex, weight_text=self._wt_text(r, "lbs")),
            company=r["shipper_name"], note=note,
        )

    def date_ambiguity(self, doc_id: str) -> Document:
        tex = self._texture("date_ambiguity")
        r = self._base()
        d = BASE_DATE + timedelta(days=self.rng.randint(4, 11))
        r["cargo_ready_date"] = d.isoformat()
        # Another unambiguous EU-format date in the thread fixes the convention.
        anchor = BASE_DATE + timedelta(days=25)  # day > 12, so DD/MM is provable
        extra = (f"\n\nFor reference our previous shipment departed "
                 f"{_fmt_date(anchor, 'eu')}, same arrangement please.")
        note = (f"{_fmt_date(d, 'eu')} is ambiguous alone. The second date "
                f"({_fmt_date(anchor, 'eu')}) has a day above 12, which proves the "
                "sender writes DD/MM.")
        return self._document(
            doc_id, "date_ambiguity", tex, r,
            self._render(r, tex, ready_text=_fmt_date(d, "eu")),
            company=r["shipper_name"], extra_after=extra, note=note,
        )

    def agent_not_shipper(self, doc_id: str) -> Document:
        tex = self._texture("agent_not_shipper")
        r = self._base()
        agent = self.rng.choice(FORWARDING_AGENTS)
        intro = self.rng.choice(ON_BEHALF).format(shipper_name=r["shipper_name"])
        note = (f"The sender's company is {agent}, an agent. The shipper is "
                f"{r['shipper_name']}, named in the body.")
        return self._document(
            doc_id, "agent_not_shipper", tex, r, self._render(r, tex),
            company=agent, intro_override=intro,
            extra_after="\n\nPlease send the quote to me directly and invoice our office.",
            note=note,
        )

    def multi_shipment(self, doc_id: str) -> Document:
        tex = self._texture("multi_shipment")
        a = self._base()
        b = self._base()
        b["shipper_name"] = a["shipper_name"]
        b["shipper_country"] = a["shipper_country"]
        # Truth nulls booking references; they must not appear in the text either
        # or an extractor that copies them would be scored as hallucinating.
        a["booking_reference"] = None
        b["booking_reference"] = None
        if tex.layout == "prose":
            inner = (f"First shipment: {self._prose(a, tex)}\n\n"
                     f"Second shipment: {self._prose(b, tex)}")
        else:
            h1, h2 = self._shipment_headers()
            inner = (f"{h1}\n{self._render(a, tex)}\n\n"
                     f"{h2}\n{self._render(b, tex)}")
        gt_a, gt_b = self._clean(a), self._clean(b)
        return self._document(
            doc_id, "multi_shipment", tex, a, inner,
            company=a["shipper_name"],
            extra_after="\n\nThey must not be consolidated.",
            contested=["special_instructions"],
            note="Two records expected. Blending them into one is the failure.",
            shipments=[gt_a, gt_b],
        )

    def forwarded_thread(self, doc_id: str) -> Document:
        tex = self._texture("forwarded_thread")
        r = self._base()
        final_pieces = r["pieces"]
        old_pieces = final_pieces + self.rng.randint(3, 15)
        old = dict(r)
        old["pieces"] = old_pieces
        newest = self._render(r, tex)
        quoted = self._render(old, tex)
        extra = self._quote_old(quoted, "booking draft")
        note = (f"The quoted original says {old_pieces} pieces; the newest message "
                f"says {final_pieces}. Newest wins.")
        return self._document(
            doc_id, "forwarded_thread", tex, r, newest,
            company=r["shipper_name"], extra_after=extra,
            intro_override="Updated details below, please use these.",
            note=note,
        )

    def trailing_correction(self, doc_id: str) -> Document:
        tex = self._texture("trailing_correction")
        r = self._base()
        corrected = r["gross_weight_kg"]
        wrong = corrected + self.rng.randrange(200, 1200, 50)
        extra = "\n\n" + self.rng.choice(TRAILING_CORRECTIONS).format(kg=int(corrected))
        note = (f"First states {int(wrong)} kg, then corrects to {int(corrected)} kg. "
                "The correction is the answer.")
        return self._document(
            doc_id, "trailing_correction", tex, r,
            self._render(r, tex, weight_text=f"{int(wrong)} kg"),
            company=r["shipper_name"], extra_after=extra, note=note,
        )

    def missing_critical(self, doc_id: str) -> Document:
        tex = self._texture("missing_critical")
        r = self._base()
        r["incoterm"] = None
        note = ("No incoterm is stated anywhere. The correct extraction is null. "
                "A plausible guess routes a wrong term downstream instead of a human.")
        return self._document(
            doc_id, "missing_critical", tex, r,
            self._render(r, tex, omit=("incoterm",)),
            company=r["shipper_name"], note=note,
        )

    def dg_undeclared(self, doc_id: str) -> Document:
        tex = self._texture("dg_undeclared")
        r = self._base()
        dg_items = [c for c, v in COMMODITIES.items() if v[3]]
        commodity = self.rng.choice(dg_items)
        hs, _, un, _ = COMMODITIES[commodity]
        r.update(commodity_description=commodity,
                 dangerous_goods=True, un_number=un)
        note = (f"The sender explicitly says no DG declaration is needed. They are "
                f"wrong: {commodity} is {un}. Hazard follows from the commodity, "
                "not from the sender's assertion.")
        return self._document(
            doc_id, "dg_undeclared", tex, r, self._render(r, tex),
            company=r["shipper_name"],
            extra_after="\n\nNo dangerous goods declaration needed for this one.",
            note=note,
        )

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
