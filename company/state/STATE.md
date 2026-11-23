# STATE: single source of truth
<!-- The Operator updates this at the end of every session (/close). Keep it under 60 lines.
     If a HALT line exists at the very top, ALL work stops until the Founder clears it. -->

**Last updated:** 2026-11-23 (evening) · **By:** Operator · **Session:** 3 (continued; waiting on Founder LABELS.csv)

**Work items live in `company/state/TRACKER.md`** (single source of truth; `python tools/tracker.py --check` runs in CI). This file is the session snapshot.

## Current milestone
**M0 → M1 in BUILD MODE** (ADR-0006, 2026-11-23 → review 2026-12-07): fast lane for non-engine work; ONE Assurance review per day on the end-to-end demo; product/research/creative on sonnet; no parallel agents; no new governance docs; scraper/trend tooling postponed.

## Done this session
- ADR-0006 build mode (Founder). TikTok MP4s moved to `quarantine/dev/` (git-ignored), INTERNAL DEV TESTING ONLY; RR-006..009 amended, RR-018..022 added
- H-0024 (eng): `experiments/dev_catalog.py` → `quarantine/dev/dev_manifest.csv`; stubs exit `NOT_IMPLEMENTED`; validator `UNSUPPORTED_FIELD`; `docs/CAPABILITIES.md` generated + drift test; language auto-detect; transcript → caption track (dir by first strong char); EXP-008 font pair in renderer
- H-0025 (eng): `src/edit/ops.py` (trim, delete_words, set_caption_style, add_zoom, set_duration) + history/undo; 3 caption presets + zoom rendered; `python -m src.demo`; `examples/ops/*.json` (3); demo on 3 English clips + 1 weak Arabic run, all within 1 frame
- H-0026 (assurance): **ACCEPT WITH FINDINGS (S1 0 · S2 1 · S3 7)**; `allow_dev` (D1) accepted with condition F2
- H-0020 WIP tests (59 red) parked in `company/handoffs/H-0020-wip/` (not collected)

## Since the session-3 close (afternoon/evening)
- ADR-0007..0013, 0015..0022 (Founder); ADR-0014 Proposed (Assurance: accept with F13)
- Week 1 A–D done: H-0027/H-0032 cost (`src/cost`), H-0028/H-0029 recipes (33/36; photos_to_video gap), H-0030 bench, H-0031 product
- H-0033 review: ACCEPT WITH FINDINGS (S1 0 · S2 5 · S3 8). Details in `company/reports/2026-11-23/README.md` Part 3
- **Founder S1:** catalog language labels are wrong (ASR fails on Arabic). ADR-0022. 10 clips in quarantine/dev; `LABELS.csv` awaiting Founder
- **ADR-0023 Founding Creator pilot** (zero-cost): H-0034 consent kit + licences DONE (SHAMS not usable, escalated; ADR-0024 retention Proposed); H-0035 schema + storyboard RUNNING; H-0036 Common Voice baseline queued. Daily via `/daily`

## Next (ordered)
0. **Founder:** training setting OFF on the Claude account; sign ADR-0024; SHAMS route; partner #1 intake
0a. **Founder fills `quarantine/dev/LABELS.csv`** → EXP-012 ASR diagnostic (prereg, Demucs = new dep T2) → pipeline fixes after the Founder verdict
0b. H-0033 S2 fixes F1–F3 (consent, backlog, rights warranty) and F5 (RR rows for bench assets)
1. Tomorrow's goal: fix H-0026 F1 (MP4 render not byte-deterministic: pin x264 threads/settings, or Founder-approved frame/PSNR equality), F2 (dev-only marker on outputs), F4 (coded error for malformed ops.json), F5/F6 (validator ↔ renderer caption text and length bounds)
2. First Arabic speech demo run, once the Founder supplies a clip
3. F3: set_duration/delete_words must not cut music/B-roll as "silence" (audio-energy gap check, with creative-lead)
4. Still open from session 2: H-0020 hook gaps (no return); PR `t2/install-company-os` → `main`; EXP-008 co-verdict; MVP pivot prompt

## Blockers
- **ASR fails on Arabic** (Founder S1): the catalog's "6 en, 4 no speech" labels are wrong. Ground truth = `quarantine/dev/LABELS.csv` (Founder to fill); EXP-012 diagnoses the failure
- Rights for all footage still UNVERIFIED (dev-only under ADR-0006). F8: outputs carry the platform video ID in metadata, and zoom crops the watermark. Fine for internal use, a blocker for any publish path

## Open decisions (awaiting Founder)
- Drop the duplicate `Download (4).mp4` (identical to (2))?
- Determinism standard (F1): byte-identical MP4, or decoded-frame / PSNR floor?
- Caption dir for mostly-Arabic lines starting with a Latin word (needs an EXP-008 amendment); Latin/Arabic size ratio (EXP-010)
- From session 2: EXP-008 co-verdict · PR/FAQ chat-editor scope (T3) · sign ADR-0001

## Last gate
- None yet

## Key numbers
| Metric | Value | Target |
|---|---|---|
| Tests | 266 pass, 8 skip; ruff clean | green |
| Demo duration error | 0 / 12 / 0 ms (3 runs), 33 ms weak run | ≤ 1 frame |
| Demo wall time | 35–152 s per 17–36 s Short (CPU, 2 cores) | set at M1 |
| Tokens today (est.) | ~0.55 M (subagents 417k + Operator ~130k) | set at M3 |
| LLM tokens per Short | 0 (no LLM in the loop yet) | set at M3 |
