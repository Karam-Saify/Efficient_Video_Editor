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
  "sources": [{"id": "src1", "path": "samples/x.mp4", "duration_ms": 600000, "sha256": "..."}],
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

## LLM tool interface for stage 5 (from EditDuet, extended)
`search(query) → top-5 segments` · `add_clip(segment_id, in_ms, out_ms, index)` · `remove_clip(index)` ·
`move_clip(from, to)` · `set_caption(...)` · `add_effect(...)` · `done()`.
The LLM never writes raw JSON for the timeline; it calls tools, and the code applies them and validates after each call.
