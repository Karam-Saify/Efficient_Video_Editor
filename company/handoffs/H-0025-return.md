# RETURN H-0025 · engineering-lead · 2026-11-23

STATUS: DONE (with deviations D1 to D3 below, for Assurance to rule on in H-0026)

SUMMARY:
- **G4 ops.** `src/edit/ops.py` is pure Python with no LLM. It provides `trim`, `delete_words`, `set_caption_style`, `add_zoom` and `set_duration`.
  - Each op takes vN and an `EditContext`, never mutates its input, and returns vN+1 only after `validate()` passes. Otherwise it raises `OpError` with a code.
  - Captions are rebuilt by code after every cut, so a deleted word leaves both the video and the captions.
  - Cut points snap to the canvas frame grid.
  - History is stored in `cache/<id>/edit/history/v<N>.json`, and `History.undo()` restores vN-1.
- **G4 render.**
  - There are 3 caption presets: `clean`, `bold_box` and `hook`. All use the EXP-008 pair at Regular weight with Encoding -1.
  - Zoom is a punch-in: split, then centre crop, then scale, then overlay with `enable`. It sits under the captions.
  - The validator now returns `UNSUPPORTED_FIELD` for an unknown preset and for a zoom `scale` outside [1, 2], and `E_EFFECT_BOUNDS` for a zoom past the timeline end. `docs/CAPABILITIES.md` was regenerated.
- **G5.**
  - `python -m src.demo` runs ingest (cached), then captions (auto language), then the ops, then validate, then a render at 1080×1920 and 30 fps.
  - There are 3 rule-based ops files in `examples/ops/`.
  - It ran on 3 English clips plus the optional weak Arabic run. Every output is within one frame of the timeline duration, and a rerun gave a byte-identical MP4.

ARTIFACTS (branch `t2/install-company-os`, not pushed):
- **Commits:**
  - `cd00569` G4 render
  - `8352262` G4 ops
  - `c7b9690` G5 demo
- **New files:**
  - `src/presets.py`, `src/edit/ops.py`, `src/edit/history.py`, `src/demo/__init__.py` (the ops.json format is documented here), `src/demo/__main__.py`
  - `examples/ops/{trim_and_style,delete_words_zoom,fit_30s}.json` + `README.md`
  - `examples/timelines/presets_ar_en.json`
  - `tests/unit/test_edit_ops.py`, `tests/unit/test_demo_cli.py`
  - `tests/fixtures/timelines/valid/v4_effects_zoom.json`, `tests/fixtures/timelines/invalid/i8_effect_bounds.json`
- **Changed files:**
  - `src/render/__init__.py`, `__main__.py` (`--allow-dev`), `adapter.py`
  - `src/validate/__init__.py`, `__main__.py` (`--allow-dev`)
  - `src/capabilities.py`, `docs/CAPABILITIES.md`, `src/captions.py`
  - `tests/unit/test_{capabilities,validate,fontrun}.py`, `tests/fixtures/README.md`
  - `tests/fixtures/timelines/unsupported/u1_effects.json`: effect 0 now has `scale` 0.8, so it stays unsupported.
- **Changed test expectations:**
  - `u1` now expects only `/tracks/effects/0/scale`, because zoom renders now.
  - `u4` now expects only `/tracks/captions/2/style`, because `hook` is a preset and `cta` is not.
  - The ASS Dialogue style name is now `clean`, not `Default`.
  - Fixture counts: 6 valid, 8 invalid, 5 unsupported.
- **Not committed (git-ignored)** in `out/h0025/`: the 4 demo MP4s with their `.ass` and `.timeline.json`, `presets_ar_en.mp4`, `bg.mp4` (lavfi test pattern), and the frames listed below. Also `cache/<id>/edit/{words.json,history/}`.
- No schema change, so no ADR. No new dependency.

EVIDENCE:
- `.venv/bin/ruff check .` gives `All checks passed!`. `.venv/bin/python -m pytest -q` gives `266 passed, 8 skipped` (it was 221 + 8 before this brief).
- I wrote the tests before the code, but I did not record a red run (`test_edit_ops` and `test_demo_cli` could not import before the modules existed). The ops tests passed on their first run against the new code.

### G5 runs (all from the repo root, `.venv`, model `large-v3-turbo` CPU int8, ingest cached after the first run)

