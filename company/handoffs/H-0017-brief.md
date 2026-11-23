# BRIEF H-0017 (close H-0009 review N1 and N2)
- **To:** engineering-lead
- **Tier / Milestone:** T2 / M0
- **Date:** 2026-11-22

1. **Objective (with why):** Remove the last Task B merge blocker (N1) and give the new `has_audio` schema field its ADR (N2), so the schema change is recorded and the validator never crashes on hostile input.
2. **Inputs:** `company/handoffs/H-0009-review.md` (N1–N5), `src/validate/`, `schemas/timeline.schema.json`, `company/positions/03-engineering/ARCHITECTURE.md`, `company/decisions/INDEX.md`
3. **Constraints:** N1: a NUL byte (or any other path that makes `os`/`pathlib` raise) in `sources[].path` must yield a coded error (`E_SOURCE_PATH`), never an exception. Add a regression test, and a small fuzz-style test over odd path strings. N2: write `company/decisions/ADR-0004-source-has-audio.md` (Proposed; Assurance and Creative are named as consulted) and correct ARCHITECTURE.md so it does not claim ingest fills `has_audio` yet (say "to be filled by ingest from ffprobe: next ingest brief"). Other N-items: answer FIX/DEFER/WONTFIX in the return. Don't touch EXP-006/EXP-008 outputs or `company/experiments/`. Never view images. No commit.
4. **Output:** code + ADR in the working tree; return `company/handoffs/H-0017-return.md` with pasted ruff + pytest output.
5. **Done when:** [ ] N1 fixed with a test that failed before · [ ] ADR-0004 + INDEX · [ ] ARCHITECTURE wording corrected · [ ] ruff + pytest green · [ ] LOG entry
6. **Out of scope:** implementing ingest's ffprobe fill; other deferred items.
7. **Effort budget:** max 20 tool calls · max 2 retries
8. **Escalate if:** the fix needs a schema change.
9. **Termination condition:** return written; stop.
10. **Consulted positions:** Assurance verifies N1 closed (spot re-check); Creative informed of ADR-0004.
