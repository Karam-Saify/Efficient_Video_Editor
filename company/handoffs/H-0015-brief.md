# BRIEF H-0015 (Task C2': run EXP-008 rendering)
- **To:** engineering-lead
- **Tier / Milestone:** T2 / M0 (Task C; ROADMAP 0.7)
- **Date:** 2026-11-22

1. **Objective (with why):** Produce the EXP-008 caption images exactly as preregistered, so Creative can judge the declared Noto pair. This replaces the invalid EXP-006 run.
2. **Inputs (exact paths):** `company/experiments/EXP-008.md` (LOCKED; authoritative for every parameter, path, check and control); `company/positions/04-creative/ARABIC_QA.md`; DATA_RIGHTS RR-001, RR-011; your H-0013 probe notes (`company/handoffs/H-0013-return.md`); `experiments/exp006_render.py` (reuse what fits)
3. **Constraints:**
   - Follow EXP-008 §5 exactly: preconditions, coverage check before render, run-splitting rule, controls, log checks, file names, and output dir (as locked). The script lives at the path EXP-008 names (`experiments/exp008_render.py`).
   - The AR-01..AR-10 PNGs (1080×1920) are what Creative judges. Control renders are not judged and must be clearly separated or named as EXP-008 says.
   - Run the full procedure twice; outputs must be byte-identical (SHA256SUMS). Re-execution only as EXP-008 allows.
   - Do NOT view any PNG with the Read tool or send any image to an LLM: ffprobe, logs and hashes only. Do not judge.
   - Do not edit EXP-008.md (locked) or anything from EXP-006 (`render/frames_check/`, `experiments/exp006_render.py`).
   - The script must pass `ruff check .` (it sits in the repo); add a small unit test for the run-splitter if EXP-008 doesn't forbid it.
   - Forbidden data: `data/golden/`, `data/heldout/`, `quarantine/`. No commit/push.
4. **Output:** EXP-008 output dir as locked; return `company/handoffs/H-0015-return.md` with the rerun command, ffprobe output, coverage and control check output, and the log-check result.
5. **Done when:** [ ] all §5 preconditions pass · [ ] coverage check 0 missing for AR-01..10 · [ ] control(s) detected as specified · [ ] 10 PNGs 1080×1920 · [ ] two runs identical · [ ] ruff + pytest green · [ ] LOG entry
6. **Out of scope:** judging, fixing renderer defects, src/render changes.
7. **Effort budget:** max 40 tool calls · max 2 retries
8. **Escalate if:** any precondition or control fails; any undeclared font resolves for AR-01..10 (that is INVALID: stop, don't rerun with changes).
9. **Termination condition:** outputs + return written, or blocked; stop.
10. **Consulted positions:** Research (A): run matches prereg; Assurance: reproducibility in the C review.
