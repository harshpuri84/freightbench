# FreightBench v0.2 results — run 2026-08-16

Corpus: seed 20260811, n=200. The corpus itself is not committed because it is
byte-reproducible from the seed. Regenerate it, then verify any number below:

    python3 -m freightbench generate --n 200 --seed 20260811 --out corpus.jsonl
    python3 -m freightbench score --corpus corpus.jsonl \
        --predictions research/model-run-2026-08-16/predictions-opus-v2.json

`predictions-*.json` are prompt v1 (superseded); `predictions-*-v2.json` are
prompt v2 and are the ones the README table reports.

| System | Pass (all) | Pass (critical) | Wrong | Missed | Hallucination rate |
|---|---|---|---|---|---|
| empty | 53.9% | 15.1% | 0.0% | 46.1% | 0.0% |
| naive rules | 92.7% | 88.6% | 2.7% | 4.6% | 0.0% |
| Haiku 4.5 | 91.5% | 85.3% | 3.9% | 2.3% | 4.4% |
| Sonnet | 99.9% | 100.0% | 0.0% | 0.0% | 0.2% |
| Opus | 100.0% | 99.9% | 0.0% | 0.0% | 0.0% |

Per-pathology critical-field pass rate:

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
