"""Field schema for a freight booking request.

The unit of evaluation is a field, not a document. A model that gets 34 of 35
fields right and silently invents the 35th is not 97% correct; it is wrong in a
way that costs money downstream. So every field carries its own criticality and
its own comparison rule.
"""

from dataclasses import dataclass
from typing import Callable, Literal, Optional

Criticality = Literal["critical", "standard", "optional"]
Compare = Literal["exact", "casefold", "numeric", "date", "code", "boolean"]


@dataclass(frozen=True)
class Field:
    name: str
    compare: Compare
    criticality: Criticality
    description: str
    # A field that is legitimately absent from the source document. The correct
    # extraction is null. Inventing a value here is a hallucination, and it is
    # scored far more harshly than failing to find a value that was present.
    nullable: bool = True


SCHEMA: tuple[Field, ...] = (
    # --- identity -----------------------------------------------------------
    Field("booking_reference", "code", "critical", "Sender's own booking or quote reference"),
    Field("customer_reference", "code", "standard", "Customer PO or internal reference"),
    Field("mode", "exact", "critical", "AIR | LCL | FCL"),
    Field("service_level", "casefold", "optional", "Express, standard, economy"),
    # --- parties ------------------------------------------------------------
    Field("shipper_name", "casefold", "critical", "Legal name of the shipping party"),
    Field("shipper_country", "code", "critical", "ISO-2 country of the shipper"),
    Field("consignee_name", "casefold", "critical", "Legal name of the receiving party"),
    Field("consignee_country", "code", "critical", "ISO-2 country of the consignee"),
    Field("notify_party_name", "casefold", "optional", "Party to notify on arrival"),
    # --- routing ------------------------------------------------------------
    Field("origin_location", "code", "critical", "UN/LOCODE of origin. Seaport and airport in the same city are different entities"),
    Field("destination_location", "code", "critical", "UN/LOCODE of destination"),
    # --- cargo --------------------------------------------------------------
    Field("pieces", "numeric", "critical", "Total piece count"),
    Field("gross_weight_kg", "numeric", "critical", "Gross weight normalised to kilograms"),
    Field("volume_cbm", "numeric", "critical", "Volume normalised to cubic metres"),
    Field("chargeable_weight_kg", "numeric", "standard", "Chargeable weight if stated"),
    Field("commodity_description", "casefold", "critical", "Free-text description of the goods"),
    Field("hs_code", "code", "standard", "Harmonised System code if stated"),
    Field("dangerous_goods", "boolean", "critical", "Whether the shipment is declared dangerous goods"),
    Field("un_number", "code", "standard", "UN number, required when dangerous_goods is true"),
    Field("packaging_type", "casefold", "optional", "Pallets, cartons, crates"),
    # --- commercial ---------------------------------------------------------
    Field("incoterm", "exact", "critical", "EXW, FCA, FOB, CIF, DAP, DDP"),
    Field("freight_terms", "exact", "standard", "PREPAID | COLLECT"),
    Field("currency", "code", "standard", "ISO-3 currency of any quoted amount"),
    Field("declared_value", "numeric", "optional", "Declared value of the goods"),
    # --- dates --------------------------------------------------------------
    Field("cargo_ready_date", "date", "critical", "Date the cargo is available for collection"),
    Field("requested_departure_date", "date", "standard", "Requested departure"),
    Field("requested_arrival_date", "date", "optional", "Requested or required arrival"),
    # --- handling -----------------------------------------------------------
    Field("pickup_required", "boolean", "standard", "Whether first-mile pickup is requested"),
    Field("pickup_address", "casefold", "optional", "Collection address if pickup is requested"),
    Field("delivery_required", "boolean", "standard", "Whether last-mile delivery is requested"),
    Field("delivery_address", "casefold", "optional", "Delivery address if requested"),
    Field("temperature_controlled", "boolean", "optional", "Reefer or temperature-controlled"),
    Field("stackable", "boolean", "optional", "Whether cargo is stackable"),
    Field("insurance_required", "boolean", "optional", "Whether cargo insurance is requested"),
    Field("special_instructions", "casefold", "optional", "Free-text handling instructions"),
)

FIELDS_BY_NAME = {f.name: f for f in SCHEMA}

CRITICAL_FIELDS = tuple(f.name for f in SCHEMA if f.criticality == "critical")

assert len(SCHEMA) == len(FIELDS_BY_NAME), "duplicate field name in SCHEMA"
