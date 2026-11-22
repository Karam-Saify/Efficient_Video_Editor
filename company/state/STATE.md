# STATE: single source of truth
<!-- The Operator updates this at the end of every session (/close). Keep it under 60 lines.
     If a HALT line exists at the very top, ALL work stops until the Founder clears it. -->

**Last updated:** 2026-11-22 · **By:** Operator · **Session:** 2 (checkpoint, not yet /close)

## Current milestone
**M0: Foundation** · started 2026-11-21 · Phase 3 of the Founder plan; next stop is STOP POINT 3. Daily report: `company/reports/2026-11-22/README.md`

## Now (in progress at checkpoint; if the session died, check these files exist)
| ID | Task | Tier | Owner | Status | Handoff |
|---|---|---|---|---|---|
| H-0023 | Assurance review of Task C (EXP-006/008) + N1 spot check | T2 | assurance | running | `H-0023-review.md` |
| H-0020 | Close hook gaps (shell writes, false positives) | T2 | engineering | running → then Assurance review | `H-0020-return.md` |
| H-0022 | EXP-001 draft (DO NOT LOCK until footage), A-11 refuted, EXP-010 registered | T1 | research | running | `H-0022-return.md` |

## Done this session (all reviewed where T2)
- Phase 1–2: Company OS installed, live hook test 4/4 (M0 0.1 ✅)
- Task A skeleton + CI 3.12/3.14 (0.2 ✅) · Task B schema v0 + validator, N1 fixed `890f225` (0.3 ✅ after the H-0023 spot check)
- EXP-006 INVALID (undeclared font fallback) → EXP-008 LOCKED, rendered, **FAIL 8/10, 0 Sev-1, E2** (Latin/digits ~1.6× alef height vs 1.3× limit; Arabic passed)
- ADR-0002 Python 3.12 (Accepted) · ADR-0003, ADR-0004 (Proposed) · ADR-0005 fast lane (Accepted, Founder)
- Rights: 4 clips + zip UNVERIFIED/not usable (RR-006..010); fonts RR-001, RR-011; trend sources RR-012..017 pending
- Risk register: 25 risks re-scored (0.8 ✅) · PR/FAQ v0 chat-editor MVP (0.9 drafted)

## Next (ordered, Founder-set)
1. Finish H-0023 + the H-0020 review → **STOP POINT 3** (Assurance verdicts A/B/C, PNGs, result table)
2. Founder checks EXP-008 AR-02/05/07/08 (counts with Creative's verdict) and sets the Latin size ratio limits for EXP-010
3. Phase 4: `/close`, then a PR `t2/install-company-os` → `main`
4. MVP pivot (T3), with the Founder's pivot prompt **(Operator does not have it; ask)**; next free ADR = ADR-0006
5. Trend & Technique T2 (Founder-approved) only after the pivot and after Assurance clears RR-012..017
6. Fast-lane batch: CI secret scan (R-15 claims one that doesn't exist)

## Blockers
- No usable footage (R-21): blocks M0 0.4, 0.5 and EXP-001 lock. Founder must supply raw Arabic sources with rights.
- Origin of the 4 Download*.mp4 clips and the quarantined zip: Founder to confirm.

## Open decisions (awaiting Founder)
- EXP-008 co-verdict; EXP-010 size limits · PR/FAQ Q: chat editor on top of M1–M3, or replacing M2–M3 (T3)? · Sign ADR-0001

## Last gate
- None yet

## Key numbers
| Metric | Value | Target |
|---|---|---|
| Tests | 155 pass, 8 skip; CI green | green |
| M0 exit criteria | ~4.5 of 9 | 9 |
| Tokens per Short | not measured | set at M3 |
