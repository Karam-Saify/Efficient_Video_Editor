# BRIEF H-0006 (Task C2: run EXP-006 rendering)
- **To:** engineering-lead
- **Tier / Milestone:** T2 / M0 (exit criterion 0.3)
- **Date:** 2026-11-22

1. **Objective (with why):** Produce the 10 caption test images exactly as preregistered in EXP-006, so Creative can judge whether our FFmpeg + libass path renders Arabic correctly before we build captions on top of it.
2. **Inputs (exact paths):**
   - `company/experiments/EXP-006.md` (LOCKED; follow its procedure and parameters exactly)
   - `company/positions/04-creative/ARABIC_QA.md` (strings)
   - `company/positions/05-assurance/DATA_RIGHTS.md` RR-001 (font must be recorded there before use)
   - `experiments/E6.md`, `src/render/` (existing libass path; `Encoding: -1`)
3. **Constraints (invariants, tools allowed/forbidden, budget):**
   - Write a small reproducible script (e.g. `experiments/exp006_render.py` or `src/render/frames_check.py`) that reads the strings from a data file and **not** from hand-copied literals in a shell command. Byte-exact strings matter: record each string's UTF-8 hex/codepoints in a log.
   - Output: `render/frames_check/AR-01.png … AR-10.png` at 1080×1920, plus the generated `.ass` files and a `render/frames_check/run_log.txt` (ffmpeg version, libass version if obtainable, font file path + sha256, command lines, codepoints per string).
   - **You must NOT view the PNGs with the Read tool or send any image to an LLM.** Only creative-lead views them. Verify with `ffprobe` (dimensions) and file size only.
   - Do not judge correctness yourself; that is Creative's job.
   - Any deviation from EXP-006 procedure is recorded under DEVIATIONS; do not edit EXP-006.md (it is locked).
   - Forbidden data: `data/golden/`, `data/heldout/`, `quarantine/`. No commit/push.
4. **Output (format + exact path):** files above; return in `company/handoffs/H-0006-return.md` with the exact rerun command.
5. **Done when:**
   - [ ] 10 PNGs, each 1080×1920 (ffprobe output pasted)
   - [ ] run_log.txt with versions, font hash, codepoints
   - [ ] Rerun command regenerates identical PNGs (compare sha256 of 2 runs)
   - [ ] Entry appended to `company/positions/03-engineering/LOG.md`
6. **Out of scope:** Fixing any rendering defect (that would be a new EXP after results); caption styling; video.
7. **Effort budget:** max 40 tool calls · max 2 retries per failing action
8. **Escalate if:** EXP-006 procedure can't be run as written with the installed ffmpeg/libass/font; RR-001 not recorded.
9. **Termination condition:** 10 PNGs + log exist and the return is written; stop without committing.
10. **Consulted positions (from RACI) and what they must confirm:** Research (A for EXP-006): run matches prereg; Assurance: reproducibility in the C review.
