# BRIEF H-0026
- **To:** assurance-lead
- **Tier / Milestone:** T2 review (the ONE daily engine review, ADR-0006) / M0→M1 build mode
- **Date:** 2026-11-23

1. **Objective (with why):** Decide whether today's engine work can be trusted. This is the single daily review of `src/`, done on the end-to-end demo (ADR-0006) and not per task.
2. **Inputs:** `company/handoffs/H-0024-return.md`, `company/handoffs/H-0025-return.md`, `docs/CAPABILITIES.md`, `src/` (diff `85dca48..HEAD`), `out/` demo outputs, `quarantine/dev/` (dev testing only).
3. **Constraints:** Read-only on `src/` and `tests/`. Write only the review and the repro log, plus your own LOG.md. Never commit media or frames: extracted frames go to `out/h0026/` (git-ignored). You may view at most 3 extracted PNG frames (CLAUDE.md rule 1: a few keyframes only).
4. **Output:** `company/handoffs/H-0026-review.md` (verdict ACCEPT / ACCEPT WITH FINDINGS / REJECT, findings S1/S2/S3) + `company/handoffs/H-0026-repro.txt`.
5. **Done when:**
   - [ ] One demo run reproduced from the H-0025 return alone, into a fresh `out/h0026/` path. Its output is compared with the original (duration; hash, or a reason why it differs).
   - [ ] For all 3 demo outputs: the ffprobe duration matches the timeline's expected duration within 1 frame (33 ms at 30 fps); the output is 1080×1920 at 30 fps.
   - [ ] Captions checked on 3 extracted frames (timestamps chosen from the caption track, not by the engineer). Each frame shows the right text, the font pair, no tofu and the right direction. At least one frame is mid-zoom or from a style preset.
   - [ ] Honesty checks: one stub stage exits non-zero and writes no manifest; one UNSUPPORTED_FIELD rejection; spot-check CAPABILITIES.md against the renderer for 2 fields.
   - [ ] Full suite + ruff run in a clean worktree.
6. **Out of scope:** H-0020 hook work; governance docs; rights decisions (just flag them).
7. **Effort budget:** max 40 tool calls · max 2 retries.
8. **Escalate if:** any media or derived dev data is committed (that is an S1 → write HALT); a demo output silently ignores an op; durations off by more than 1 frame.
9. **Termination condition:** review + repro written. Or blocked after 2 retries.
10. **Consulted positions:** none (this is a single review).

## Addendum (Operator, after H-0025 return)
- Rule on H-0025 deviation D1: the validator's `allow_dev` opt-in admits `quarantine/dev/` only. Check that it is off by default, that it cannot admit other `quarantine/` paths, and that nothing outside `src.demo` sets it.
- Note the set_duration "no words = silence" behaviour on music clips. Say whether it is a finding or acceptable for now.
