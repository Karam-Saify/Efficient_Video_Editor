# Company Scorecard
Owner: Assurance (A) for integrity; each metric has an owner who produces it.
"Leading" metrics predict success, "lagging" metrics confirm it. Targets are set at the milestone
listed and are changed only by ADR.

## Product metrics
| Metric | Type | Owner | How measured | Target set at | Target | Current |
|---|---|---|---|---|---|---|
| Golden-set rubric score (mean, 1–5) | Lagging | Creative | `RUBRIC.md` applied blind to outputs | M0 | ≥ M2 baseline + prereg delta | — |
| Exact-duration hit rate | Lagging | Engineering | output duration == target ±1 frame | M2 | 100% | — |
| Timeline validity first try | Leading | Engineering | validator pass rate | M4 | ≥ 90% | — |
| ASR WER on golden set | Leading | Research | EXP-001 script | M1 | prereg | — |
| Arabic caption defect rate | Lagging | Creative | defects / caption lines checked | M1 | 0 Sev-1 | — |
| Time from raw video to approved Short (Founder) | Lagging | Product | stopwatch log | M4 | prereg | — |
| Audience retention vs channel baseline | Lagging | Product | YouTube Studio | M5 | ≥ baseline | — |

## Cost metrics
| Metric | Owner | How measured | Target set at | Target |
|---|---|---|---|---|
| Tokens per Short (end-to-end) | Engineering | `cache/<id>/usage.jsonl` summed | M3 | budget TBD by Product |
| Tokens per revision (median) | Engineering | same | M4 | < 2,000 |
| Render minutes per Short | Engineering | timing log | M2 | < 5 min |
| Codespace core-hours per week | Engineering | GitHub billing page | M1 | within free quota |
| **Cost per successful export** (incl. retries + failures, ADR-0015) | Engineering (Product owns target) | `src/cost` ledger: total $ ÷ successful exports | Week 1 baseline (`docs/COST_BASELINE.md`) | ≤ $0.01, stretch ≤ $0.005 |
| **Quality ÷ cost** (ADR-0015) | Product | golden rubric mean ÷ cost per successful export | M2 | higher than the previous release |

## Operating-health metrics (is the company OS working?)
| Metric | Owner | Healthy | Warning |
|---|---|---|---|
| Sessions closed with push | Operator | 100% | any miss |
| T2 items with Assurance verdict before merge | Assurance | 100% | any miss |
| Briefs with all 10 fields | Assurance (sample) | 100% | < 90% |
| Returns with STATUS PARTIAL/BLOCKED/ESCALATE (honesty signal) | Assurance | 10–30% | 0% (suspicious) or > 50% (briefs too big) |
| Escaped defects (found after a GO) | Assurance | 0 Sev-1 | any Sev-1 |
| Scope changes per milestone | Product | ≤ 2 | > 2 |
| Dissent predictions checked at gate | Assurance | 100% | any skipped |
