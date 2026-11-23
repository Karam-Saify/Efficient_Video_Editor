# RETURN H-0029
- **From:** engineering-lead
- **STATUS:** DONE (core). The stretch (text overlay) was not done and stays UNRENDERED.
- **SUMMARY (≤5 lines):** Recipe language v0 is in place: `schemas/recipe.schema.json`, 12 recipe files, the pure compiler `src/recipes/` with CLI `python -m src.recipes compile|check`, and `docs/RECIPE_LANGUAGE.md`. Following the Founder's scope change, the package is `src/recipes/` (plural) and R11 is replaced by `photos_to_video`. The matrix ran 36 cells. 33 compiled to valid timelines (11 video recipes × 3 speech clips). The other 3 are `photos_to_video` on 3 synthetic testsrc image sets, which fail with the designed `E_RECIPE_SOURCE_KIND` and list every missing feature as UNRENDERED. One additive timeline-schema change is filed as ADR-0014 (Proposed): optional `provenance.recipe`. The H-0026 F2 `ADR-0006 dev-only` marker is set in both the compiler and `src.demo`. Suite: 363 passed, 8 skipped; ruff clean.
- **ARTIFACTS (paths):**
  - `schemas/recipe.schema.json`; `schemas/timeline.schema.json` (+`provenance.recipe`)
  - `recipes/R01-one-tip.json` … `recipes/R10-trend-format.json`, `recipes/R12-bilingual.json`, `recipes/photos_to_video.json` (12)
  - `src/recipes/__init__.py` (compiler), `src/recipes/__main__.py` (CLI)
  - `src/capabilities.py` (+5 provenance meta rows, + `Feature`/`FEATURES` table); `docs/CAPABILITIES.md` (regenerated, new "Recipe features" section)
  - `src/demo/__main__.py` (F2 marker)
  - `docs/RECIPE_LANGUAGE.md` v0
  - `company/decisions/ADR-0014-timeline-provenance-recipe.md` (Proposed) + INDEX row
  - Tests: `tests/unit/test_recipes.py` (84 tests); fixtures `tests/fixtures/recipes/{valid(5),invalid(7)}/`, `tests/fixtures/timelines/provenance/{valid(5),invalid(6)}/`
  - Commits on `t2/install-company-os` (not pushed): c5a3e87 (schema), d2eb7dc (recipes + compiler + tests), 418f5ea (demo F2), 75973de (docs), plus the commit with this return
  - Scratch, git-ignored, not committed: `out/h0029/*.timeline.json`, `*.result.json`, 3 MP4s, `img_set{1,2,3}/` (synthetic testsrc PNGs)
- **EVIDENCE (commands + outputs / metric files):**
  - `.venv/bin/python -m src.recipes check` → `ok` for all 12 (R01..R10, R12, photos_to_video).
  - `.venv/bin/python -m pytest -q` → `363 passed, 8 skipped` (the 8 skips are the existing runtime-lock tests); `.venv/bin/ruff check .` → `All checks passed!`.
  - Determinism: compiling R05 on Download (3) again gave a timeline that `cmp` reports IDENTICAL to the first run (sha256 `49e14fc06a6dcf5c…` for both). Unit test `test_determinism_same_fill_byte_identical` covers the same with `--set` in a different order.
  - Renders, ffprobe (all 1080×1920, 30 fps; the timeline target duration is in brackets):
    - `out/h0029/Download5__R01.mp4`: 35.001 s [35000 ms], 8 zooms, `clean`
    - `out/h0029/Download3__R05.mp4`: 35.001 s [35000 ms], 3 item zooms, `bold_box`
    - `out/h0029/Download6__R10.mp4`: 18.000 s [18000 ms], 5 zooms, `hook`
    - Each `.timeline.json` contains `provenance.selection = "src.recipes <id>@1 language=en ADR-0006 dev-only"` and the `provenance.recipe` block. Render wall times: 90.8 s, 75.9 s, 40.3 s.
  - One-line repro for Assurance: `.venv/bin/python -m src.recipes compile --recipe R05 --video "quarantine/dev/Download (3).mp4" --allow-dev --out out/h0029/r.timeline.json && cmp out/h0029/r.timeline.json out/h0029/Download3__R05.timeline.json && .venv/bin/python -m pytest -q tests/unit/test_recipes.py` (needs the cached ingest of Download (3); if it is missing, run `python -m src.ingest "quarantine/dev/Download (3).mp4" --language auto --no-scenes` first).

