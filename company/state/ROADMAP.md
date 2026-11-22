# Roadmap: Milestones, Exit Criteria and Kill Criteria
Owner: Product (A). Changing this file's milestone definitions is a T3 change.
Each exit criterion must get an **evidence path** before the gate opens.

---

## M0: Foundation
**Goal:** The company can operate safely: OS installed, data and quality definitions exist, first experiments preregistered.

| # | Exit criterion | Owner | Evidence path |
|---|---|---|---|
| 0.1 | Company OS installed; hooks tested (protected file edit is blocked) | Engineering | `company/gates/M0/hook-test.txt` |
| 0.2 | Repo skeleton, CI runs tests on push, green | Engineering | CI run link / `ci-log.txt` |
| 0.3 | `schemas/timeline.schema.json` v0 + validator + 5 valid and 5 invalid fixture files pass/fail correctly | Engineering | `tests/fixtures/` + test output |
| 0.4 | Golden set: 5 source videos with rights recorded, metadata filled | Creative | `data/golden/MANIFEST.md` |
| 0.5 | Held-out set: 3 source videos, sealed, access log started | Assurance | `data/heldout/ACCESS_LOG.md` |
| 0.6 | Quality rubric v1 + 1 calibration round (Founder + Creative rate 3 reference Shorts; agreement computed) | Creative | `company/positions/04-creative/RUBRIC.md` + `calibration-001.csv` |
| 0.7 | EXP-001 and EXP-006 preregistered and LOCKED | Research | `company/experiments/EXP-001.md`, `EXP-006.md` |
| 0.8 | Risk register with ≥ 12 risks scored, each with an owner | Assurance | `company/state/RISK_REGISTER.md` |
| 0.9 | Target user v0 + problem statement (PR/FAQ draft) | Product | `company/positions/01-product/PRFAQ.md` |

**Kill criteria:** none (foundation). **Pivot trigger:** the Founder cannot obtain 5 usable source videos with clear rights → redefine the input domain.

---

## M1: Feasibility of the risky parts (Arabic in, Arabic out)
| # | Exit criterion | Threshold (set in prereg) |
|---|---|---|
| 1.1 | EXP-001 Arabic ASR run on golden set; WER and timestamp drift measured | Preregistered |
| 1.2 | EXP-006 Arabic captions render with correct shaping and RTL in ≥ 1 renderer | 100% of test strings visually correct (Creative check) |
| 1.3 | Ingest stage: video → transcript.json + scenes.json, cached, deterministic (same hash twice) | 2 identical runs |
| 1.4 | ADR: ASR choice; ADR: renderer choice | Accepted |

**Kill criterion:** no ASR option reaches the preregistered WER on dialect content AND no workaround (manual transcript import) is acceptable to the Founder → narrow to MSA or to non-speech content.

## M2: Walking skeleton (no LLM)
| # | Exit criterion |
|---|---|
| 2.1 | Transcript → MILP selection → timeline.json → render, end-to-end on all golden videos |
| 2.2 | Output duration exactly equals target (±1 frame) for 30/45/58 s on every golden video |
| 2.3 | Full run reproducible from clean checkout by Assurance using one command |
| 2.4 | Baseline rubric score recorded (this is the bar M3 must beat) |
| 2.5 | Runtime and cost per Short recorded in METRICS.md |

**Kill criterion:** a render of a 60 s Short takes > 15 min on the target machine with no feasible optimisation path.

## M3: Intelligence (LLM scoring + rule object)
| # | Exit criterion |
|---|---|
| 3.1 | EXP-002 (are visual captions needed?) concluded |
| 3.2 | EXP-004 LLM-scored selection beats M2 baseline on golden set rubric (preregistered effect size) |
| 3.3 | Same result replicated on held-out set (E3) |
| 3.4 | EXP-005 cost per Short within budget set in METRICS.md |

**Kill criterion:** LLM scoring does not beat the no-LLM baseline on held-out → the LLM adds no value at this stage; rethink the approach.

## M4: Editing loop (natural-language revisions)
| # | Exit criterion |
|---|---|
| 4.1 | EXP-003 ≥ 90% valid timeline JSON first try; rest fixed within 1 retry |
| 4.2 | EXP-007 median revision < 2k tokens, diffs small |
| 4.3 | Captions, zoom and overlay expressible in schema and render correctly in Arabic |
| 4.4 | Founder completes 5 real edit sessions; time to final < preregistered target |

## M5: Pilot (real audience)
| # | Exit criterion |
|---|---|
| 5.1 | 10 Shorts published on the Founder's channel, AI-use disclosed per platform rules |
| 5.2 | Retention / views compared to the channel's previous 10 Shorts (E4) |
| 5.3 | Real cost per Short and editing time logged |

**Kill criterion:** audience metrics are significantly worse than the manual baseline after 10 Shorts AND the Creative rubric does not predict audience metrics → the quality model is wrong; return to M3.

## M6: Company readiness
| # | Exit criterion |
|---|---|
| 6.1 | Target customer and willingness-to-pay evidence (≥ 10 creator interviews) |
| 6.2 | Unit economics: cost per Short vs price hypothesis, with margin |
| 6.3 | Productisation decision: tool, service, or API (ADR, one-way door) |
| 6.4 | Legal: licenses of all dependencies compatible with commercial use |
