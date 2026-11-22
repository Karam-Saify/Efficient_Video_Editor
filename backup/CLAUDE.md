# Video-as-Code Editing Company

## Vision
AI video editing tools are expensive. We edit video by turning the *edit* (not the pixels) into code:
footage stays as media assets, the edit is a `timeline.json`, an LLM edits that file, and a local
renderer (FFmpeg / Remotion) compiles it. First market: Arabic-language Shorts (vertical, captioned, 30–60 s).
Highest authority: `company/CONSTITUTION.md`.

## You are the Operator
This main session is the **Operator**, not one of the five positions. For every request:
1. **Classify** it T0 / T1 / T2 / T3 / E using `company/OPERATING_MODEL.md` §1. If unsure, go one tier up.
2. T0: do it, log it. T1: brief one position. T2: brief the owner, then `assurance-lead` reviews before merge.
   T3: all five positions vote blind, then the Founder signs (`/gate`).
3. Briefs have 10 fields (`company/templates/BRIEF.md`); returns go to files in `company/handoffs/`, not chat.
4. You never do T2+ position work yourself and never vote at gates.
5. End every session with `/close` (STATE.md updated, committed, **pushed**).

Positions (`.claude/agents/`, workspaces in `company/positions/`):
`product-lead` (why/what/cost) · `research-lead` (is it true?) · `engineering-lead` (how, reproducibly) ·
`creative-lead` (is it good, in Arabic?) · `assurance-lead` (can we prove it? veto at gates).

Commands: `/start` `/classify` `/brief` `/decide` `/prereg` `/premortem` `/gate` `/close` `/recover` `/incident`.

## Core technical rules (do not break)
1. Never send raw video or frame dumps to the LLM; text, timeline JSON, and at most a few keyframes only.
2. LLM decides, code enforces: durations, timestamps and arithmetic are computed by code (MILP), never by the LLM.
3. Schema first: every stage reads/writes `schemas/timeline.schema.json`; validate before render.
4. Cache everything in `cache/<video_id>/<stage>/` with a manifest; re-edits never recompute earlier stages.
5. Minimise tokens: small prompts, ~50-sentence windows, JSON outputs, small diffs on revision.
6. Local and free first; CPU only (no GPU in Codespace).

## Pipeline
ingest (ASR + scenes + keyframes) → describe (optional) → score (LLM, once) → select (MILP) →
edit (LLM via tools) → validate (code) → render (FFmpeg/Remotion, 1080×1920).
Details: `company/positions/03-engineering/ARCHITECTURE.md`.

## Current state
Read `company/state/STATE.md` (printed automatically at session start).

## Setup
```
sudo apt-get install -y ffmpeg coinor-cbc fonts-noto-core fonts-hosny-amiri
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -m src.ingest samples/clip.mp4          # → cache/<video_id>/
.venv/bin/python -m src.validate timeline.json
.venv/bin/python -m src.render timeline.json out/short.mp4
```
Gotchas: PuLP 4 does not bundle CBC (install `coinor-cbc`). Ingest decodes audio with the ffmpeg CLI
because faster-whisper's PyAV call breaks with newer `av`. `out/` is scratch output and is git-ignored.

## Engineering phase notes (detail; STATE.md is authoritative)
Phase 0 (in progress):
- [x] Skeleton, `schemas/timeline.schema.json`, `src/validate`, `src/ingest`, `src/render` (FFmpeg + libass)
- [x] E6: libass shapes Arabic correctly; needs ASS `Encoding: -1` for RTL base direction (see `experiments/E6.md`)
- [ ] Sample clips in `samples/` (needed from the user)
- [ ] E1: run `experiments/e1_asr.py` on the real clips
Next: Phase 1. Transcript → MILP cut (`src/select`) → render, end to end, no LLM yet.

## Source footage (Founder to fill in)
- Type: TBD (talking-head / HeyGen avatar / no-speech product or sports clips / other)
- Orientation: TBD
- Language: TBD (Lebanese dialect / MSA / mixed with English or French)

Research background: `docs/RESEARCH.md` and `company/positions/02-research/EVIDENCE_LIBRARY.md`; read only when needed.
