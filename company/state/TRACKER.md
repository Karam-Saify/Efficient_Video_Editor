# TRACKER: single source of truth for work items
<!-- Founder instruction 2026-11-23. Edit rows by hand; then run `python tools/tracker.py` to regenerate the stats.
     CI runs `python tools/tracker.py --check`. It fails on a Done row without evidence, a missing evidence path,
     a bad status, a duplicate ID, or stale stats.
     Status: Todo | Doing | Blocked | Done | Dropped. Evidence: backticked repo paths, commit hashes, or a short note.
     STATE.md stays the session snapshot (milestone, blockers, key numbers); the work items live here.
     BUILD_CHECKLIST.md is replaced by this file (it never existed in this repo; nothing to archive). -->

<!-- stats:start -->
**38 items · 11 done (29 %)** · Todo 23 · Doing 0 · Blocked 4 · Done 11 · Dropped 0  
Open by owner: assurance-lead 1, engineering-lead 9, founder 12, operator 2, product-lead 1, research-lead 2
<!-- stats:end -->

## Engine and product
| ID | Item | Owner | Status | Evidence | Updated |
|---|---|---|---|---|---|
| T-001 | Build mode recorded (ADR-0006); dev clips in quarantine/dev | operator | Done | `company/decisions/ADR-0006-build-mode.md` | 2026-11-23 |
| T-002 | Honest engine + multilingual ingest (H-0024) | engineering-lead | Done | `company/handoffs/H-0024-return.md`, `docs/CAPABILITIES.md` | 2026-11-23 |
| T-003 | Edit ops + undo + end-to-end demo (H-0025) | engineering-lead | Done | `company/handoffs/H-0025-return.md`, `examples/ops` | 2026-11-23 |
| T-004 | Week 1 A: cost baseline + `src/cost` (H-0027, H-0032) | engineering-lead | Done | `docs/COST_BASELINE.md`, `company/handoffs/H-0032-return.md` | 2026-11-23 |
| T-005 | Week 1 B: device bench page (H-0030) | engineering-lead | Done | `bench/README.md`, `company/handoffs/H-0030-return.md` | 2026-11-23 |
| T-006 | Week 1 C: recipe language + 12 recipes + compiler, 33/36 compile (H-0028, H-0029) | engineering-lead | Done | `docs/RECIPE_LANGUAGE.md`, `company/handoffs/H-0029-return.md` | 2026-11-23 |
| T-007 | Week 1 D: prompt form, fake doors, EXP-011, AdKraft (H-0031) | product-lead | Done | `company/handoffs/H-0031-return.md` | 2026-11-23 |
| T-008 | `photos_to_video`: still-image sources in the renderer | engineering-lead | Todo | — | 2026-11-23 |
| T-009 | Text overlay (non-spoken text; unblocks 8 recipes) | engineering-lead | Todo | — | 2026-11-23 |
| T-010 | Caption presets `clean`/`bold_box` sit at 83 % height, bound is 72 % | engineering-lead | Todo | `company/handoffs/H-0029-return.md` | 2026-11-23 |
| T-011 | H-0026 F1: render not byte-deterministic (standard needs Founder) | engineering-lead | Todo | `company/handoffs/H-0026-review.md` | 2026-11-23 |
| T-012 | H-0026 F4–F8: malformed ops error, emoji/length validation, tail snap, strip metadata | engineering-lead | Todo | `company/handoffs/H-0026-review.md` | 2026-11-23 |
| T-013 | H-0026 F3: no-word gaps are not silence (audio-energy check) | engineering-lead | Todo | `company/handoffs/H-0026-review.md` | 2026-11-23 |
| T-014 | H-0033 S3 F6–F13 (price citations, units, caption collision, bench ASR "ok", SRI, door wording, error order, string params) | engineering-lead | Todo | `company/handoffs/H-0033-review.md` | 2026-11-23 |
| T-015 | Fake-door waitlist line names the form host (H-0034 leftover) | product-lead | Todo | `company/handoffs/H-0034-return.md` | 2026-11-23 |
| T-016 | H-0020 hook gaps (no return; WIP tests parked) | engineering-lead | Blocked | `company/handoffs/H-0020-wip/test_protect_hook.py` | 2026-11-23 |
| T-017 | PR `t2/install-company-os` → `main` | operator | Todo | — | 2026-11-23 |
| T-018 | Tracker + `tools/tracker.py --check` in CI | operator | Done | `tools/tracker.py`, `.github/workflows/ci.yml`, `tests/unit/test_tracker.py` | 2026-11-23 |

