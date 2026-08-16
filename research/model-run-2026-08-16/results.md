| System | Pass (all) | Pass (critical) | Wrong | Missed | Hallucination rate |
|---|---|---|---|---|---|
| empty | 53.9% | 15.1% | 0.0% | 46.1% | 0.0% |
| naive | 91.9% | 86.6% | 3.5% | 4.6% | 0.0% |
| haiku | 87.4% | 81.2% | 4.3% | 4.7% | 6.5% |
| sonnet | 94.5% | 89.7% | 1.6% | 3.5% | 0.7% |
| opus | 94.9% | 90.7% | 1.4% | 3.7% | 0.0% |

Per-pathology critical-field pass rate:
| Pathology | naive | haiku | sonnet | opus |
|---|---|---|---|---|
| agent_not_shipper | 96% | 81% | 90% | 91% |
| ambiguous_port | 94% | 82% | 89% | 91% |
| clean | 92% | 82% | 89% | 89% |
| date_ambiguity | 89% | 81% | 90% | 91% |
| dg_undeclared | 91% | 80% | 90% | 91% |
| forwarded_thread | 96% | 78% | 89% | 90% |
| missing_critical | 94% | 82% | 89% | 90% |
| multi_shipment | 58% | 85% | 89% | 91% |
| trailing_correction | 87% | 77% | 91% | 90% |
| unit_ambiguity | 89% | 80% | 92% | 92% |
| weight_conflict | 96% | 81% | 90% | 91% |
