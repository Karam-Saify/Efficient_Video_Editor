# Timeline v0 capabilities

Generated from `src/capabilities.py` by `python -m src.capabilities --write`; `tests/unit/test_capabilities.py` fails if this file drifts. Do not edit by hand.

A field with kind `render` and rendered `n` is rejected by `src.validate` with `UNSUPPORTED_FIELD` and its JSON path, so a timeline never carries an instruction the renderer silently ignores. `meta` fields are checked but are not render instructions.

| field | kind | validated | rendered | notes |
|---|---|---|---|---|
| `version` | meta | y | n | const "0.1"; document version, not a render input |
| `canvas.width` | render | y | y | output width (scale/crop target) |
| `canvas.height` | render | y | y | output height |
| `canvas.fps` | render | y | y | output frame rate; also the one-frame tolerance of E_DURATION |
| `target_duration_ms` | meta | y | n | checked against the sum of clip lengths (E_DURATION) |
| `sources[].id` | render | y | y | key that clips reference (E_DUPLICATE_ID, E_SOURCE_MISSING) |
| `sources[].path` | render | y | y | ffmpeg input; repo-relative, protected roots refused (E_SOURCE_PATH, E_SOURCE_MISSING) |
| `sources[].duration_ms` | meta | y | n | bounds clip out_ms (E_RANGE) |
| `sources[].sha256` | meta | y | n | integrity check when given (E_SOURCE_HASH) |
| `sources[].has_audio` | render | y | y | false: that source's clips get silence (anullsrc) |
| `tracks.video[].id` | meta | y | n | unique id (E_DUPLICATE_ID); effect target key |
| `tracks.video[].source` | render | y | y | which input the clip trims |
| `tracks.video[].in_ms` | render | y | y | trim start, source time (E_RANGE) |
| `tracks.video[].out_ms` | render | y | y | trim end, source time (E_RANGE, E_OVERLAP) |
| `tracks.video[].crop` = `"center"` | render | y | y | centre crop to the canvas |
| `tracks.video[].crop` = `"auto_face"` | render | y | n | no face tracking yet: UNSUPPORTED_FIELD |
| `tracks.captions[].id` | meta | y | n | unique id (E_DUPLICATE_ID) |
| `tracks.captions[].text` | render | y | y | burned in via libass; EXP-008 font pair (Noto Sans Arabic + Noto Sans, `\fn` run tags); a character outside both fonts' ranges fails the render |
| `tracks.captions[].start_ms` | render | y | y | output time (E_CAPTION_BOUNDS) |
| `tracks.captions[].end_ms` | render | y | y | output time (E_CAPTION_BOUNDS) |
| `tracks.captions[].style` | render | y | y | preset from src/presets.py: clean (default), bold_box, hook; one ASS style each, EXP-008 pair, Regular weight, Encoding -1; any other name: UNSUPPORTED_FIELD |
| `tracks.captions[].dir` | render | y | y | libass auto base direction (ASS Encoding -1) follows the first strong character; a `dir` that disagrees with it cannot be rendered: UNSUPPORTED_FIELD |
| `tracks.effects[].type` | render | y | y | zoom = punch-in on the output: centre crop by 1/scale, scaled back to the canvas, instant in/out, under the captions (overlay with `enable`) |
| `tracks.effects[].target` | meta | y | n | must be a clip id (E_EFFECT_TARGET); the clip that contains at_ms, bookkeeping only (the zoom applies to output time) |
| `tracks.effects[].at_ms` | render | y | y | output time, zoom start (E_EFFECT_BOUNDS) |
| `tracks.effects[].duration_ms` | render | y | y | zoom length; window must end by the timeline end (E_EFFECT_BOUNDS) |
| `tracks.effects[].scale` | render | y | y | 1.0 to 2.0, default 1.2 (src/presets.py); outside: UNSUPPORTED_FIELD (no zoom-out) |
| `tracks.audio[].source` | render | y | n | extra audio tracks are not mixed: UNSUPPORTED_FIELD |
| `tracks.audio[].gain_db` | render | y | n | not rendered |
| `tracks.audio[].duck_under_speech` | render | y | n | not rendered |
| `provenance.selection` | meta | y | n | free text; type-checked only |
| `provenance.prompt_versions` | meta | y | n | object; type-checked only |
| `provenance.model_ids` | meta | y | n | object; type-checked only |
