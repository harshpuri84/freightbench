"""The pathologies that make real booking email extraction hard.

A benchmark built from clean documents measures nothing, because clean documents
are not the job. Every pathology here is a distinct failure mode with a distinct
correct behaviour, and each one is tagged so failures can be reported by cause
rather than as a single accuracy number.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Pathology:
    key: str
    label: str
    what_it_tests: str
    correct_behaviour: str


PATHOLOGIES: tuple[Pathology, ...] = (
    Pathology(
        "clean",
        "Clean request",
        "Baseline. Everything stated once, unambiguously.",
        "Extract every stated field.",
    ),
    Pathology(
        "ambiguous_port",
        "Seaport / airport collision",
        "Whether the extractor resolves a city name to the right entity. "
        "Shanghai the seaport (CNSHA) and Shanghai Pudong the airport (CNPVG) "
        "are different locations that share a city name.",
        "Resolve using the transport mode as the disambiguating constraint: an "
        "air booking from 'Shanghai' means CNPVG, an ocean booking means CNSHA.",
    ),
    Pathology(
        "weight_conflict",
        "Body contradicts attachment",
        "Whether the extractor notices two different values for one field.",
        "Do not silently pick one. Flag the conflict; the correct extraction "
        "marks the field as contested rather than guessing.",
    ),
    Pathology(
        "unit_ambiguity",
        "Imperial units",
        "Whether weights in lbs are converted rather than copied as a number.",
        "Normalise to kilograms. A raw 2205 where 1000 kg was meant is wrong "
        "by a factor of 2.2, and it looks perfectly plausible.",
    ),
    Pathology(
        "date_ambiguity",
        "Ambiguous date format",
        "Whether 03/04/2026 is read as 3 April or 4 March.",
        "Use the sender's regional convention where it is inferable from other "
        "dates in the thread; otherwise mark ambiguous rather than guessing.",
    ),
    Pathology(
        "agent_not_shipper",
        "Sender is the agent",
        "Whether the extractor confuses the party sending the email with the "
        "party shipping the goods. The most common party error in practice.",
        "shipper_name is the party named in the body, not the sender's company.",
    ),
    Pathology(
        "multi_shipment",
        "Two bookings, one email",
        "Whether the extractor splits the request or blends the two shipments "
        "into one incorrect record.",
        "Emit two separate booking records.",
    ),
    Pathology(
        "forwarded_thread",
        "Stale values earlier in thread",
        "Whether the extractor takes the most recent value or the first one it "
        "encounters while reading top to bottom.",
        "The newest message wins. Earlier quoted values are superseded.",
    ),
    Pathology(
        "trailing_correction",
        "Correction at the end",
        "Whether a late 'ignore my previous, the weight is actually...' is applied.",
        "Apply the correction. The corrected value is the answer.",
    ),
    Pathology(
        "missing_critical",
        "Required field simply absent",
        "Whether the extractor abstains or invents. The single most important "
        "behaviour in the whole benchmark.",
        "Return null. A plausible invented incoterm is worse than an empty field, "
        "because a null routes to a human and a guess does not.",
    ),
    Pathology(
        "dg_undeclared",
        "Dangerous goods described but not declared",
        "Whether hazard is inferred from the commodity rather than from a checkbox. "
        "Lithium batteries are dangerous goods whether or not the sender says so.",
        "dangerous_goods is true, inferred from the commodity description.",
    ),
)

PATHOLOGIES_BY_KEY = {p.key: p for p in PATHOLOGIES}