| # | command | output | timeline ms | ffprobe (format / video / audio) | frames | size, fps | language | wall |
|---|---|---|---|---|---|---|---|---|
| 1 | `.venv/bin/python -m src.demo --video "quarantine/dev/Download (5).mp4" --ops examples/ops/trim_and_style.json --out out/h0025` | `out/h0025/Download_5__trim_and_style.mp4` (24.4 MB) | 17333 | 17.333 / 17.333 / 17.333 s | 520 | 1080x1920, 30 | en (p=1.0) | 82.9 s (ingest not cached); 34.7 s cached |
| 2 | `.venv/bin/python -m src.demo --video "quarantine/dev/Download (6).mp4" --ops examples/ops/delete_words_zoom.json --out out/h0025` | `out/h0025/Download_6__delete_words_zoom.mp4` (28.3 MB) | 35755 | 35.767 / 35.767 / 35.756 s | 1073 | 1080x1920, 30 | en (p=1.0) | 142.1 s (not cached) |
| 3 | `.venv/bin/python -m src.demo --video "quarantine/dev/Download (3).mp4" --ops examples/ops/fit_30s.json --out out/h0025` | `out/h0025/Download_3__fit_30s.mp4` (28.2 MB) | 30000 (from 91100, 11 clips) | 30.002 / 30.000 / 30.002 s | 900 | 1080x1920, 30 | en (p=1.0) | 152.4 s (not cached) |
| 4 (weak) | `.venv/bin/python -m src.demo --video "quarantine/dev/Download (8).mp4" --ops examples/ops/fit_30s.json --out out/h0025 --language ar` | `out/h0025/Download_8__fit_30s.mp4` | 30033 (target 30000) | 30.033 / 30.033 / 30.012 s | 901 | 1080x1920, 30 | ar (forced) | 68.8 s |

- The expected duration is `timeline ms` (the sum of clip lengths in `out/h0025/<name>.timeline.json`). Every video stream is within one frame (33 ms) of it: the differences are 0, 12, 0 and 0 ms.
- Run 3 has 11 cuts and exactly 900 frames, so the frame-grid snapping shows no drift.
- **Wall-time caveat:** runs 2 and 3 ran one after the other while I was doing other work, so their wall times include contention.
- **Run 4 is labelled weak** (3 words per minute). It has one caption, "لنصنع لبن أمو" (rtl). `set_duration` removed 30 s of "no word" time, which here is music, not silence (OQ2).
- **Determinism:** I reran run 1 with ingest cached into `out/h0025_rerun/`. The `.mp4` (sha256 `c63fc6dc12a2f214…`), `.timeline.json` (`bda8d7eb…`) and `.ass` (`45e76b3e…`) are byte-identical to the first run. `presets_ar_en.mp4` also rendered twice to the same bytes (`1bc7fc2e…`).
- **Fast repro for Assurance:**
  - Run 1 with cached ingest takes about 35 s. On a clean cache it is about 85 s, because ingest transcribes first.
  - Check the output with `ffprobe -v error -show_entries stream=codec_type,duration,nb_frames -of compact out/h0025/Download_5__trim_and_style.mp4`.
  - Validate the saved timeline with `.venv/bin/python -m src.validate out/h0025/Download_5__trim_and_style.timeline.json --allow-dev`.

### G4 render frames (`out/h0025/`, all png 1080×1920; I looked at each one)

Synthetic Arabic/English frames are reproducible with:
```
mkdir -p out/h0025 && ffmpeg -v error -y -f lavfi -i testsrc2=size=576x1024:rate=30:duration=6 -f lavfi -i sine=frequency=440:duration=6 -c:v libx264 -pix_fmt yuv420p -c:a aac -shortest out/h0025/bg.mp4 && .venv/bin/python -m src.render examples/timelines/presets_ar_en.json out/h0025/presets_ar_en.mp4 && for t in 0.75 2.25 3.75 5.25; do ffmpeg -v error -y -ss $t -i out/h0025/presets_ar_en.mp4 -frames:v 1 out/h0025/ar_en_$t.png; done
```

