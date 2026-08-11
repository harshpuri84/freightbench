# FreightBench

An evaluation benchmark for agents that extract structured bookings from freight-forwarding emails.

Booking intake is the entry point of every forwarding operation, and it is a swamp: dozens of senders, no schema, values contradicted three paragraphs later, half of it exceptions. It is also the workflow AI vendors most want to sell into, and there is no public way to compare them. This is an attempt at one.

```bash
python3 -m freightbench generate --n 200 --out corpus.jsonl
python3 -m freightbench naive --corpus corpus.jsonl
```

Pure standard library. No API key, no network, no install.

## What makes it a benchmark rather than a test set

**Documents are generated, not collected.** Every corpus is reproducible from a seed, so a score that moves means the system changed and not the data. Real booking emails cannot be published anyway — they are somebody's commercial correspondence.

**Difficulty is named, not incidental.** Each document carries exactly one labelled pathology, so failures report by cause instead of collapsing into one accuracy number. `python3 -m freightbench pathologies` prints what each one tests and what correct behaviour looks like.

| Pathology | What it tests |
|---|---|
| `ambiguous_port` | Shanghai the seaport and Shanghai Pudong the airport are different entities sharing a city name. Mode is the disambiguating constraint |
| `weight_conflict` | Body and attachment state different weights. Correct behaviour is to flag it, not to quietly prefer one |
| `unit_ambiguity` | Weight given in lbs. Copying the number verbatim is wrong by a factor of 2.2 and looks entirely plausible |
| `date_ambiguity` | `03/04/2026`. A second date in the thread with a day above 12 proves the convention |
| `agent_not_shipper` | The sender is a forwarding agent. The shipper is named in the body |
| `multi_shipment` | Two bookings in one email that must not be merged |
| `forwarded_thread` | Superseded values quoted below the newest message |
| `trailing_correction` | "Apologies, the weight above is wrong" |
| `missing_critical` | A required field simply is not there |
| `dg_undeclared` | The sender says no dangerous goods declaration is needed. They are wrong: lithium batteries are UN3480 regardless of what the sender believes |

**A wrong value and a missing value are counted separately.** This is the central design decision. They have opposite operational consequences: a null routes the booking to a human, a confident wrong value goes straight through and surfaces when someone is invoiced for it. Any metric that averages them is hiding the expensive failure inside the cheap one. So there are five outcomes, not two:

| Outcome | Meaning |
|---|---|
| `correct` | Value present and right |
| `abstained_ok` | Field genuinely absent, extractor returned null. **This is a win** |
| `wrong` | Value present and incorrect |
| `missed` | Value was there, extractor returned null |
| `hallucinated` | Field was absent, extractor invented one |

The **hallucination rate** — of fields legitimately absent, the share invented anyway — is reported on its own, because it is the number that decides whether a system can be trusted to run unattended.

## Two reference points

An empty extractor that predicts nothing:

```
pass rate (all)        25.0%
pass rate (critical)    0.6%
```

That 25% is not noise. Abstaining on a genuinely absent field is correct behaviour, so any real system must clear this bar decisively before its headline number means anything. The critical-field figure is the honest one.

The bundled naive rule-based extractor, roughly what a competent engineer writes in an afternoon:

```
pass rate (all)        62.7%
pass rate (critical)   72.0%
hallucination rate      0.0%
```

Its 72% looks respectable until you break it out by pathology. It scores **39% on multi-shipment**, because it always emits exactly one record per email, and it fails unit conversion and trailing corrections outright. It never hallucinates only because it never guesses. That profile — passable average, catastrophic on specific failure modes — is exactly what a single accuracy number conceals, and it is the reason this benchmark reports by cause.

## Scoring rules worth knowing

- **Numeric tolerance is 0.5%.** Enough to absorb unit-conversion rounding, not enough to absorb unit confusion.
- **Company suffixes are ignored.** `Vantage Components BV` and `Vantage Components` are the same party; `Vantage Components` and `Vantage Holdings` are not.
- **Contested fields are excluded from the denominator.** When a document states two conflicting weights there is no assertable truth, and scoring it either way would reward guessing.
- **The headline is per-field, not per-document.** Document-level exact match cannot distinguish one systematic failure from thirty scattered ones.

## Evaluating your own system

Emit `{doc_id: [record, ...]}` keyed by document, one record per shipment, then:

```bash
python3 -m freightbench score --corpus corpus.jsonl --predictions yours.json
```

Field names and comparison rules are in [`freightbench/schema.py`](freightbench/schema.py) — 35 fields, each with its own criticality and comparison rule.

## Tests

```bash
python3 -m unittest discover -s tests
```

24 tests covering determinism, ground-truth correctness per pathology, and that the outcome categories stay distinct. A benchmark that is not tested is an opinion with a percentage sign attached.

## Status and honesty about scope

Version 0.1. What exists: the generator, the schema, deterministic scoring, and two reference extractors.

What does not exist yet, and should be assumed missing rather than implied: LLM-judged scoring for the free-text fields, PDF and HAWB documents (currently email bodies only), and any result for a frontier model — I have not published one, and no number here should be read as a model comparison.

The synthetic corpus is a model of the problem, not a sample of it. It is built from the failure modes I have watched break production extraction pipelines, which is a real but partial view, and a system that scores well here has cleared a designed obstacle course rather than proven itself on live mail.

## Data

Entirely synthetic. Companies, references, lanes and commodities are invented. No real booking data appears in this repository.

## License

MIT
