# Architecture (v0, M0)
Changes to this file that alter a stage boundary or the schema are T2 and need an ADR.

## Pipeline stages and contracts
| # | Stage | Input | Output (in `cache/<video_id>/`) | LLM? | Deterministic? |
|---|---|---|---|---|---|
| 1 | `ingest` | source video | `ingest/transcript.json` (words + timestamps + speaker), `ingest/scenes.json`, `ingest/keyframes/*.jpg`, `ingest/audio_features.json` (silence, beats) | No (local ASR) | Yes, pinned model + int8 |
| 2 | `describe` (optional, EXP-002) | keyframes | `describe/scenes_text.json` | Small local VLM | Yes, fixed seed |
| 3 | `score` | transcript + scenes_text | `score/rule_object.json`, `score/scores.json` | Yes (Claude) | No → cached once, versioned prompt |
| 4 | `select` | scores + target duration | `select/selection.json` | No (PuLP/CBC MILP) | Yes |
| 5 | `edit` | selection + style + instruction | `edit/timeline.json` | Yes (Claude, tools) | No → validated |
| 6 | `validate` | timeline.json + sources | `validate/report.json` | No | Yes |
| 7 | `render` | validated timeline | `render/out.mp4` + `render/frames_check/*.png` | No (FFmpeg / Remotion) | Yes |

## Timeline schema v0 (to be formalised in `schemas/timeline.schema.json`)
```json
{
  "version": "0.1",
  "canvas": {"width": 1080, "height": 1920, "fps": 30},
  "target_duration_ms": 45000,
  "sources": [{"id": "src1", "path": "samples/x.mp4", "duration_ms": 600000, "sha256": "...", "has_audio": true}],
  "tracks": {
    "video": [{"id": "c1", "source": "src1", "in_ms": 42100, "out_ms": 51300, "crop": "auto_face"}],
    "captions": [{"id": "t1", "text": "السعر الحقيقي؟", "start_ms": 0, "end_ms": 1800, "style": "hook", "dir": "rtl"}],
    "effects": [{"type": "zoom", "target": "c1", "at_ms": 6000, "scale": 1.15, "duration_ms": 400}],
    "audio": [{"source": "music1", "gain_db": -18, "duck_under_speech": true}]
  },
  "provenance": {"selection": "select/selection.json", "prompt_versions": {}, "model_ids": {}}
}
```
Validator rules (minimum): every `source` exists and its hash matches · `0 ≤ in_ms < out_ms ≤ duration_ms` ·
no overlapping clips on the video track · captions inside total duration · total duration equals
`target_duration_ms` ± 1 frame · every caption has `dir` · only known effect types.
H-0009 additions: every integer field is a real JSON integer (`2000.0` → `E_SCHEMA`) · source paths are
repo-relative, resolve inside the repo and outside the protected roots (held-out, golden, quarantine) →
`E_SOURCE_PATH`, checked before any file is opened (H-0017: a control character such as NUL, a lone
surrogate, or a path `os` cannot resolve is also `E_SOURCE_PATH`, never an exception) · optional `has_audio`
(default true) makes the renderer use silence for that source; see ADR-0004 (Proposed). Nothing fills it
yet: ingest is a stub that writes no timeline. It is to be filled by ingest from ffprobe: next ingest brief.
Until then a silent source without `has_audio:false` passes validation and fails at render. "No overlapping clips" is enforced as
"no reuse of the same source range" (`E_OVERLAP`); see ADR-0003 (Proposed).

Stage cache known properties (H-0003 review F8, WONTFIX): the input-hash key includes the repo-relative
path (inputs outside the repo are keyed by absolute path), so identical content at another path reruns;
`duration_s` excludes hashing time. Skip key = input hashes + config (incl. `stage_version`) + code version;
a `stub` manifest never satisfies real work; `--out` inside an `--input` dir is an error (H-0009).

## LLM tool interface for stage 5 (from EditDuet, extended)
`search(query) → top-5 segments` · `add_clip(segment_id, in_ms, out_ms, index)` · `remove_clip(index)` ·
`move_clip(from, to)` · `set_caption(...)` · `add_effect(...)` · `done()`.
The LLM never writes raw JSON for the timeline; it calls tools, and the code applies them and validates after each call.
