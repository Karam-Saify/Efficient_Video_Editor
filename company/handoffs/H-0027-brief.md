# BRIEF H-0027 (Week 1 · A)
- **To:** engineering-lead · **Tier / Milestone:** T2 (engine; covered by the one daily Assurance review, ADR-0006) / M1 · **Date:** 2026-11-23

1. **Objective (with why):** Measure what one exported video costs today, per stage, against the Founder's ceiling of $0.01 per free export (stretch $0.005, ADR-0011). We need the top 3 cost drivers before we design anything else.
2. **Inputs:** `company/decisions/ADR-0006..0013`; `src/demo/`, `src/ingest/`, `src/edit/`, `src/render/`; `quarantine/dev/*.mp4` + `dev_manifest.csv` (dev testing only); `company/handoffs/H-0025-return.md`, `H-0026-review.md`.
3. **Constraints:**
   - Build-mode rules (ADR-0006). CPU only. Never commit media or derived data.
   - Stages to cover: **ASR, understanding, planning, render, storage**.
     - Understanding and planning have no LLM yet. Estimate their tokens from realistic prompt sizes under ADR-0008 (a small model selects and fills a recipe; a big model is called only on a miss, so assume a miss rate and show how cost changes with it). Mark these rows as estimates.
     - Take current list prices from the `claude-api` skill (Haiku 5.5 small, Sonnet 5.5 / Opus 5.5 big). Do not guess them from memory.
   - Convert CPU time to dollars with a stated, sourced assumption (e.g. one cloud vCPU-hour price, cited). Also state the client-side alternative (on-device ASR/render, cost ≈ 0 to us).
   - Storage: bytes per stage (cache + output) × a stated $/GB-month and retention.
   - The instrumentation must be reusable: per-stage wall time, CPU time and peak RSS written into the stage manifest (or a `timings.json` in the cache). Add tests for it.
4. **Output:** `docs/COST_BASELINE.md`: method, assumptions table with sources, a per-clip × per-stage table, the median and P90 cost per exported video, the **top 3 cost drivers**, and 3 levers ranked by $ saved. Instrumentation code + tests are committed. Return at `company/handoffs/H-0027-return.md`.
5. **Done when:**
   - [ ] All **unique** dev clips are measured. There are 8, because `(2)` = `(4)`. The Founder asked for 10: report the shortfall and do not invent clips.
   - [ ] Every number in the doc traces to a measurement file or a cited assumption.
   - [ ] The ceiling verdict is stated: under / over $0.01 and $0.005, with the stage that breaks it.
   - [ ] Suite + ruff green.
6. **Out of scope:** optimising anything; the H-0026 F1–F8 fixes (queued for later); bench/ (task B); recipes (task C).
7. **Effort budget:** max 50 tool calls · 2 retries per failing action.
8. **Escalate if:** a price cannot be sourced; a full run of 8 clips would take more than 60 min of CPU (then sample and say so).
9. **Termination condition:** doc + code committed (do not push), return written.
10. **Consulted:** none. The daily Assurance review checks one row of the table.
