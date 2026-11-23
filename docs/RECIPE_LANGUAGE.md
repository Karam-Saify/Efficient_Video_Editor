# Recipe language v0 (H-0029)

A **recipe** is a typed, versioned JSON document (`recipes/*.json`, schema `schemas/recipe.schema.json`) that
describes one Short format: beats, hook rule, pacing, caption look, sound, typed params and the principles it
rests on (ADR-0008). A **fill** is a value for each param. Today fills come from the param defaults or from
`--set`; later a model will propose them (only the values, never times). The compiler in `src/recipes/` turns
recipe + fill + source into a validated timeline v0 through the `src/edit` ops. It is pure Python with no LLM,
and all times are computed by code (I-4).

```
python -m src.recipes check                       # every recipe in recipes/ against the schema + semantic rules
python -m src.recipes compile --recipe R01 --video "quarantine/dev/Download (5).mp4" --allow-dev \
    --set length_s=30 --out out/r01.timeline.json --result out/r01.result.json
python -m src.render out/r01.timeline.json out/r01.mp4 --allow-dev
```
`compile` reads the **cached** ingest (`cache/<video_id>/meta.json` and the transcript). It never runs ASR; if
the cache is missing it fails with `E_RECIPE_INGEST` and prints the ingest command to run.

## 1. Recipe fields
| field | meaning | compile effect |
|---|---|---|
| `id`, `version` | `R01`..`R12` or a snake_case name (`photos_to_video`); integer version | provenance |
| `name`, `tier`, `use_case`, `golden_set` | H-0028 labels; `golden_set: false` = compile only (R12) | none (labels) |
| `source.speech` | `required` / `forbidden` / `any`, measured as ASR words/min against `SPEECH_MIN_WPM` = 30 | gate: `E_RECIPE_SOURCE` |
| `source.kind` | `video` (default) or `images` | gate: `E_RECIPE_SOURCE_KIND` |
| `beats[]` | `{id, label, share_pct}`, shares sum to 100; `repeat_param: item_count` splits a beat into N equal items | proportional output windows (used for zoom placement) |
| `hook.cut_greeting` | delete greeting words that start in the first 2 s | `delete_words` |
| `hook.lead_in_ms` | if the first word starts later than this, trim the start to 120 ms before it | `trim` |
| `hook.rule` | editorial rule text | advisory |
| `pacing.duration_mode` | `tighten` = `set_duration` (silence longest-first, then the tail); `window` = one continuous take | `set_duration` or `trim` |
| `pacing.wpm`, `cut_interval_s`, `max_dead_air_ms` | targets from H-0028 | advisory (not enforced) |
| `captions.preset` | `{"param": "caption_look"}` or `"none"` (no caption track at all) | `set_caption_style` |
| `captions.per_beat` | wanted preset per beat | **UNRENDERED** |
| `zoom.placement` | `rhythm` (every `punch_in_every_s`), `beats` (start of the listed beats; a repeat beat = each item), `fraction`, `none`; `duration_ms` 100 to 1500 (default 800) | `add_zoom` |
| `sound.available` | what the render carries: the source audio | none |
| `sound.music_bed`, `sound.sfx` | wanted audio | **UNRENDERED** |
| `overlays[]` | unspoken on-screen text (title, price card, badge, ...) | **UNRENDERED** |
| `structure.reorder` | `cold_open` / `after_first` | **UNRENDERED** (no reorder op) |
| `needs[]` | other features: transitions, b_roll, stickers, speed_ramp, zoom_ease, beat_sync, keyword_highlight, per_script_size, second_source, image_source, pan_zoom | **UNRENDERED** each |
| `params` | see section 2 | fill |
| `principles[]` | `P-...` ids (H-0028 section 4, uncalibrated SG/J status) | provenance |
| `language`, `notes` | ar/en/fr/mixed behaviour notes | advisory |

`tests/unit/test_recipes.py::test_every_recipe_schema_property_is_classified` fails if a schema property is
added that is neither compiled, a feature source (FEATURES in `src/capabilities.py`) nor advisory. So no
field can be dropped silently.

