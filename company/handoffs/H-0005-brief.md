# BRIEF H-0005 (Task C1: preregister EXP-006)
- **To:** research-lead
- **Tier / Milestone:** T2 / M0 (exit criterion 0.3)
- **Date:** 2026-11-22

1. **Objective (with why):** Preregister and LOCK EXP-006, "Can our FFmpeg + libass path render Arabic captions correctly?", before any rendering happens. Fixing the pass rule in advance stops us from moving the goalposts after seeing the images (Constitution I-5).
2. **Inputs (exact paths):**
   - `company/positions/04-creative/ARABIC_QA.md` (severity scale + the 10 test strings AR-01..AR-10, used verbatim)
   - `company/positions/02-research/PLAYBOOK.md` (SOP-R2/R3 preregistration procedure), `company/experiments/README.md`, any prereg template in `company/templates/`
   - Prior exploratory note: `experiments/E6.md` (exploratory only, not gate evidence; ASS `Encoding: -1` finding)
3. **Constraints (invariants, tools allowed/forbidden, budget):**
   - **Pass rule (Founder-fixed, do not change):** PASS = 10/10 strings judged correct by creative-lead AND zero Sev-1 defects. Anything else = FAIL.
   - Procedure to preregister: render each string as a single caption on a plain neutral 1080×1920 frame with FFmpeg + libass, font Noto Sans Arabic (license per DATA_RIGHTS RR-001), output `render/frames_check/AR-01.png … AR-10.png` (repo root), plus the exact `.ass` files and command used. Judge: creative-lead, inspects each PNG at 200% for shaping, RTL order, digits, Latin words, lam-alef, diacritics, brackets/quotes mirroring, tatweel. Record per string pass/fail + severity.
   - Specify the fixed render parameters (font, size, colours, alignment, `Encoding`, ffmpeg version capture), what counts as a deviation, and what happens on FAIL (new EXP id, no edits to this one).
   - The file must contain the line `**Lock:** LOCKED` (with date) when finished. Once it does, the hook will block further edits, so get it right before you lock it.
   - No rendering, no code, no media. Do not use `data/golden/`, `data/heldout/`, `quarantine/`.
4. **Output (format + exact path):** `company/experiments/EXP-006.md` (LOCKED). Return in `company/handoffs/H-0005-return.md`.
5. **Done when:**
   - [ ] EXP-006.md has hypothesis, the 10 strings verbatim with IDs, procedure, fixed parameters, judge, metric, pass rule, deviations policy, results path `company/experiments/EXP-006-results.md`
   - [ ] `**Lock:** LOCKED · 2026-11-22` present
   - [ ] Entry appended to `company/positions/02-research/LOG.md`
6. **Out of scope:** Rendering (H-0006), judging (H-0007), EXP-001, literature review.
7. **Effort budget:** max 25 tool calls · max 2 retries per failing action
8. **Escalate if:** The Founder pass rule seems untestable as stated, or ARABIC_QA strings look malformed (e.g. invisible characters); report, don't fix.
9. **Termination condition:** EXP-006.md is LOCKED, the return file is written; stop. Do not commit.
10. **Consulted positions (from RACI) and what they must confirm:** Engineering (RACI 8 C: feasibility). The procedure must match what H-0006 can run with the installed ffmpeg 6.1.1 + libass. Creative (C: quality metric) must agree the judging matches ARABIC_QA.md. Assurance (C: lock) checks the lock in the C review.
