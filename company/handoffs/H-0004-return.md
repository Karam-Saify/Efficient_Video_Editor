# RETURN H-0004
- **From:** engineering-lead
- **STATUS:** DONE (uncommitted, as instructed; two interpretation flags below for Assurance/Founder)
- **SUMMARY (≤5 lines):**
  `schemas/timeline.schema.json` now implements the ARCHITECTURE.md v0 shape (integer ms, `canvas`, `sources[]`, `tracks.{video,captions,effects,audio}`, `provenance`).
  `src/validate` runs the draft 2020-12 schema check first, then the 7 semantic rules. It returns every issue as a structured `Issue(code, path, message)` with stable codes.
  There are 5 valid and 5 invalid fixtures. Each invalid fixture yields exactly one, different code. Rules 6 and 7 are covered by extra unit tests.
  The renderer accepts v0 through a new input adapter (`src/render/adapter.py`, ms → s). The FFmpeg graph and ASS writer are byte-for-byte unchanged.
  Result: 70 tests pass and ruff is clean. The tests also pass in a clean copy of the tree, and two validate runs give byte-identical `report.json`.

- **ARTIFACTS (paths):**
  - `schemas/timeline.schema.json` (rewritten to v0)
  - `src/validate/__init__.py` (validator, `Issue`, `total_duration_ms`), `src/validate/__main__.py` (legacy CLI + H-0003 `--input/--out` stage CLI, report errors are now objects)
  - `src/render/adapter.py` (new: v0 → internal render model), `src/render/__init__.py` (`render()` validates v0, then adapts; 5 lines)
  - `tests/fixtures/timelines/valid/v1_single_clip.json`, `v2_multi_clip.json`, `v3_captions_rtl_ltr.json`, `v4_effects.json`, `v5_audio.json`
  - `tests/fixtures/timelines/invalid/i1_source_missing.json`, `i2_range.json`, `i3_overlap.json`, `i4_caption_bounds.json`, `i5_duration.json`
  - `tests/fixtures/media/{src_a,src_b,music}.txt` (placeholder text "sources"; no media), `tests/fixtures/README.md`
  - `tests/fixtures/timeline_min.json` (migrated to v0), `tests/unit/test_stage_cli.py` (3 assertions migrated to v0), `tests/unit/test_validate.py` (new, 39 tests)

- **Rule → fixture → error code**

  | # | Rule | Invalid fixture | Code | Extra unit tests |
  |---|---|---|---|---|
  | 1 | source declared + file exists; sha256 checked only if file exists and `sha256` given | `i1_source_missing.json` (clip → undeclared `srcZ`) | `E_SOURCE_MISSING` (hash mismatch: `E_SOURCE_HASH`) | missing file, hash mismatch / no-hash, undeclared audio source, `base_dir` resolution |
  | 2 | `0 <= in_ms < out_ms <= duration_ms` | `i2_range.json` (out 11000 > 10000) | `E_RANGE` | in<0, in==out, in>out |
  | 3 | no overlapping video clips | `i3_overlap.json` (same source, [0,3000) ∩ [2000,4000)) | `E_OVERLAP` | adjacent ranges are not an overlap |
  | 4 | caption `0 <= start_ms < end_ms <= total` | `i4_caption_bounds.json` (end 3500 > 3000) | `E_CAPTION_BOUNDS` | end <= start |
  | 5 | total == target ± 1 frame, integers: `abs(total-target)*fps <= 1000` | `i5_duration.json` (+67 ms at 30 fps) | `E_DURATION` | boundary table at 25/30/60 fps (33 ok / 34 fail at 30, etc.) |
  | 6 | caption has `dir` ∈ {rtl, ltr} | **unit tests only** | `E_CAPTION_DIR` | missing, `"auto"`, `"RTL"` |
  | 7 | only known effect types (enum = `["zoom"]`) | **unit tests only** | `E_EFFECT_TYPE` | `"blur"` |
  | – | extra: duplicate source/clip/caption id; effect `target` not a clip id | – | `E_DUPLICATE_ID`, `E_EFFECT_TARGET` | 1 test |
  | – | any other structural/type error (e.g. float ms, missing required field) | – | `E_SCHEMA` | stops semantic checks; all schema errors are still listed |

  Design note: rules 6 and 7, and the `>= 0` parts of rules 2 and 4, are enforced by the schema, so the schema stays a complete contract for later structured LLM output. Those schema errors are mapped to the rule's own code (`_schema_code`) instead of `E_SCHEMA`. Semantic checks still run when the only schema errors are mapped ones, so "all errors" holds (test `test_all_errors_returned_not_just_first`).