## 2. Params (typed, with defaults and ranges)
Only these names are allowed (schema `propertyNames`), so every param has a defined meaning.
| name | type | maps to |
|---|---|---|
| `length_s` | int | `set_duration` target or window length; the source must be at least `min` s after the hook steps |
| `cut_fillers` | bool | `delete_words` on hesitation sounds (`FILLERS`: um, uh, erm, euh, امم ...; never content words) |
| `punch_in_every_s` | float | rhythm zoom spacing |
| `punch_in_strength` | float | zoom scale (style guide 1.05 to 1.20) |
| `caption_look` | enum clean/bold_box/hook | preset |
| `start_at_s` | float, max may be `"source_duration"` | `trim` start |
| `item_count` | int | number of repeat beats |
| `seconds_per_image` | float | photos_to_video (not compiled today) |

Each param spec is `{type, default, min, max}` (numbers), `{type: enum, default, values}`, or `{type: bool,
default}`. `int` is strict (`30.0` and `true` are not ints). A `float` accepts an int and stores a float.

## 3. Compile semantics (in this order; each step is one `src/edit` op on the previous timeline)
0. Check: recipe (schema, then semantic rules), then fill (unknown, type, range), then source kind and speech.
1. v0 = the whole source as one clip, with captions from the ASR words (none if `captions.preset` is `"none"`).
2. `start_at_s > 0` → `trim(start, end)`.
3. `hook.cut_greeting` → `delete_words` (greetings starting before 2 000 ms of output time).
4. Lead-in: if the first word starts after `lead_in_ms` → `trim(first_word - 120, end)`.
5. `cut_fillers` → `delete_words` (all hesitation sounds still in the timeline).
6. Length: if the timeline is longer than `length_s`, run `set_duration` (tighten) or `trim(0, length)`
   (window). If it is shorter, record the warning `SHORT_SOURCE`, which is not an error.
7. `set_caption_style(caption_look)`. If the timeline has no captions (a silent source on an `any` recipe), add
   `captions.preset` to UNRENDERED.
8. Zooms on the final timeline T. Beat windows are `T * cumulative_share // 100` (integer). Rhythm uses
   `k * every`, k >= 1. Each time snaps to the first word that starts in the next half-interval (for `beats`,
   the first half of the beat), then floors to the frame grid. A zoom is skipped if it would end after T or
   overlap the previous one.
9. Write `provenance.recipe = {id, version, params (the full fill), principles, unrendered (fields)}` (ADR-0014,
   Proposed) and `provenance.selection = "src.recipes <id>@<v> language=<l>"`, plus ` ADR-0006 dev-only` when
   `allow_dev` is used (H-0026 F2). Then `src.validate`.

Beats are **proportional windows**, not content-aligned: without a model the compiler does not know where the
"tip" or "turning point" is said. That is the job of a future fill model, which may only choose values (for example
`start_at_s`, `item_count`) and never times.

**Determinism.** Same recipe + fill + words + source gives byte-identical output through `src.recipes.dumps`
(sorted keys, UTF-8, indent 2). The fill is key-sorted, so `--set` order does not matter.

**Result** (`--result`): `{recipe, version, fill, beats, ops, unrendered, advisory, warnings, timeline}`.
Each `unrendered` entry is `{code: "UNRENDERED", field, feature, reason}`. On a coded failure the CLI prints the
UNRENDERED list as JSON on stdout as well.

