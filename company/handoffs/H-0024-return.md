# RETURN H-0024 · engineering-lead · 2026-11-23

STATUS: DONE

SUMMARY:
- G2a: every stage that does no real work (describe, score, select, edit, and the `--input/--out` paths of ingest and render) now exits 2, prints `NOT_IMPLEMENTED: <stage>` to stderr, and leaves no manifest. A stale manifest is deleted. Only `validate` still does real stage-contract work.
- G2b/G2c: the validator returns `UNSUPPORTED_FIELD` with the JSON path for every field the renderer ignores: crop `auto_face`, caption `style`, all `effects[]` fields, all `audio[]` fields, and a caption `dir` that disagrees with libass's base direction. `docs/CAPABILITIES.md` is generated from the same table, and a test fails if the doc drifts or a schema field has no row. No schema change, so no ADR.
- G3: ingest defaults to `--language auto` and records `language_requested`, `language` and `language_probability`. New `src/captions.caption_track` turns a transcript into `tracks.captions`, with integer output-time ms computed by code and `dir` taken from the bidi strong classes. The renderer uses the EXP-008 pair (Noto Sans Arabic Regular plus `{\fnNoto Sans}` runs). A frame was rendered.
- G1: `experiments/dev_catalog.py` ran on all 9 clips with the cached `large-v3-turbo` (CPU int8), 17–116 s per clip. The CSV is below. Only the script is committed.

ARTIFACTS:
- Commits on `t2/install-company-os` (not pushed): `21b24a6` (G2a), `01a48a7` (G2b + G2c, one commit because they share `src/capabilities.py`), `9f05860` (G3 + G3 font), `e526cdb` (G1)
- New: `src/capabilities.py`, `src/bidi.py`, `src/captions.py`, `src/render/fontrun.py`, `docs/CAPABILITIES.md`, `experiments/dev_catalog.py`, `tests/unit/test_capabilities.py`, `tests/unit/test_captions.py`, `tests/unit/test_fontrun.py`, `tests/unit/test_ingest_language.py`, `tests/fixtures/timelines/unsupported/u1..u5`, `tests/fixtures/timelines/valid/v7_multilingual_captions.json`
- Changed: `src/manifest.py`, `src/{describe,score,select,edit,ingest,render}/__main__.py`, `src/validate/__init__.py`, `src/render/__init__.py`, `src/render/adapter.py` (docstring), `tests/fixtures/README.md`
- Not committed (git-ignored): `quarantine/dev/dev_manifest.csv`, `out/h0024/frame_ar_en.png`, `out/h0024/timeline.json`, `out/h0024/captions.{mp4,ass}`, `out/h0024/bg.mp4` (a synthetic lavfi colour clip, not dev media)

Tests whose expectations changed:
- `test_stage_cli.py`: only `validate` keeps the manifest-then-skip test. There is a new parametrized `NOT_IMPLEMENTED` test for 6 stages.
- `test_manifest.py`: `test_cli_prints_skip_on_rerun` now passes a real work function. `test_stub_manifest_never_satisfies_real_work` simulates a pre-H-0024 stub manifest. New test: `test_cli_stub_is_not_implemented`.
- `test_validate.py`: the effect-type, undeclared-audio-source and duplicate-id/effect-target tests now load `unsupported/u1`/`u2` and check rules only (`check_support=False`).

Fixtures changed:
- `v4_effects` and `v5_audio` moved to `unsupported/u1`, `u2`.
- `v2` and `v6` crop changed from `auto_face` to `center`. The `v3` style was removed.
- Counts are now 5 valid, 7 invalid and 5 unsupported.

EVIDENCE:
- `.venv/bin/ruff check .` gives `All checks passed!`
- `.venv/bin/python -m pytest -q` gives `221 passed, 8 skipped in 7.39s`. The suite had 155 passed and 8 skipped before H-0024. The 8 skips are the existing runtime-lock tests.
- G2a/G2b/G3 tests were red before the code: `test_capabilities` + `test_validate` showed 19 failed, and `test_captions` failed at import before `src/captions.py` existed. I did not record a red run for the G2a tests.
- Frame: `out/h0024/frame_ar_en.png`
  - png, 1080×1920, sha256 `ffd79c1d5e659afd…`
  - Shows "جربت iPhone 16 امبارح" (rtl) and "Link in bio" (ltr). I looked at it: the word order is right-to-left, Latin runs use Noto Sans, and nothing is missing.
  - Rendering it twice gave a byte-identical PNG and `.ass`.
  - libass verbose log: exactly 2 fontselect lines, `(Noto Sans Arabic, 400, 0) -> …/NotoSansArabic-Regular.ttf` and `(Noto Sans, 400, 0) -> …/NotoSans-Regular.ttf`. No `Glyph … not found` and no fallback line.
  - Repro:
    ```
    .venv/bin/python -m src.validate out/h0024/timeline.json && .venv/bin/python -m src.render out/h0024/timeline.json out/h0024/captions.mp4 && ffmpeg -v error -y -ss 1.5 -i out/h0024/captions.mp4 -frames:v 1 out/h0024/frame_ar_en.png
    ```