- **EVIDENCE (commands + outputs / metric files):**
  - Reproduction (one line, from repo root): `.venv/bin/python -m pytest -q tests/unit/test_validate.py tests/unit/test_stage_cli.py && .venv/bin/ruff check .`
  - `.venv/bin/python -m pytest -q`
    ```
    ......................................................................   [100%]
    70 passed in 3.07s
    ```
  - `.venv/bin/ruff check .`
    ```
    All checks passed!
    ```
  - CLI on every fixture: valid ones print e.g. `OK: 3 clips, 9020 ms`, exit 0. Invalid ones print one line each and exit 1:
    ```
    E_SOURCE_MISSING /tracks/video/0/source: unknown source 'srcZ' (declared: srcA)
    E_RANGE /tracks/video/0/out_ms: clip 'c1': out_ms (11000) exceeds source 'srcA' duration_ms (10000)
    E_OVERLAP /tracks/video/1: clip 'c2' [2000, 4000) overlaps clip 'c1' [0, 3000) in source 'srcA'
    E_CAPTION_BOUNDS /tracks/captions/0/end_ms: caption 't1': end_ms (3500) is after the timeline end (3000 ms)
    E_DURATION /target_duration_ms: total duration 3067 ms differs from target 3000 ms by +67 ms; allowed is one frame (1000/30 ms)
    ```
  - Clean copy: I copied the tracked and new files (excluding `quarantine/` and `data/`) to a scratch directory and ran the full suite there: `70 passed`. I ran `python -m src.validate --input v5_audio.json --out o1|o2` twice. `cmp` reported `IDENTICAL`.
  - Render dry run: `test_render_accepts_valid_v0_timeline_dry_run` stubs `subprocess.run` and renders `v3_captions_rtl_ltr.json`. It asserts the ffmpeg graph contains `trim=start=2.0:end=8.0` and that the ASS file contains the Arabic dialogue line at `0:00:00.00–0:00:01.80`. `test_render_rejects_invalid_timeline` checks that `E_OVERLAP` blocks a render.
  - Python 3.11: no 3.11 interpreter in this Codespace (`.venv` is 3.14.2). Ruff runs with `target-version = "py311"` and passes. The code uses no 3.12+ syntax (no `type` statements, no same-quote nested f-strings). The only runtime dependency is `jsonschema==4.26.0`, which is already in `requirements-dev.txt`. CI on 3.11 is the real proof; it will run on push.
  - Secrets: the diff contains no keys or tokens (the only hex strings are fixture sha256 values of placeholder text files).
  - I-3 / I-4: no LLM involved. All time arithmetic is integer ms in `src/validate`, and the ms → s conversion happens only in `src/render/adapter.py`.
  - Tokens/minutes impact: zero tokens. Validation takes milliseconds. The sha256 check reads the whole source file, but only when `sha256` is given.

- **DONE-WHEN CHECK:**
  - ✅ Schema implements the ARCHITECTURE v0 shape; existing render path still works on a valid fixture (dry run): `test_render_accepts_valid_v0_timeline_dry_run`, `test_legacy_render_command_builder_still_works`
  - ✅ 7 rules implemented with error codes; all errors returned: table above, `test_all_errors_returned_not_just_first`
  - ✅ 5 valid + 5 invalid fixtures; tests green; ruff clean: `test_fixture_counts`, pytest/ruff output above
  - ✅ Entry appended to `company/positions/03-engineering/LOG.md`

- **Differences: old schema vs ARCHITECTURE v0 (ARCHITECTURE wins)**
  1. Seconds (float) → integer milliseconds everywhere (`in`/`out` → `in_ms`/`out_ms`, `start`/`end` → `start_ms`/`end_ms`, `duration` → `duration_ms`).
  2. `output` → `canvas`; `output.target_duration` (optional) → top-level `target_duration_ms` (**required**). Rule 5 now always applies.
  3. `sources` changed from an object keyed by id to an array of `{id, path, duration_ms, sha256?}`. Dropped: `width`, `height`, `fps`, `has_audio`.
  4. `clips` → `tracks.video`. Dropped: clip `note`. Added: optional `crop`.
  5. `captions.{style, items}` → `tracks.captions[]` with a per-caption named `style` string and a required `dir`. The global style object (font, size, colour, outline, position, margin_v) is gone; the renderer now always uses its `STYLE_DEFAULTS`.
  6. `video_id` and `output.reframe` dropped (not in v0). New: `tracks.effects`, `tracks.audio`, `provenance`.
  7. `fps` is now an integer (it was a number), so the frame tolerance is exact integer arithmetic. 29.97 fps cannot be expressed.
  8. Old validator rules no longer present: "caption overlaps previous caption" (dropped: not in ARCHITECTURE, and stacked bilingual captions may be wanted; Creative to decide in H-0007) and "clip shorter than one frame" (dropped: not in ARCHITECTURE). New: file existence, sha256, overlap, duplicate caption/source ids, effect target.

