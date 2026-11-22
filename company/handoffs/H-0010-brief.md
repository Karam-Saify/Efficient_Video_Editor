# BRIEF H-0010 (EXP-006 results as INVALID; draft EXP-007)
- **To:** research-lead
- **Tier / Milestone:** T2 / M0 (ROADMAP criterion 0.7)
- **Date:** 2026-11-22

1. **Objective (with why):** Close EXP-006 honestly as INVALID, and draft its successor EXP-007 testing a *declared* font pair, so our Arabic + Latin caption path is proven on the configuration we will actually ship (Lebanese Shorts mix in English words).
2. **Inputs (exact paths):**
   - `company/experiments/EXP-006.md` (LOCKED; reuse its structure), `company/handoffs/H-0006-return.md`, `company/handoffs/H-0006-ruling.md`, `render/frames_check/render.log`, `render/frames_check/SHA256SUMS`
   - `company/positions/04-creative/ARABIC_QA.md` (the same 10 strings, verbatim)
   - `company/positions/05-assurance/DATA_RIGHTS.md` RR-001 (Noto Sans Arabic), RR-011 (Noto Sans)
   - Founder decision 2026-11-22 (delegated to the Operator): **font stack = Noto Sans Arabic (Arabic script) + Noto Sans (Latin, digits, ASCII/general punctuation), declared explicitly**
3. **Constraints (invariants, tools allowed/forbidden, budget):**
   - Write `company/experiments/EXP-006-results.md`: verdict **INVALID** (no PASS/FAIL), the reason, the deviations (script edit after run 2, missed fallback detection), the evidence hashes, and a pointer to EXP-007. No PNG has been judged, so say so.
   - Draft `company/experiments/EXP-007.md` with `**Lock:** DRAFT` (NOT locked). It must include: the declared font pair and how fonts are assigned per run (e.g. code splits each string into script runs and wraps non-Arabic runs in an ASS `{\fnNoto Sans}` override, with the run-splitting rule specified exactly, including how neutral characters such as spaces, digits, brackets and the en dash are assigned); a **pre-render coverage check** in code (every code point is covered by its assigned font file, otherwise INVALID); and log-check validation using a **known-fallback control** (one deliberately uncovered character, rendered separately and not judged, must be detected by the check). Keep the Founder pass rule: PASS = 10/10 correct and no Sev-1. Keep the §6 "correct" definition from EXP-006 unless Creative objects.
   - Add a section "Consultation before lock" with two empty sign-off lines: Engineering (feasibility with ffmpeg 6.1.1/libass 0.17.1) and Creative (judging and "correct" definition). Locking happens only after both sign.
   - No rendering, no images, no code. Do not edit EXP-006.md.
4. **Output (format + exact path):** the two files above; return in `company/handoffs/H-0010-return.md`.
5. **Done when:**
   - [ ] EXP-006-results.md records INVALID with evidence
   - [ ] EXP-007.md drafted (DRAFT), with font pair, run-splitting rule, coverage check, fallback control, pass rule, deviations policy and consultation block
   - [ ] LOG.md entry
6. **Out of scope:** Locking EXP-007 (later, after consultation), EXP-001, the Trend & Technique work.
7. **Effort budget:** max 30 tool calls · max 2 retries per failing action
8. **Escalate if:** ASS/libass can't express per-run font assignment, in your reading; then propose an alternative and stop.
9. **Termination condition:** both files and the return written; stop. No commit.
10. **Consulted positions (from RACI) and what they must confirm:** Engineering (feasibility) and Creative (quality metric) sign the EXP-007 consultation block in the next step; Assurance checks the lock in the C review.
