# BRIEF H-0036 (pilot · Common Voice Arabic baseline)
- **To:** research-lead · **Tier / Milestone:** T2 (an experiment) / pilot day 1–2 · **Date:** 2026-11-23

1. **Objective (with why):** Establish a public, CC0 Arabic ASR baseline for our local stack (ADR-0023 item 4). This gives a number to beat that does not depend on third-party TikTok clips or on our own wrong labels (ADR-0022).
2. **Inputs:** `company/handoffs/H-0034-return.md` (Common Voice licence/access verdict); `company/experiments/EXP-001.md` (normalisation, 9 steps, reuse it); `company/templates/EXPERIMENT.md` (§0 decision brief, ADR-0012); `src/ingest/__main__.py` (faster-whisper config).
3. **Constraints:**
   - Run only if H-0034 marks Common Voice Arabic as usable **and** it is downloadable without the Founder's personal account. If it needs an account or terms acceptance, STOP: BLOCKED, with the exact steps the Founder must take.
   - Zero cost, CPU only. Sample size sized for CPU: e.g. 200 test utterances of the Arabic test split, seed fixed. Justify n.
   - Configs: large-v3-turbo with auto language vs forced `ar`. Add large-v3 only if the download and runtime fit (say so).
   - Metrics: WER and CER after EXP-001 normalisation, language-ID accuracy under auto, RTF. Data stays in `cache/` or `quarantine/`. Commit no audio, and no transcripts beyond 3 example lines.
   - Preregister as EXP-013 (EXP-012 is reserved for the Founder's clip diagnostic). Lock before running.
4. **Output:** `company/experiments/EXP-013.md` (LOCKED) + `EXP-013-results.md` + the script in `experiments/`. Return at `company/handoffs/H-0036-return.md`.
5. **Done when:**
   - [ ] EXP-013 is locked before the run (commit order proves it).
   - [ ] Results table per config: WER, CER, LID accuracy, RTF, n, with a 95 % CI (bootstrap).
   - [ ] An evidence level is assigned.
6. **Out of scope:** SHAMS, ASC, TimelineBench runs (licence-gated); fixing the pipeline.
7. **Effort budget:** max 40 tool calls · 2 retries.
8. **Escalate if:** the access terms forbid our use; the CPU run would exceed 90 min.
9. **Termination condition:** results committed, or BLOCKED with Founder steps. Commit each finished file (~every 5 min), but do not push.
10. **Consulted:** engineering-lead (only if the ASR harness needs changes; if so, list them instead of making them).