## ASR (Founder S1 correction)
| ID | Item | Owner | Status | Evidence | Updated |
|---|---|---|---|---|---|
| T-020 | Intake Download (9), (10); drop duplicate (4); ADR-0022 | operator | Done | `company/decisions/ADR-0022-founder-spot-check-data-claims.md`, `company/positions/05-assurance/DATA_RIGHTS.md` | 2026-11-23 |
| T-021 | Fill `quarantine/dev/LABELS.csv` (ground truth) | founder | Todo | — | 2026-11-23 |
| T-022 | EXP-012 ASR diagnostic (multi-window LID, VAD, Demucs, turbo vs v3, auto vs ar) | research-lead | Blocked | waits for T-021 | 2026-11-23 |
| T-023 | Pipeline ASR fixes after Founder verdict (per-segment LID, ASR_SUSPICIOUS, vocal separation, ASR config in manifest) | engineering-lead | Blocked | waits for T-022 | 2026-11-23 |
| T-024 | EXP-013 Common Voice Arabic baseline | research-lead | Blocked | `company/handoffs/H-0036-return.md` (Founder must download via MDC account) | 2026-11-23 |
| T-025 | Re-upload the ~4 clips that never arrived | founder | Todo | — | 2026-11-23 |

## Founding Creator pilot (ADR-0023, days 1–10)
| ID | Item | Owner | Status | Evidence | Updated |
|---|---|---|---|---|---|
| T-030 | Consent kit + intake/feedback forms + eval-set licences (H-0034) | assurance-lead | Done | `company/positions/05-assurance/CONSENT_KIT.md`, `company/handoffs/H-0034-return.md` | 2026-11-23 |
| T-031 | Annotation schema + Footage Intelligence v0 storyboard (H-0035) | engineering-lead | Done | `schemas/annotation.schema.json`, `docs/FOOTAGE_INTELLIGENCE.md`, `company/handoffs/H-0035-return.md` | 2026-11-23 |
| T-032 | Daily Assurance review of H-0035 (ADR-0025, `t_start_ms`, ADR-0014) | assurance-lead | Todo | — | 2026-11-23 |
| T-033 | Claude account model-training setting confirmed OFF | founder | Todo | — | 2026-11-23 |
| T-034 | Sign ADR-0024 (90-day retention) | founder | Todo | `company/decisions/INDEX.md` | 2026-11-23 |
| T-035 | SHAMS route: permission / lawyer / drop | founder | Todo | `company/handoffs/H-0034-return.md` | 2026-11-23 |
| T-036 | Partners recruited with signed consent: 0/5 (Founder's store = #1) | founder | Todo | — | 2026-11-23 |
| T-037 | Source videos with rights: 0/20–30 | founder | Todo | — | 2026-11-23 |
| T-038 | Jobs delivered (2 versions each): 0/5 | operator | Todo | — | 2026-11-23 |
| T-039 | Bench run on 3 phones (incl. lowest-end) | founder | Todo | `bench/README.md` | 2026-11-23 |

## Founder decisions pending
| ID | Item | Owner | Status | Evidence | Updated |
|---|---|---|---|---|---|
| T-040 | ADR-0014 `provenance.recipe` (Assurance: accept with F13) and ADR-0025 annotation schema | founder | Todo | `company/decisions/INDEX.md` | 2026-11-23 |
| T-041 | Budget failure rate and miss rate for the cost ceiling | founder | Todo | `docs/COST_BASELINE.md` | 2026-11-23 |
| T-042 | Pricing-door anchors; form tool | founder | Todo | `company/positions/01-product/FAKE_DOOR_COPY.md` | 2026-11-23 |
| T-043 | Session-2 carryovers: EXP-008 co-verdict, sign ADR-0001 | founder | Todo | — | 2026-11-23 |