### Compile matrix (12 × 3 = 36)
Clips: the 3 unique speech dev clips in `quarantine/dev/dev_manifest.csv`, which are `Download (3).mp4` (91.1 s, 138 wpm), `Download (5).mp4` (37.5 s, 141 wpm) and `Download (6).mp4` (36.0 s, 123 wpm). All three are English, and the dev set has no Arabic speech clip (H-0024). `photos_to_video` uses 3 synthetic image sets instead (ffmpeg lavfi testsrc, 3/4/5 PNGs, `out/h0029/img_set{1,2,3}`), as the scope change requires. It was also run on the 3 speech clips, where it gives the same designed error.
Cell format: `ms / clips / zooms`. `S` = `SHORT_SOURCE` warning (the source is shorter than `length_s` after the hook steps, so nothing was cut for length; this is not an error).

| recipe | tier | Download (3) | Download (5) | Download (6) | UNRENDERED (by recipe field) |
|---|---|---|---|---|---|
| R01 one-tip | A | ✅ 35000/13/8 | ✅ 35000/6/8 | ✅ 35000/2/8 | sound.music_bed, captions.per_beat, needs[]=keyword_highlight |
| R02 product demo | B | ✅ 30000/11/9 | ✅ 30000/10/9 | ✅ 30000/1/9 | sound.music_bed, sound.sfx, overlays[0]:price_cta, captions.per_beat, needs[]=b_roll |
| R03 testimonial | A | ✅ 40000/18/1 | ✅ S 37466/1/1 | ✅ S 35989/1/1 | overlays[0]:name_title |
| R04 before/after | B | ✅ 25000/1/1 | ✅ 25000/1/1 | ✅ 25000/1/1 | sound.music_bed, overlays[0]:before_after, structure.reorder, needs[]=transitions, needs[]=second_source |
| R05 listicle | B | ✅ 35000/13/3 | ✅ 35000/6/3 | ✅ 35000/2/3 | sound.sfx, overlays[0]:number_badge, needs[]=transitions |
| R06 offer promo | B | ✅ 25000/9/8 | ✅ 25000/7/7 | ✅ 25000/1/7 | sound.music_bed, sound.sfx, overlays[0]:date_price_place, needs[]=stickers |
| R07 behind the scenes | A | ✅ 35000/13/5 | ✅ 35000/6/5 | ✅ 35000/2/5 | sound.music_bed, captions.per_beat, needs[]=speed_ramp, needs[]=b_roll |
| R08 FAQ | A | ✅ 30000/11/1 | ✅ 30000/10/1 | ✅ 30000/1/1 | needs[]=keyword_highlight |
| R09 story hook | B | ✅ 45000/19/8 | ✅ S 37466/1/7 | ✅ S 35989/1/7 | sound.music_bed, captions.per_beat, structure.reorder |
| R10 trend | B | ✅ 18000/7/5 | ✅ 18000/6/5 | ✅ 18000/1/5 | sound.music_bed, overlays[0]:template_text, needs[]=transitions, needs[]=stickers |
| R12 bilingual (compile only) | B | ✅ 40000/18/7 | ✅ S 37466/1/7 | ✅ S 35989/1/7 | needs[]=per_script_size |
| photos_to_video | C | ✅* img_set1 (3) | ✅* img_set2 (4) | ✅* img_set3 (5) | sound.music_bed, overlays[0]:photo_text, overlays[1]:brand_offer, needs[]=image_source, needs[]=pan_zoom, needs[]=transitions |

✅* = the designed failure `E_RECIPE_SOURCE_KIND: image sources cannot be expressed in timeline v0 or rendered`, which counts as a pass under the brief. Count: 33 timelines compiled and passed validation (every compile ends in `src.validate`). 11 recipes compile, so the "≥ 9 compile" escalation rule is not triggered. That count includes 6 degraded recipes, and each of them lists every missing feature as UNRENDERED, as the addendum requires.

