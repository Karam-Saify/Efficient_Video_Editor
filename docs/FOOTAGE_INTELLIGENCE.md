# Footage Intelligence v0 (H-0035, ADR-0025)
A concierge session turns one partner clip into an **annotation record** (`schemas/annotation.schema.json`) and an
**offline storyboard** the partner corrects. The corrections become `human_verified` labels (ADR-0022, ADR-0023).
Cost: $0. No API is called; the scene descriptions are written by the Claude Code session itself, from at most
4 keyframes per clip (CLAUDE.md rule 1, I-3). Every time and duration is computed by code (I-4).

## Before you start (gates, not suggestions)
- The clip has a DATA_RIGHTS row (`RR-P<partner>-<n>`, PARTNER_INTAKE_FORM C10) and the partner signed CK-v0.1.
- The Founder has confirmed the Claude plan's training setting is off (H-0034 F3) before any partner keyframe
  or transcript reaches the session.
- Partner media and everything derived from it stay in `cache/` (git-ignored). Never commit them.

## Steps (one clip)
```
V="partner/P001/clip01.mp4"                      # wherever the Operator stored it, outside git
.venv/bin/python -m src.describe annotate "$V" --rights-id RR-P001-01   # ASR + scenes + keyframes + audio + roles
```
Prints three paths under `cache/<video_id>/`: `describe/annotation.json` (machine labels only),
`describe/descriptions.todo.json` (at most 4 keyframes, spread first to last) and `storyboard/index.html`.
ASR, scenes and keyframes are cached and shared with `src.ingest`; a rerun with a cached transcript takes ~1 s.
`annotate` refuses to overwrite a record that already holds descriptions or corrections (`--force` to override).

**Describe (in the session).** Read only the image files listed in `items[].path` (tiling those same 4 into one
image is fine). Write one plain sentence per item into `description` (≤ 300 chars, what is visible, no times),
set `describer` to `claude-code-session <model id>`, then:
```
.venv/bin/python -m src.describe apply-descriptions "$V" cache/<video_id>/describe/descriptions.todo.json
```
More than 4 items, a keyframe hash that does not match, or no `describer` fails loudly. Descriptions are `machine`
labels: a model wrote them, not the partner.

**Partner review.** Send `cache/<video_id>/storyboard/index.html` (one file, ~200 KB, opens offline in any
browser, makes no network request: CSP `default-src 'none'`). The partner fixes descriptions, roles and transcript
lines, or ticks *Correct*, then presses **Export corrections** and sends back `corrections-<video_id>.json`.

**Import.**
```
.venv/bin/python -m src.describe import-corrections "$V" corrections-<video_id>.json
.venv/bin/python -m src.describe validate cache/<video_id>/describe/annotation.json
```
Every edited or confirmed field becomes `human_verified`, and `machine_value` keeps what the machine said. The
correction file is kept verbatim in `describe/corrections/<sha256>.json` and listed in `provenance.corrections`.
A file exported from an older storyboard is rejected (the record hash changed): regenerate it and ask again.

## What the machine labels mean
- **Roles (`roles-v0`)**: first scene `hook`, last `cta`, second `product_intro` (4+ scenes), middle scenes
  `proof` if VAD speech covers half of them, `demo` otherwise, `other` if under 1 s. Suggestions only.
- **Audio**: integrated loudness and LRA (ffmpeg `ebur128`), `speech_ratio` (silero VAD bundled with
  faster-whisper), `energy_db_1s`, and `nonspeech_sound_ratio` (sound that is not speech: a music/ambience proxy).
- **Flags**: `ASR_SUSPICIOUS` (VAD finds speech but the transcript has < 60 words per speech-minute),
  `LOW_VAD_SPEECH`, `SILENT_TRACK`, `NO_AUDIO_STREAM`. There is no "no speech" flag: an empty transcript is a
  possible ASR failure, and the storyboard says so.

## Checks
`experiments/storyboard_offline_check.mjs` opens a storyboard headless from `file://`, fails on any request that
is not `file:`, `data:` or `blob:`, edits one scene and saves the real Export download (Playwright 1.57.0, set up as
in `bench/README.md`). Tests: `tests/unit/test_annotation_schema.py`, `test_describe_rules.py`,
`test_describe_pipeline.py` (synthetic ffmpeg media only).