- **DEVIATIONS FROM BRIEF:**
  1. **Render-side input adapter (`src/render/adapter.py`, plus 5 lines in `render()`).** The done-when criterion requires the render path to accept a valid v0 timeline, and the renderer reads the old shape. I adapted the input and left the rendering logic alone. The ffmpeg graph and ASS output are unchanged for equivalent input. Assurance should judge whether this counts against "Rendering changes" being out of scope.
  2. **v0 fields the renderer ignores for now** (documented in the adapter docstring): `crop` (always centre crop; `auto_face` is not implemented), caption `style` and `dir`, `effects`, `audio`. Before H-0004 the renderer could do `fit_blur`/`fit_pad` and custom caption styling; v0 can no longer request either. Silent sources (old `has_audio: false`) are no longer expressible, so the renderer assumes every source has audio.
  3. **Values I chose where ARCHITECTURE gives only an example:** `crop` enum `["auto_face","center"]`; effects enum `["zoom"]`, with `scale` optional; caption `style` is a free non-empty string; `provenance` stays open. No field names were added or renamed. Two extra codes (`E_DUPLICATE_ID`, `E_EFFECT_TARGET`) and `E_SOURCE_HASH` were added beyond the brief's examples.
  4. **H-0003 artifacts touched:** I migrated `tests/fixtures/timeline_min.json` and 3 assertions in `tests/unit/test_stage_cli.py` to v0, as the fixture README required ("must be updated together with the schema"). Assurance is reviewing 5b2b39e in parallel, so its review of those files describes the pre-H-0004 state.
  5. **Consumer broken, not fixed (out of scope: EXP-006):** `experiments/e6_captions.py` builds an old-shape timeline and calls `render()`. It will now fail validation. It needs a port to v0 before anyone reruns E6 or EXP-006 (H-0006).
  6. **Order of work:** the schema came first, then the validator, fixtures and tests in the same pass. Strictly, the tests were not written before the code.
  7. **Branch:** the work is uncommitted on the current branch `t2/install-company-os`, not on `t2/H-0004`, because I was told not to commit. When this is committed it should go on `t2/H-0004`.

- **OPEN QUESTIONS (numbered, with who should answer):**
  1. **Rule 3 meaning (Assurance → Founder if disputed).** v0 clips have no timeline position; they play back-to-back, which is also how the renderer concatenates them. A timeline overlap is therefore impossible by construction. I read "overlap" as two clips using intersecting `[in_ms, out_ms)` ranges of the **same source**, which would show duplicated footage. Adjacent ranges are allowed. This rejects intentional repeats, such as a replayed punchline. Is that acceptable for M0?
  2. **"Total duration" (flag; does not conflict with the render code).** I read it as the sum of `out_ms - in_ms` over `tracks.video`, which matches the renderer's concat. The other reading (last caption end, or effects end) is not used.
  3. **Relative source paths (Engineering decision, flagged).** They resolve against the current working directory, as the renderer's ffmpeg call does, not against the timeline file's folder. The CLI must therefore run from the repo root. `validate()` takes a `base_dir` for other callers.
  4. **Creative (H-0007):** do v0 captions (`text`, `start_ms`, `end_ms`, `style`, `dir`) suffice for Arabic captions? Should overlapping or stacked captions be allowed (currently allowed), and which named styles exist?
  5. **Founder:** should `fit_blur`/`fit_pad` reframing and silent sources come back into the schema? Either one is a schema change that needs an ADR.

- **CONFIDENCE:** High for the validator and tests. Medium for scope fit (biggest doubt: rule 3's reading and the render adapter against "Rendering changes" being out of scope).
- **NEXT RECOMMENDED STEP:** Assurance reviews (H-0004-review.md) with the reproduction command above, and rules on open question 1 and deviation 1. After ACCEPT, commit on `t2/H-0004` with trailers `Role: engineering`, `Tier: T2`, `Reviewed-by: assurance-lead`. Then brief a small T1 to port `experiments/e6_captions.py` to v0 before H-0006.