| frame | shows |
|---|---|
| `ar_en_0.75.png` (`1964312c…`) | `clean`, rtl, "جربت iPhone 16 امبارح" |
| `ar_en_2.25.png` (`688f4c3e…`) | `bold_box`, rtl, "السعر الحقيقي؟", on a semi-opaque box; no zoom, testsrc2 timecode visible top-left |
| `ar_en_3.75.png` (`8e9f85b7…`) | `hook`, rtl, "وين بتلاقيه؟ Link in bio": Arabic on the right, Latin in Noto Sans on the left, yellow, upper third. Mid-zoom ×1.3: the colour bars are visibly wider and the timecode is cropped out |
| `ar_en_5.25.png` (`021b1da2…`) | `bold_box`, ltr, "Link in bio" |
| `frame_hook_run5.png` | real clip, `hook`, "300. This vehicle has" |
| `frame_bold_box_run3.png` | real clip, `bold_box` |
| `frame_clean_run6_nozoom.png` / `frame_midzoom_run6.png` | real clip, `clean`. At 22.2 s, inside the ×1.4 zoom [21453, 22953) ms, the TikTok watermark is cut off at the right edge |
| `frame_ar_run8.png` | real clip, `bold_box`, Arabic rtl |

- Extracting a frame from a run: `ffmpeg -v error -y -ss <t> -i <mp4> -frames:v 1 <png>`.
- Font check: `ffmpeg -v verbose -i out/h0025/bg.mp4 -vf "scale=1080:1920,ass=filename=out/h0025/presets_ar_en.ass:shaping=complex" -f null - 2>&1 | grep fontselect` prints exactly 2 lines: `(Noto Sans Arabic, 400, 0) -> NotoSansArabic-Regular.ttf` and `(Noto Sans, 400, 0) -> NotoSans-Regular.ttf`. There are no `Glyph not found` lines.

DEVIATIONS FROM BRIEF:
- **D1. The validator has a dev opt-in.** `validate(..., allow_dev=True)` admits sources under `quarantine/dev/` only, never other protected roots (tested).
  - Without it, the demo could not render any dev clip, because `quarantine/` is a protected root (`E_SOURCE_PATH`).
  - It is set only by `src.demo`, when the video is under `quarantine/dev/`, and the demo prints `note: … internal development testing only (ADR-0006)`. It is also available as `--allow-dev` on the `src.validate` and `src.render` CLIs.
  - The alternative was copying the clips out of quarantine, which would hide the source. I chose the visible opt-in. This is a policy-adjacent change for Assurance to accept or reject (OQ1).
- **D2. The renderer now runs `fps` before `trim`** for every clip. Together with the ops' frame-grid snapping, each clip renders an exact frame count, so many cuts add no A/V drift. Single-clip renders are unchanged in duration. This is a behaviour change to existing renders.
- **D3. Caption `dir` now follows the first strong character**, as the Addendum decided. The `bold_box` preset is not bold-weight, because EXP-008 declared only the Regular files; "bold" refers to the box.
- **Minor changes:**
  - New validator code `E_EFFECT_BOUNDS`.
  - The `tracks.effects[].target` row became kind `meta`, because the zoom applies to output time.
  - The ops.json format adds `{"op": "undo"}`.
  - The brief's `undo()` is `History.undo()`.

OPEN QUESTIONS:
1. Assurance: is the `allow_dev` opt-in (D1) an acceptable reading of ADR-0006, or should dev renders go through another mechanism? Owner: assurance-lead.
2. `set_duration` treats any stretch without ASR words as removable "silence". On a music clip (run 4) that cut 30 s from the middle. Should it use an audio-energy test instead? Owner: engineering-lead with creative-lead.
3. Run 4 landed exactly at the one-frame limit: 30033 ms against a target of 30000. The cause is that the tail snap happens in source time and the source grid is offset from the output grid. Snapping the tail to the output grid would make this exact. This is a small fix for the next brief.
4. Caption grouping crosses sentence ends ("300. This vehicle has"), and `bold_box`/`clean` look small on 576-px sources. These are for creative-lead.

CONFIDENCE: High for ops semantics, validation and determinism (tests plus byte-identical reruns). High for preset and zoom rendering, based on the frames I inspected and the fontselect log. Medium for `set_duration` quality on non-speech audio (OQ2).

NEXT RECOMMENDED STEP: Assurance H-0026 reproduces run 1 from a clean `out/`. It should check the four ffprobe values in the table above and the frames `ar_en_0.75/2.25/3.75.png`, and rule on D1.