- G1 reproduction: `.venv/bin/python experiments/dev_catalog.py` (model `large-v3-turbo`, total about 8 min on 2 vCPU). Per-clip times: 29.6, 68.3, 115.5, 69.8, 62.4, 56.2, 16.8, 37.2, 36.9 s. All are under the 5-minute escalation limit.

```
file,duration_s,width,height,fps,has_audio,language,language_prob,words_per_min,scene_cuts,mean_shot_s
Download (1).mp4,18.118,576,1024,30.0,True,en,0.601,0.0,6,2.588
Download (2).mp4,503.067,576,1024,29.964,True,en,0.601,0.0,305,1.644
Download (3).mp4,91.1,576,1024,30.0,True,en,1.0,137.7,23,3.796
Download (4).mp4,503.067,576,1024,29.964,True,en,0.601,0.0,305,1.644
Download (5).mp4,37.467,576,1024,30.0,True,en,1.0,140.9,0,37.467
Download (6).mp4,35.989,576,1024,29.222,True,en,1.0,123.4,6,5.141
Download (7).mp4,21.855,576,1024,29.97,True,en,0.601,0.0,5,3.643
Download (8).mp4,60.0,576,1024,30.0,True,ar,0.806,3.0,4,12.0
Download.mp4,65.0,576,768,30.0,True,en,0.365,23.1,28,2.241
```

Reading the CSV (code facts, not a judgement):
- `Download (2)` and `Download (4)` are the same file (sha256 `fcc9134b3f421b2a…` for both).
- Four clips have 0 words after VAD. Their `en 0.601` is the detector's value on no speech, so treat it as "no speech" and not as English.
- Only clips 3, 5 and 6 are clear speech clips, all English at probability 1.0.
- Clip 8 is detected as `ar` at 0.806, but with only 3 words per minute it is likely music or a few words.
- None of the dev clips is an Arabic talking-head.

DEVIATIONS FROM BRIEF:
1. G2b and G2c are in one commit (`01a48a7`), not two, because the capability table is the single source for both the validator and the doc.
2. Caption `dir` is not forced by the renderer: ASS cannot force RTL, and only Encoding -1 (auto) was validated in E6 and EXP-008. So `dir` counts as rendered only when it equals libass's first-strong-character direction. Otherwise the validator returns `UNSUPPORTED_FIELD`. Consequence: `caption_track` uses the brief's majority rule, so a mostly-Arabic line that starts with a Latin word (e.g. "iPhone جديد جدا جدا") gets `dir: rtl`, the validator rejects it, and it is never silently mis-laid-out.
3. The render default changed from bold `Noto Naskh Arabic` to regular `Noto Sans Arabic`, because EXP-008 declared only the Regular files. Bold would select an undeclared face.
4. Characters outside the EXP-008 ranges now fail the render (`UnsupportedCharacter`). This includes Hebrew, Persian-specific letters outside U+0600–06FF (none are known), emoji and tabs. Hebrew is therefore auto-detected and gets `dir` correctly, but cannot be rendered yet.
5. The transcript cache name now includes the requested language (`transcript.<model>.<lang>.json`), so old cached transcripts are recomputed once.

OPEN QUESTIONS:
1. Should H-0025 make `caption_track` split, or re-derive `dir`, so mostly-Arabic lines that start with a Latin word render? Options are first-strong `dir`, or a leading RLM, which would need an EXP-008 amendment. Owner: engineering-lead with creative-lead.
2. In the frame, Noto Sans Arabic looks visibly smaller than Noto Sans at the same size. Is a per-run size scale wanted? Owner: creative-lead.
3. The dev set has no real Arabic speech clip. For an Arabic demo in H-0025, can the Founder supply one? Owner: Founder via Operator.
4. `Download (2)` and `Download (4)` are duplicates. Should one be dropped from `quarantine/dev/`? Owner: Founder.

CONFIDENCE: High for G2/G3 (tests plus a frame log showing only the declared fonts). Medium for G1's language column: detection on clips with no speech returns a confident-looking `en 0.601`, so `words_per_min == 0` must be read as "no speech".

NEXT RECOMMENDED STEP: In H-0025, implement style presets and zoom by flipping their rows in `src/capabilities.py` (the doc and validator follow), then build the demo on `Download (3)`/`(5)`/`(6)`.
