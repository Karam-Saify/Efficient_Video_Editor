# ADR-0004: Timeline v0 `sources[].has_audio` (optional boolean, default true)
- **Status:** Proposed
- **Date:** 2026-11-22 · **Tier:** T2 · **Door:** two-way (an optional field; absent means today's behaviour)
- **Decider:** Founder (via Operator) · **Recommender:** engineering-lead · **Consulted:** assurance-lead (H-0009 review N2), creative-lead (informed via H-0017 brief field 10: no-speech product/sports clips are a candidate footage type) · **Input:** `company/handoffs/H-0004-review.md` F2, `company/handoffs/H-0009-review.md` N2

## Context
The renderer maps each clip's audio from its source (`[n:a]`). A source with no audio stream (no-speech
product or sports clips, a muted screen recording) makes ffmpeg fail with `Stream specifier ':a' ... matches
no streams` (H-0004 F2). H-0009 added `sources[].has_audio` to `schemas/timeline.schema.json`; when false, the
renderer uses generated silence (stereo, the clip's duration) for that source's clips. ARCHITECTURE.md
requires an ADR for any schema change; this records it after the fact (review N2).

## Options considered
| Option | Pros | Cons |
|---|---|---|
| A. Optional `has_audio` boolean on each source, default true, set by code from ffprobe | Explicit, validated, cheap; the renderer stays a pure function of the timeline; old timelines stay valid | Field must be filled by ingest; absent on a silent source still fails at render |
| B. Renderer probes every source with ffprobe at render time | No schema field; never stale | Hidden input to render (timeline no longer fully describes the output); extra probe per render |
| C. Always mix a silence bed under every clip | No field, no probe | Masks a missing audio track on a speech source (a real defect would pass silently) |

## Decision (proposed)
Option A. The value is metadata measured by code (ffprobe in ingest), never chosen by the LLM. Until ingest
fills it (next ingest brief, Done-when: "write `has_audio` from `probe()`"), it is set by hand in test
timelines only.

## Consequences
+ Silent sources render (H-0009 review Part F: exit 0, silent stereo track). + Backward compatible.
− Residual: field absent on a silent source = validate 0, render 1, until ingest fills it (review N2).
− A later "required" change would be a schema version bump.

## Reversal plan
Remove the property from the schema, the silence branch in `src/render`, and its test; under 15 minutes.
No stored data depends on it (no ingest output writes it yet).

## Dissent
None recorded.