## 4. Error codes (`RecipeError.code`; CLI exit 2)
| code | when |
|---|---|
| `E_RECIPE_SCHEMA` | recipe fails `recipe.schema.json` (strict integers) |
| `E_RECIPE_SHARES` | beat shares do not sum to 100 |
| `E_RECIPE_REF` | zoom / per_beat / overlay / wpm names an unknown beat; duplicate beat id |
| `E_RECIPE_PARAM` | a param default has the wrong type or is out of range; a param the recipe needs is missing |
| `E_RECIPE_UNKNOWN` | unknown recipe id or missing recipe file |
| `E_PARAM_UNKNOWN` / `E_PARAM_TYPE` / `E_PARAM_RANGE` | fill errors (also `start_at_s` past the source end) |
| `E_RECIPE_SOURCE` | speech required but source < 30 words/min, speech forbidden but >= 30, source shorter than `length_s.min` after the hook steps, `--images` directory empty |
| `E_RECIPE_SOURCE_KIND` | `photos_to_video` (image sources cannot be expressed in timeline v0 or rendered), or a video recipe given images |
| `E_RECIPE_INGEST` | no cached ingest for the video (CLI) |
| `E_RECIPE_OP` | an edit op refused (wraps the `OpError` code) |
| `E_RECIPE_INVALID` | the final timeline failed `src.validate` (for example a `quarantine/dev/` source without `--allow-dev`) |

## 5. Example (R01, abridged)
```json
{"id": "R01", "version": 1, "name": "One-tip talking head", "tier": "A",
 "source": {"speech": "required"},
 "beats": [{"id": "hook", "label": "Hook claim", "share_pct": 10}, {"id": "tip", "label": "Tip body", "share_pct": 65},
           {"id": "recap", "label": "Recap", "share_pct": 15}, {"id": "cta", "label": "CTA line", "share_pct": 10}],
 "hook": {"rule": "...", "cut_greeting": true, "lead_in_ms": 300},
 "pacing": {"duration_mode": "tighten", "wpm": {"hook": [170, 190]}},
 "captions": {"preset": {"param": "caption_look"}, "per_beat": {"hook": "hook"}},
 "zoom": {"placement": "rhythm", "duration_ms": 800},
 "sound": {"available": "speech", "music_bed": {"kind": "soft", "gain_db": [-22, -18], "duck_under_speech": true}},
 "params": {"length_s": {"type": "int", "default": 35, "min": 20, "max": 60}, "caption_look": {"type": "enum", "default": "clean", "values": ["clean", "bold_box", "hook"]}},
 "principles": ["P-HOOK-3S", "P-MUTED-CAPTION", "P-ZOOM-RHYTHM"]}
```
Compiles to ops `delete_words` (greeting) → `trim` (lead-in) → `delete_words` (fillers) → `set_duration(35000)`
→ `set_caption_style(clean)` → `add_zoom` x N. UNRENDERED: `sound.music_bed`, `captions.per_beat`,
`needs[]=keyword_highlight`.

## 6. Recipe status (H-0028 tiers; the Founder replaced R11 with `photos_to_video`)
| recipe | compiles today | UNRENDERED fields |
|---|---|---|
| R01, R03, R07, R08 (A) | yes | optional extras only (music, per-beat style, keyword highlight, lower third) |
| R02, R04, R05, R06, R09, R10 (B) | yes, degraded | each required missing piece is listed by field |
| R12 (B) | yes, **compile only**: `golden_set: false` until the EXP-008 per-script size fix passes | `needs[]=per_script_size` |
| photos_to_video (C) | **no**: designed `E_RECIPE_SOURCE_KIND` | image_source, pan_zoom, transitions, music_bed, 2 overlays |

## 7. Backlog (not built in H-0029)
Ranked by recipes unblocked (H-0028 section 5):
1. **Text overlay** (ASS, EXP-008 font pair): R02 R03 R04 R05 R06 R10 photos_to_video. H-0029 stretch, not done.
2. **Still-image sources + deterministic pan/zoom** (ffmpeg `-loop 1 -t`, `zoompan`): photos_to_video. Needs a
   timeline source type (schema change, ADR).
3. **Per-beat caption style** (an op that styles a caption range): R01 R02 R07 R09.
4. **Reorder / splice op**: R04 R09.
5. **Music bed + ducking**: blocked on a rights-cleared library (DATA_RIGHTS) as well as the renderer.
6. Per-script size factor (EXP-008 O1): R12. Then transitions, SFX, b-roll, stickers, speed ramp, zoom ease and
   beat sync.
