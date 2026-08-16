"""Reference data for generated documents. Entirely invented.

Locations deliberately include a city where the seaport and the airport are
distinct entities *sharing the city's name*, because that collision is the
point of the ambiguous_port pathology.

Only Shanghai qualifies. An earlier version also mapped Rotterdam to Amsterdam
Schiphol, Busan to Incheon, Felixstowe to Heathrow and Santos to Guarulhos.
That is a different claim: not "which of this city's two entities do you mean"
but "which airport serves this port city", a routing decision forwarders
resolve differently. Asserting it as truth penalised extractors for correctly
reading the place the document actually named, and it produced every single
LOCODE error in the first model run.
"""

LOCATIONS = {
    # city key -> (sea LOCODE, air LOCODE, country ISO-2, display city)
    "shanghai": ("CNSHA", "CNPVG", "CN", "Shanghai"),
    "rotterdam": ("NLRTM", "NLRTM", "NL", "Rotterdam"),
    "hamburg": ("DEHAM", "DEHAM", "DE", "Hamburg"),
    "singapore": ("SGSIN", "SGSIN", "SG", "Singapore"),
    "busan": ("KRPUS", "KRPUS", "KR", "Busan"),
    "felixstowe": ("GBFXT", "GBFXT", "GB", "Felixstowe"),
    "chennai": ("INMAA", "INMAA", "IN", "Chennai"),
    "santos": ("BRSSZ", "BRSSZ", "BR", "Santos"),
}

COMPANIES = [
    ("Vantage Components BV", "NL"),
    ("Kestrel Industrial Ltd", "GB"),
    ("Meridian Trading Co", "SG"),
    ("Nordwind Maschinenbau GmbH", "DE"),
    ("Blue Harbour Foods Pte Ltd", "SG"),
    ("Arclight Electronics Inc", "US"),
    ("Steelbrook Fabrication", "GB"),
    ("Calyx Pharma BV", "NL"),
    ("Ridgeline Outdoor Gear", "US"),
    ("Tamarind Textiles Pvt Ltd", "IN"),
]

FORWARDING_AGENTS = [
    "Halcyon Freight Services",
    "Pathfinder Logistics BV",
    "Kingsgate Forwarding Ltd",
]

# commodity -> (hs_code, is_dangerous, un_number, obviously_dangerous)
# obviously_dangerous marks goods a competent extractor should flag as DG from
# the description alone, even when the sender does not declare them.
COMMODITIES = {
    "consumer electronics": ("8517", False, None, False),
    "lithium-ion battery packs": ("8506", True, "UN3480", True),
    "aluminium extrusions": ("7604", False, None, False),
    "cotton fabric rolls": ("5208", False, None, False),
    "industrial paint, flammable": ("3208", True, "UN1263", True),
    "stainless steel fittings": ("7307", False, None, False),
    "packaged food ingredients": ("2106", False, None, False),
    "hydraulic pumps": ("8413", False, None, False),
    "aerosol cleaning spray": ("3402", True, "UN1950", True),
    "laboratory glassware": ("7017", False, None, False),
}

INCOTERMS = ["EXW", "FCA", "FOB", "CIF", "DAP", "DDP"]
PACKAGING = ["pallets", "cartons", "crates", "wooden cases"]
SERVICE_LEVELS = ["standard", "express", "economy"]
CURRENCIES = ["EUR", "USD", "GBP", "SGD"]

FIRST_NAMES = ["Marta", "Declan", "Priya", "Tomasz", "Ines", "Rafael", "Yuki",
               "Anneke", "Samir", "Greta", "Owen", "Lucia"]
LAST_NAMES = ["Vermeer", "Okafor", "Nair", "Kowalski", "Duarte", "Lindqvist",
              "Tanaka", "Bakker", "Haddad", "Rossi", "Mbeki", "Fontaine"]
