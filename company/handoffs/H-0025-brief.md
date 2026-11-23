# BRIEF H-0025
- **To:** engineering-lead
- **Tier / Milestone:** T2 (engine; one Assurance review at day end on this demo, ADR-0006) / M0→M1 build mode
- **Date:** 2026-11-23

1. **Objective (with why):** Build a pure-Python edit core and an end-to-end demo CLI. This proves the video-as-code loop works with no LLM: ingest → captions → ops → validate → render. Later the LLM will only choose ops. Founder goals 4–5 of 2026-11-23.
2. **Inputs (exact paths):**
   - `company/handoffs/H-0024-return.md` (what G1–G3 delivered: caption track builder, UNSUPPORTED_FIELD, CAPABILITIES.md)
   - `schemas/timeline.schema.json`, `src/validate/`, `src/render/`, `src/ingest/`, `src/common.py`, `docs/CAPABILITIES.md`
   - `quarantine/dev/dev_manifest.csv` (pick demo clips from it), `quarantine/dev/*.mp4` (dev testing only)
3. **Constraints:**
   - Code computes all times, never hand-typed constants in ops (CLAUDE.md rule 2). Schema first: every op output passes `src.validate`.
   - The renderer must actually implement everything the ops produce: caption style presets and zoom. If a field is not rendered, the validator must reject it (UNSUPPORTED_FIELD stays honest). Update `docs/CAPABILITIES.md` and its drift test.
   - Prefer no schema change. If word ids or presets need one, write a `Proposed` ADR (next free number) and list it in the return. An alternative is a word sidecar in `cache/<id>/edit/` that the timeline references by caption id.
   - No new dependencies, no LLM, CPU only. Never commit media or outputs. `out/` and `quarantine/` stay git-ignored.
   - Suite + ruff green. One commit per goal, trailers `Role: engineering-lead` / `Tier: T2`. Do not push.
4. **Output:** code + tests + 3 example ops files in `examples/ops/`, committed. Return at `company/handoffs/H-0025-return.md`.
5. **Done when:**
   - [ ] **G4** `src/edit/ops.py` (pure, no I/O inside the ops themselves) provides `trim(start_ms, end_ms)`, `delete_words(word_ids)`, `set_caption_style(preset)`, `add_zoom(at_ms, scale, duration_ms)` and `set_duration(target_ms)`. Each op takes timeline vN and returns vN+1, after `validate()` passes. Captions are re-timed by code when clips change (deleted words are cut from the video and removed from the captions). A small history store persists versions in `cache/<video_id>/edit/history/v<N>.json`, and `undo()` restores vN-1. Define the semantics of each op in its docstring (e.g. set_duration: how the cut is chosen, deterministic). Unit tests per op + undo + invalid-input cases (out-of-range ms, unknown word id, unknown preset).
   - [ ] **G4 render** Caption style presets (at least 3, e.g. `clean`, `bold_box`, `karaoke_hook` or similar, all with the EXP-008 font pair, working for RTL and LTR) and the zoom effect are rendered by FFmpeg. Frame-level evidence: one extracted frame per preset + one mid-zoom frame, in `out/`.
   - [ ] **G5** `python -m src.demo --video <path> --ops <ops.json> --out out/` runs ingest (cached) → caption track (auto language) → ops in order → validate → render at 1080×1920, 30 fps. It prints the output path, the final duration and the language. A non-zero exit on any failure, with a clear message.
   - [ ] **G5 examples** `examples/ops/` has 3 ops files (e.g. `trim_and_style.json`, `delete_words_zoom.json`, `fit_30s.json`). Word ids in examples must be resolvable or selected by rule, so they work on any clip. Document the ops.json format in the module docstring.
   - [ ] **G5 runs** Run the demo on 3 different clips from `quarantine/dev/`, at least one non-Arabic (use the catalog). Use a different ops file each time. Record for each run: command, output path in `out/`, ffprobe duration/size/fps, expected duration (from the timeline), and wall time.
   - [ ] Full suite + ruff green; commands and outputs in the return.
6. **Out of scope:** MILP select, LLM tools/prompts, Remotion, describe/score, H-0020 hook work, CI changes, governance docs.
7. **Effort budget:** max 60 tool calls · max 2 retries per failing action. Per the Founder, stop if any goal fails twice.
8. **Escalate if:** a schema change would invalidate existing valid timelines; FFmpeg cannot render a needed preset or zoom without a new dependency; no non-Arabic speech clip exists among the 9 (report it, then run on the best available and say so).
9. **Termination condition:** G4–G5 committed, 3 outputs in `out/`, suite green, return written. Or a goal has failed twice → STATUS: BLOCKED.
10. **Consulted positions:** Assurance reviews this demo once at day end (H-0026). It will reproduce one run, check durations with ffprobe, and check captions on 3 extracted frames, so make each run reproducible from the return alone.
