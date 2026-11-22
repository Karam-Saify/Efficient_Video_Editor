# STATE: single source of truth
<!-- The Operator updates this at the end of every session (/close). Keep it under 60 lines.
     If a HALT line exists at the very top, ALL work stops until the Founder clears it. -->

**Last updated:** 2026-11-22 · **By:** Operator · **Session:** 1

## Current milestone
**M0: Foundation** · started 2026-11-21 · gate target: when exit criteria in ROADMAP.md are met

## Now (in progress)
| ID | Task | Tier | Owner | Status | Handoff |
|---|---|---|---|---|---|
| — | Install Company OS into repo (CLAUDE.md + .gitignore merged; hook self-test 7/7) | T2 | Operator | done, uncommitted; ADR-0001 awaits Founder signature | `company/gates/M0/hook-test.txt` |
| H-0001 | Golden-set intake profile of 4 Founder clips | T1 | Operator→Creative | PARTIAL: no rights | `company/handoffs/H-0001-return.md` |

## Next (ordered)
1. M0 pre-mortem: all five positions → `company/gates/M0/premortem.md`
2. Founder fills "Source footage" in root CLAUDE.md
3. Creative: draft golden-set spec + data-rights intake (no footage yet)
4. Research: preregister EXP-001 (Arabic ASR) and EXP-006 (Arabic caption rendering)
5. Engineering: repo skeleton + `schemas/timeline.schema.json` v0 + CI running tests

## Blockers
- Golden set (M0 0.4): the 4 supplied clips are third-party finished TikToks with no rights record (I-9); need raw 2–10 min sources with rights

## Open decisions (awaiting Founder)
- Rights/proof for the 4 clips in data/golden/ (H-0001 Q1)
- Sign ADR-0001

## Last gate
- None yet

## Key numbers (from METRICS.md)
| Metric | Value | Target |
|---|---|---|
| Tokens per Short (end-to-end) | not measured | set at M3 |
| Golden-set rubric score | not measured | set at M0 |
