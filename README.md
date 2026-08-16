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
pass rate (all)        91.9%
pass rate (critical)   86.6%
hallucination rate      0.0%
```

Its 86.6% looks strong until you break it out by pathology. It scores **58% on multi-shipment**, because it always emits exactly one record per email. It never hallucinates only because it never guesses. That profile — flattering average, catastrophic on a specific failure mode — is exactly what a single accuracy number conceals, and it is the reason this benchmark reports by cause.

## Model results (v0.2 preview)

Three Claude tiers, run 2026-08-16 on the canonical corpus (seed 20260811, n=200, prompt v1 from [`freightbench/llm.py`](freightbench/llm.py)):

| System | Pass (all) | Pass (critical) | Wrong | Missed | Hallucination rate |
|---|---|---|---|---|---|
| empty | 53.9% | 15.1% | 0.0% | 46.1% | 0.0% |
| naive rules | 91.9% | 86.6% | 3.5% | 4.6% | 0.0% |
| Haiku 4.5 | 87.4% | 81.2% | 4.3% | 4.7% | 6.5% |
| Sonnet | 94.5% | 89.7% | 1.6% | 3.5% | 0.7% |
| Opus | 94.9% | 90.7% | 1.4% | 3.7% | 0.0% |

**Method, stated plainly:** these runs went through Claude Code subagents reading 20 documents per call, not through the raw API. Sampling parameters were not pinned. Treat them as a preview: directionally informative, not third-party reproducible. A raw-API harness with pinned parameters is the planned replacement, and the canonical prompt they must use ships in this repo (`python3 -m freightbench prompt`).

Three things the table hides that the pathology breakdown shows:

1. **The afternoon of regexes beats Haiku** on 10 of 11 pathologies. The exception is multi-shipment (naive 58%, Haiku 85%): recognising that one email contains two bookings is structural understanding, and it is the first place the LLM earns its keep.
2. **Hallucination separates the tiers: 6.5% → 0.7% → 0.0%.** Haiku's inventions are mostly booleans asserted from silence (`temperature_controlled: false` where the email says nothing) and country codes inferred from company legal suffixes. Both look harmless and both are exactly the confident-wrong output that costs money unattended.
3. **Naive still beats Sonnet and Opus on the rigid-template pathologies** (agent-not-shipper, weight-conflict, forwarded-thread: 96% vs ~90%). The v0.1 templates are regex-friendly, which flatters rules. That is a limitation of this corpus, not a finding about models, and it is the strongest argument for the realism work planned next.

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

Version 0.2. What exists: the generator, the schema, deterministic scoring, two reference extractors, a versioned canonical prompt, and preview results for three Claude tiers.

What changed since 0.1, because a benchmark should confess its own bugs: v0.1 ground truth carried values for ten fields that no template ever rendered into a document, which scored correct abstention as "missed" and deflated every extractor. v0.2 fixes the truth, adds the evidence invariant to the test suite, and regenerates the same documents byte-for-byte from the same seed. **No v0.1 number is comparable to the numbers above.**

What does not exist yet, and should be assumed missing rather than implied: raw-API model runs with pinned sampling (the table above is an agent-harness preview), non-Claude models, LLM-judged scoring for the free-text fields, and PDF and HAWB documents (currently email bodies only).

The synthetic corpus is a model of the problem, not a sample of it. It is built from the failure modes I have watched break production extraction pipelines, which is a real but partial view, and a system that scores well here has cleared a designed obstacle course rather than proven itself on live mail.

## Data

Entirely synthetic. Companies, references, lanes and commodities are invented. No real booking data appears in this repository.

## License

MIT