- **DONE-WHEN CHECK:**
  - ✅ All 12 recipes validate against `recipe.schema.json`: `src.recipes check` and `test_every_recipe_validates[12]`.
  - ✅ Every recipe compiles to a valid timeline on 3 dev clips (36): see the matrix. The designed failures are `photos_to_video` × 3 with `E_RECIPE_SOURCE_KIND`, tested by `test_photos_to_video_fails_with_designed_code_and_lists_unrendered[3,4,5]` on generated testsrc images.
  - ✅ Rendered 3 of the 36 (different recipes) to `out/h0029/`: `Download5__R01.mp4`, `Download3__R05.mp4`, `Download6__R10.mp4`.
  - ✅ Unit tests for param type/range errors (`test_param_errors[10]`, `test_parse_set_types`, `test_start_at_range_is_the_source_length`), unknown recipe id (`test_unknown_recipe_id`, CLI exit 2), UNRENDERED reporting (`test_unrendered_lists_every_missing_feature_by_field`, `test_every_recipe_schema_property_is_classified`, `test_compile_result_and_provenance_carry_unrendered`), provenance content (`test_provenance_content`, `test_allow_dev_sets_the_adr0006_marker`) and determinism (`test_determinism_same_fill_byte_identical`).
  - ✅ Suite and ruff are green: 363 passed, 8 skipped; ruff clean.
  - Addendum, R11: superseded by the Founder scope change, because R11 no longer exists. The equivalent decision for its replacement `photos_to_video` is that it **fails with the designed code** on any source and reports image_source, pan_zoom, music and overlays as UNRENDERED. Tested.
  - Addendum, stretch (text overlay): ❌ not done, because the core plus the scope change used the ~40-call window. It stays UNRENDERED and is item 1 of the backlog in RECIPE_LANGUAGE.md §7. A reorder op, music bed and per-beat style were not built, and all three are listed in the backlog.
  - Addendum, R12: `golden_set: false` in the recipe; compiled only.
- **DEVIATIONS FROM BRIEF:**
  1. Package `src/recipes/` and CLI `python -m src.recipes` instead of `src/recipe/` (Founder scope change). R11 is replaced by `photos_to_video` (Founder scope change). Recipe ids may be `R\d\d` or snake_case.
  2. Recipe meaning changes against H-0028, for creative-lead to confirm:
     - (a) Beats are proportional time windows, not content-aligned. Every beat-anchored zoom (R03 turning point, R05 items, R08 verdict) is therefore positional.
     - (b) R06 wants a punch-in "on the date/price word". The compiler cannot find that word without a model, so R06 uses rhythm placement.
     - (c) R03 keeps `punch_in_every_s` as a param, but placement is the turning-point beat only, so the param is unused (noted in the recipe).
     - (d) R04 uses `duration_mode: window` (one continuous take) and R09 uses `tighten`.
     - (e) The pacing wpm targets, cut intervals and dead-air limits are advisory, not enforced, because there is no op for speech rate or shot cuts.
     - (f) The R08 question card is not declared as an overlay, so R08 stays tier A for spoken questions.
     - (g) R10 has no `cut_fillers` param (as in H-0028), so its fillers are kept.
  3. Timeline schema change: additive optional `provenance.recipe` (ADR-0014 Proposed). All existing valid fixtures stay valid (`test_existing_timeline_fixtures_still_valid`).
  4. "Advisory" is a second honesty category next to UNRENDERED. The result lists fields the compiler keeps only for explanations (`hook.rule`, `pacing.wpm`, …), so they are not mistaken for enforced targets.
- **OPEN QUESTIONS (numbered, with who should answer):**
  1. (assurance-lead) Rule on ADR-0014 (`provenance.recipe`), and confirm that the compile CLI's `--allow-dev` as an explicit human flag satisfies the D1/F2 scope. The compiler never sets `allow_dev` itself.
  2. (creative-lead) Accept deviations 2a–2g, especially the proportional beats and the R06 rhythm placement, or say which need a model-chosen anchor first.
  3. (creative-lead / Assurance, H-0028 OQ3 answered by code) Assuming ASS PlayResY = 1920, the preset bottom edges are `clean` 83.3 % and `bold_box` 82.3 % of the height (margin_v 320/340, bottom-aligned), and `hook`'s top edge is at 21.9 %. **The clean and bold_box captions sit below the style guide's 72 % bound.** No preset was changed (out of scope). The right-12 % rule was not measured.
  4. (Operator / product-lead) Next unlock: text overlay (7 recipes) or still-image sources + pan/zoom (photos_to_video; needs a source-type schema change and ADR)?
  5. (research-lead) `SPEECH_MIN_WPM = 30` is taken from the 9-clip dev manifest (no-speech clips 0–23 wpm, speech 123+). It is uncalibrated on Arabic.
- **CONFIDENCE:** Medium-High (the compiler, tests and determinism are verified. The biggest doubt is editorial: proportional beats on English clips say nothing about how the recipes look in Arabic, and the 3 renders were not viewed (I-3/viewing is Assurance and Creative's job)).
- **NEXT RECOMMENDED STEP:** Assurance H-0029 review using the repro line above. Then a T2 brief for the text-overlay op + ASS renderer path with the EXP-008 pair.
