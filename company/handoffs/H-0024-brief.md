# BRIEF H-0024
- **To:** engineering-lead
- **Tier / Milestone:** T2 (engine; reviewed once at day end on the demo per ADR-0006) / M0→M1 build mode
- **Date:** 2026-11-23

1. **Objective (with why):** Make the engine honest and multilingual, and catalog the dev clips. Today's end-to-end demo (H-0025) has to run on real clips, and nothing may pretend to work when it doesn't. Founder goals 1–3 of 2026-11-23.
2. **Inputs (exact paths):**
   - `company/decisions/ADR-0006-build-mode.md` (build mode, dev-only clips, multilingual)
   - `quarantine/dev/*.mp4` (9 TikTok clips, git-ignored, INTERNAL DEV TESTING ONLY)
   - `src/manifest.py`, `src/{describe,score,select,edit}/__main__.py`, `src/ingest/__main__.py`, `src/common.py`
   - `src/validate/__init__.py`, `schemas/timeline.schema.json`, `src/render/__init__.py`, `src/render/adapter.py`
   - `company/experiments/EXP-008.md` + `experiments/` EXP-008 splitter + `tests/unit/test_exp008_splitter.py` (the font pair: Noto Sans Arabic for Arabic runs, Noto Sans for Latin and digits)
   - `tests/unit/test_stage_cli.py`, `tests/unit/test_validate.py`
3. **Constraints:**
   - CLAUDE.md core rules 1–6 (CPU only; code computes all times; schema first; cache under `cache/<video_id>/<stage>/`).
   - Never commit media, frames or transcripts of the dev clips. Commit only code, tests and docs. `quarantine/` and `out/` stay git-ignored.
   - No new dependencies unless already in `requirements.txt`. If one is unavoidable, ESCALATE.
   - Schema changes are allowed only when strictly needed. Each one gets an ADR (`Proposed`, next free number ADR-0007) and is listed in the return.
   - Keep the suite green: `.venv/bin/python -m pytest -q` and `ruff check .`. Update tests whose expectations change (the stub manifest tests), and say which ones in the return.
   - No parallel agents. Do not edit `company/` governance docs except your own LOG.md and the return.
4. **Output:** code + tests, committed on the current branch (`t2/install-company-os`), one commit per goal, trailers `Role: engineering-lead` / `Tier: T2`. Return at `company/handoffs/H-0024-return.md` (OPERATING_MODEL §4 shape).
5. **Done when:**
   - [ ] **G1** `experiments/dev_catalog.py` writes `quarantine/dev/dev_manifest.csv` with columns file, duration_s, width, height, fps, has_audio, language, language_prob, words_per_min, scene_cuts, mean_shot_s for all 9 clips. Detection uses faster-whisper (the cached `large-v3-turbo`; `tiny` is also cached if that is too slow, so say which). Run it and paste the CSV into the return. Only the script is committed.
   - [ ] **G2a** `describe`, `score`, `select`, `edit` stage stubs exit non-zero, print `NOT_IMPLEMENTED: <stage>` to stderr, and write no success manifest. This holds for every stage that does not really do its work, including the `src.ingest --input/--out` stage-contract path if it still does not decode media. Tests cover it.
   - [ ] **G2b** The validator rejects every timeline field the renderer does not actually implement, with error code `UNSUPPORTED_FIELD` and the JSON path. Example: `crop: auto_face`, `audio[].duck_under_speech`, or `effects` if they are not rendered yet. Tests cover each field. H-0025 will implement caption style presets and zoom, so those fields become supported then.
   - [ ] **G2c** `docs/CAPABILITIES.md`: a table with one row per schema field: validated (y/n), rendered (y/n), notes. Generate it or check it with a test, so it cannot drift from the validator's supported-field list.
   - [ ] **G3** Ingest auto-detects language by default (`--language auto` is the default; `--language ar` etc. still overrides) and records `language` + `language_probability` in the transcript. New pure function: transcript → caption track (timeline `tracks.captions`, output-time ms computed by code). `dir` is computed from the text's script: rtl when the strong characters are mostly Arabic/Hebrew/Persian (Unicode bidi classes R/AL), else ltr. Unit tests cover ar, en, fr, he and a mixed ar+English line.
   - [ ] **G3 font** The renderer uses the EXP-008 font pair, Noto Sans Arabic + Noto Sans, the same way EXP-008 did. No undeclared fallback. Write one rendered frame to `out/` showing an Arabic caption and an English caption, and name its path in the return.
   - [ ] Full suite + ruff green. Commands and outputs are in the return.
6. **Out of scope:** edit ops, `src.demo` (that is H-0025); MILP select; LLM calls; H-0020 hook work (its WIP tests are parked in `company/handoffs/H-0020-wip/`, leave them there); CI changes; trend/scraper tooling.
7. **Effort budget:** max 60 tool calls · max 2 retries per failing action. Per the Founder, stop if any goal fails twice.
8. **Escalate if:** a new dependency is needed; faster-whisper cannot detect language on CPU in reasonable time (>5 min per clip); a schema change would break existing valid timelines; any step would need committing or uploading dev media.
9. **Termination condition:** G1–G3 are committed with the suite green and the return written. Or a goal has failed twice: then write STATUS: BLOCKED and stop.
10. **Consulted positions:** Assurance reviews once at day end on the H-0025 demo (ADR-0006). No other position is consulted.
