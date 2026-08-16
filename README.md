# FreightBench

[![tests](https://github.com/harshpuri84/freightbench/actions/workflows/tests.yml/badge.svg)](https://github.com/harshpuri84/freightbench/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

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
pass rate (all)        53.9%
pass rate (critical)   15.1%
```

That floor is high on purpose and it is not noise. A null is the correct answer for every field the document does not state, and most fields in a real booking email are not stated. Any real system must clear this bar decisively before its headline number means anything. The critical-field figure is the honest one.

The bundled naive rule-based extractor, roughly what a competent engineer writes in an afternoon:

```
pass rate (all)        92.7%
pass rate (critical)   88.6%
hallucination rate      0.0%
```

Its 88.6% looks strong until you break it out by pathology. It scores **59% on multi-shipment**, because it always emits exactly one record per email. Its zero hallucination rate is not restraint either: it does guess, unconditionally answering `dangerous_goods` as false whenever the email does not say otherwise, which is right 57.3% of the time for free. That field can never be scored as a hallucination because its truth is never null, so the guess is invisible in the headline. That profile — flattering average, catastrophic on one failure mode, and a free ride on another — is exactly what a single accuracy number conceals, and it is the reason this benchmark reports by cause.

## Model results: the corpus is saturated

Three Claude tiers, run 2026-08-16 on the canonical corpus (seed 20260811, n=200, prompt v2 from [`freightbench/llm.py`](freightbench/llm.py)):

| System | Pass (all) | Pass (critical) | Wrong | Missed | Hallucination rate |
|---|---|---|---|---|---|
| empty | 53.9% | 15.1% | 0.0% | 46.1% | 0.0% |
| naive rules | 92.7% | 88.6% | 2.7% | 4.6% | 0.0% |
| Haiku 4.5 | 91.5% | 85.3% | 3.9% | 2.3% | 4.4% |
| Sonnet | 99.9% | 100.0% | 0.0% | 0.0% | 0.2% |
| Opus | 100.0% | 99.9% | 0.0% | 0.0% | 0.0% |

**The headline is not a ranking, it is a ceiling.** Sonnet and Opus both solve this corpus. Sonnet scores 100% on every one of the eleven pathologies; Opus misses two `pieces` values on multi-shipment documents and nothing else, zero wrong answers in 7,576 fields. Eleven named difficulty knobs producing one identical score is the definition of a benchmark that has stopped measuring anything at the top.

Per-pathology, critical fields:

| Pathology | naive rules | Haiku 4.5 | Sonnet | Opus |
|---|---|---|---|---|
| agent_not_shipper | 98% | 86% | 100% | 100% |
| ambiguous_port | 95% | 85% | 100% | 100% |
| clean | 95% | 86% | 100% | 100% |
| date_ambiguity | 90% | 86% | 100% | 100% |
| dg_undeclared | 93% | 87% | 100% | 100% |
| forwarded_thread | 99% | 82% | 100% | 99% |
| missing_critical | 98% | 84% | 100% | 100% |
| multi_shipment | 59% | 88% | 100% | 100% |
| trailing_correction | 90% | 82% | 100% | 100% |
| unit_ambiguity | 90% | 84% | 100% | 100% |
| weight_conflict | 98% | 85% | 100% | 100% |

What still holds:

1. **Haiku is the only model this corpus can grade,** and the interesting number is its 4.4% hallucination rate, not its 85.3% pass rate. Its inventions are booleans asserted from silence (`temperature_controlled: false` where the email says nothing) and country codes inferred from company legal suffixes. Both look harmless; both are the confident-wrong output that costs money when nobody is checking.
2. **An afternoon of regexes beats Haiku overall** (88.6% against 85.3% on critical fields) and loses catastrophically on one thing: multi-shipment, 59% against 88%. Recognising that one email contains two bookings is structural understanding, and it is where a language model first earns its keep.
3. **Do not read Sonnet against Opus.** Two independent Sonnet runs over the same 200 documents differ by 0.6 points on critical fields, with 99.1% field-level agreement. Any gap smaller than that is noise, and the gap here is smaller than that.

Every prediction behind these numbers is committed under [`research/model-run-2026-08-16/`](research/model-run-2026-08-16/), so any figure in the table can be re-derived without re-running a model. The corpus is not committed because it is byte-reproducible from its seed.

**Method, stated plainly.** These runs went through agent subagents reading 20 documents per call, not the raw API, and sampling parameters were not pinned. Later runs were given an explicit instruction not to read this repository, after one agent disclosed that it had read the generator's reference tables — the answer key — and its batch was discarded and re-run. Treat these numbers as directional and not third-party reproducible. A pinned raw-API harness is the planned replacement; it cannot read the repository at all, which is now a second reason to build it.

### What v0.1 got wrong

Every model failure this benchmark originally reported was a benchmark defect. Four of them, in the order they surfaced:

| Defect | Effect |
|---|---|
| Ten truth fields that no template ever rendered | Correct abstention scored as `missed` |
| Prompt said "do not guess" while truth required derivation | `dangerous_goods` scored missed on 200 of 218 records |
| The naive extractor guesses `dangerous_goods` unconditionally | A free 57.3% on a critical field, invisible in its hallucination rate |
| Air LOCODEs pointing at other cities' airports | 100% of the frontier models' remaining errors |

The last one is the subtlest and worth spelling out. Mapping Rotterdam to Amsterdam Schiphol, Busan to Incheon, Felixstowe to Heathrow and Santos to Guarulhos is not a name collision, it is a routing decision about which airport serves a port city, and forwarders resolve it differently. Only Shanghai was ever a genuine `CNSHA` versus `CNPVG` split. Asserting the rest as truth punished extractors for correctly reading the place the document named.

Each fix preserves the random-number stream, so the same seed still regenerates byte-identical documents and predictions collected against the old ground truth rescore without re-running anything.

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

Field names and comparison rules are in [`freightbench/schema.py`](freightbench/schema.py) — 35 fields, each with its own criticality and comparison rule. If you are scoring an LLM, use the canonical prompt (`python3 -m freightbench prompt`); two systems scored with different prompts are not comparable, so the prompt is versioned and part of the benchmark definition.

## Tests

```bash
python3 -m unittest discover -s tests
```

38 tests covering determinism, ground-truth correctness per pathology, that the outcome categories stay distinct, and one invariant learned the hard way: **every non-null truth value must be evidenced in the document**. A benchmark that is not tested is an opinion with a percentage sign attached.

## Status and honesty about scope

Version 0.2, and the honest summary is that **this corpus is solved.** Any current frontier model clears it completely. It still separates a small model from a large one, and it still measures hallucination usefully, but it cannot tell a very good extraction system from a perfect one. Until the corpus gets harder, a high score here means the obstacle course was designed too easy, not that a system is ready for live mail.

What exists: the generator, the schema, deterministic scoring, two reference extractors, a versioned canonical prompt, and full results for three Claude tiers.

**No v0.1 number is comparable to anything above.** Four ground-truth and prompt defects were fixed between them, documented in the results section, because a benchmark that hides its own bugs is worth less than one that publishes them.

What does not exist yet, and should be assumed missing rather than implied: raw-API model runs with pinned sampling, non-Claude models, LLM-judged scoring for the free-text fields, and PDF and HAWB documents (currently email bodies only).

The v0.3 work is therefore not a polish pass. Document texture is uniform enough that a regex extractor beats a small model on nine of eleven pathologies, and the pathologies themselves are too easy to separate the top two tiers at all. Both have to change before another model number is worth publishing.

The synthetic corpus is a model of the problem, not a sample of it. It is built from the failure modes I have watched break production extraction pipelines, which is a real but partial view, and a system that scores well here has cleared a designed obstacle course rather than proven itself on live mail.

## Data

Entirely synthetic. Companies, references, lanes and commodities are invented. No real booking data appears in this repository.

## License

MIT
