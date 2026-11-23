# BRIEF H-0035 (pilot · annotation schema + Footage Intelligence v0)
- **To:** engineering-lead · **Tier / Milestone:** T2 (new schema + an unfrozen stage; daily Assurance review) / pilot day 1–2 · **Date:** 2026-11-23

1. **Objective (with why):** Give the pilot a data spine and its first partner-facing tool. Each partner clip becomes a storyboard the partner corrects, and the corrections become `human_verified` labels. This is the only evidence that counts under ADR-0022 and ADR-0023.
2. **Inputs:** `company/decisions/ADR-0016`, `ADR-0022`, `ADR-0023`; `company/handoffs/H-0034-return.md` + `company/positions/05-assurance/PARTNER_FEEDBACK_FORM.md` (field mapping); `src/ingest/`, `src/describe/` (unfrozen: cheap footage understanding), `src/common.py`, `src/cost/`, `schemas/timeline.schema.json`; `quarantine/dev/` (dev testing only).
3. **Constraints:**
   - **Zero cost (ADR-0023):** local, open-source tools only (faster-whisper, PySceneDetect, ffmpeg). No paid API calls. Scene descriptions are written *inside a Claude Code session* by reading at most a few keyframes (CLAUDE.md rule 1). The pipeline therefore writes a `descriptions.todo.json`, and a session fills it. Build that hand-off; do not call an API.
   - `schemas/annotation.schema.json` covers each source (scenes, keyframes, transcript with language per segment, audio signals, creative roles hook/product_intro/demo/proof/cta, `label_origin` machine|human_verified **on every label**, `rights_id`) and each job (brief, audience, platform, objective, the partner's published version, likes/dislikes, edits delivered, partner choice, corrections, would_publish, would_pay). Job fields must match Assurance's mapping 1:1. Write an ADR (Proposed, next free number).
   - Audio signals: loudness (ebur128), speech coverage (VAD), music/energy proxy, all with ffmpeg/numpy. Low words/min → `ASR_SUSPICIOUS`, never "no speech" (Founder rule from the S1 correction).
   - Storyboard: a static, self-contained HTML file per video, written to `cache/<id>/storyboard/index.html`. It shows keyframes + scene descriptions + suggested roles, with editable fields and an **Export corrections** button (JSON download). It works offline and loads nothing from the network. `python -m src.describe import-corrections <video> <json>` stores corrections as `human_verified`, and keeps the machine label alongside for diffing.
   - Suggested roles are deterministic rules in v0 (position, speech/no speech, scene length), marked `machine`.
   - Partner data and dev-clip derivatives live only in `cache/` (git-ignored). Committed fixtures use **synthetic** media only (ffmpeg testsrc).
   - Commit each finished, test-green unit (~every 5 min), but do not push.
4. **Output:** schema + ADR + `src/describe` (annotate, storyboard, import-corrections) + tests + a short `docs/FOOTAGE_INTELLIGENCE.md` (how a concierge session runs it end to end). Return at `company/handoffs/H-0035-return.md`.
5. **Done when:**
   - [ ] On 2 dev clips: annotate → storyboard HTML → you fill `descriptions.todo.json` for ≤ 4 keyframes per clip → a simulated correction JSON → import → the record validates, with both machine and human_verified labels. Give the paths (in `cache/`, not committed).
   - [ ] Schema tests: valid and invalid fixtures; label_origin required everywhere; rights_id required.
   - [ ] The storyboard makes no network requests (prove it with a grep for http in the generated file, or a headless check).
   - [ ] Suite + ruff green.
6. **Out of scope:** EXP-012 ASR fixes (they wait for the Founder's LABELS.csv verdict); paid APIs; recipes/compiler changes; hosting.
7. **Effort budget:** max 60 tool calls · 2 retries.
8. **Escalate if:** the H-0034 field mapping is missing or contradicts ADR-0023; a needed tool is not installed and not free.
9. **Termination condition:** committed, return written.
10. **Consulted:** assurance-lead (field mapping, H-0034); the daily review.
