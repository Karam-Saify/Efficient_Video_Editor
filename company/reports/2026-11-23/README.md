# Daily report: 2026-11-23 (Session 3, build mode day 1)
Operator summary for the Founder. Branch `t2/install-company-os` · everything committed and pushed (`6aaa716` + this report).
Mode: **BUILD MODE** (ADR-0006, until 2026-12-07).

## What works
| Goal | Result | Evidence |
|---|---|---|
| 1. Data intake | 9 TikTok clips moved to `quarantine/dev/` (git-ignored), INTERNAL DEV TESTING ONLY. `experiments/dev_catalog.py` writes `quarantine/dev/dev_manifest.csv` | H-0024, RR-006..009 amended, RR-018..022 |
| 2. Honest engine | Stages that aren't built exit non-zero with `NOT_IMPLEMENTED` and write no manifest. The validator rejects fields the renderer doesn't draw (`UNSUPPORTED_FIELD`). `docs/CAPABILITIES.md` is generated from the same table, and a test checks it for drift | H-0024 |
| 3. Multilingual ingest | Language auto-detected (`--language ar` still overrides). Caption track built from the transcript by code; `dir` comes from the first strong letter. Font pair Noto Sans Arabic + Noto Sans, no fallback | H-0024, `out/h0024/frame_ar_en.png` |
| 4. Edit core | `src/edit/ops.py`: trim, delete_words, set_caption_style, add_zoom, set_duration. Each op is validated and versioned in `cache/<id>/edit/history/`, and can be undone. The renderer draws 3 caption presets (clean, bold_box, hook) and the zoom | H-0025 |
| 5. End-to-end demo | `python -m src.demo --video … --ops … --out out/` with 3 files in `examples/ops/`. All runs are within 1 frame of their planned length | H-0025 |
| 6. Assurance review | **ACCEPT WITH FINDINGS (S1 0 · S2 1 · S3 7)** | `company/handoffs/H-0026-review.md` |

Tests: 266 pass, 8 skip, ruff clean.

## The 3 outputs (git-ignored)
| Output | Clip | Ops | Length (planned → actual) | Language |
|---|---|---|---|---|
| `out/h0025/Download_5__trim_and_style.mp4` | Download (5) | trim_and_style | 17.333 → 17.333 s | en |
| `out/h0025/Download_6__delete_words_zoom.mp4` | Download (6) | delete_words_zoom | 35.755 → 35.767 s | en |
| `out/h0025/Download_3__fit_30s.mp4` | Download (3) | fit_30s (91 s → 30 s) | 30.000 → 30.000 s | en |
| `out/h0025/Download_8__fit_30s.mp4` (weak extra) | Download (8) | fit_30s | 30.000 → 30.033 s | ar (forced; 3 words/min) |

All outputs are 1080×1920 at 30 fps. Wall time is 35–152 s per Short (CPU, 2 cores).

## Review findings (H-0026)
| # | Sev | Finding | Required action |
|---|---|---|---|
| F1 | **S2** | The MP4 render is not byte-deterministic. One timeline rendered 4 times gave 4 different hashes. The differences cannot be seen (PSNR > 50 dB) and audio is identical. H-0025's "byte-identical rerun" was luck | Engineering: find the cause (likely x264/filter threading) and fix it, or restate the claim as frame-identical / PSNR ≥ X. **The Founder signs any threshold** |
| F2 | S3 | `allow_dev` accepted, but dev outputs carry no dev-only marker | Write `ADR-0006 dev-only` into `provenance.selection`. Any future export step must refuse it |
| F3 | S3 | set_duration / delete_words treat "no words" as silence. 30 s of music was cut from the middle of clip (8). Deleting all words leaves 5.5 s with 0 captions and no error | Acceptable for now (speech-led market). Rename to "no-word gaps" and raise an error when no words are left. Audio-energy check with creative-lead. Becomes S2 if non-speech footage comes into scope |
| F4 | S3 | A malformed ops.json crashes with a traceback | Validate the shape of each step and raise a coded `DemoError` |
| F5 | S3 | The validator passes caption text the renderer will refuse (emoji) | `validate()` flags characters outside the font pair, with their JSON path |
| F6 | S3 | No caption length limit (a 2000-character caption validates) | Max characters per caption; creative-lead sets the number |
| F7 | S3 | Run 4 lands exactly on the 1-frame tolerance (30 033 vs 30 000 ms) | Snap the tail to the output frame grid |
| F8 | S3 | Rights: outputs inherit the source's platform video ID in their metadata, and the zoom crops out the source watermark | Renderer passes `-map_metadata -1`. Assurance notes that watermark cropping is dev-only. Fine internally, **a blocker on any publish path** |

Accepted rulings: D1 `allow_dev` (off by default; a symlink, `quarantine/devX` or `..` can't get past it; only `src.demo` sets it). Caption `dir` = first strong letter (Operator, under the medium-term delegation).

## Tokens today (estimate)
About **0.55 M**: subagents 417k (H-0024 144k, H-0025 184k, H-0026 89k) plus the Operator's ~130k. No LLM is in the edit loop yet, so a Short costs 0 tokens.

## Tomorrow's goal
Fix F1, F2, F4, F5/F6, F7 and F8 in one engineering brief. Then the daily Assurance review reruns the 5-render determinism check and the malformed-ops cases. After that, run the first Arabic demo if a clip arrives.

## Needed from the Founder
1. **One Arabic speech clip** (ideally Lebanese). The dev set has 6 English clips, 4 with no speech, and none with real Arabic speech.
2. **The render check standard (F1):** byte-identical MP4s, or matching frames / a PSNR floor?
3. **Drop `Download (4).mp4`?** It is identical to `(2)`.
4. Caption direction for mostly-Arabic lines that start with a Latin word needs an EXP-008 amendment. Until then they display left-to-right.

---

# Part 2 (afternoon): Founder strategy memos + Week 1 tasks
Status at the time of writing: A and C done, B running, D and the daily Assurance review not started.

## Decisions recorded (all Accepted, Founder; no position vote held, dissent may be filed at the M1 gate)
- **Memo 1 (3 stakeholder memos):** ADR-0007 product = Creative Director (one-tap preview cards; chat as fallback) · 0008 recipe-first intelligence · 0009 explanations come from provenance · 0010 code-switching ar/en/fr, Arabic-first launch · 0011 cost ceiling $0.01 (stretch $0.005) · 0012 experiment decision brief · 0013 edit diffs are sensitive personal data.
- **Memo 2 (CFO/CTO + competitor scan):** ADR-0015 cost per *successful* export, and quality ÷ cost · 0016 module map (orchestrator, model_router, recipes, cost) · 0017 router order: deterministic → cache → small → large · 0018 adaptive evidence selection (research-lead must verify the AKS/CSES citations) · 0019 prompt caching · 0020 no training or GPU · 0021 `photos_to_video` recipe.
- ADR-0014 (Proposed, engineering-lead): an additive `provenance.recipe` field. Assurance to rule.
- Also new: `company/positions/05-assurance/DATA_POLICY.md`, `company/positions/01-product/RECIPE_BACKLOG.md`, 2 METRICS.md rows, and an EXPERIMENT.md §0 decision brief.

## Week 1 tasks
| Task | Status | Key result | Evidence |
|---|---|---|---|
| **A. Cost** (`src/cost`, `docs/COST_BASELINE.md`) | Done | Cost per successful export, median / P90: **$0.0080 / $0.0111** at 0 % failures; $0.0084 / $0.0117 at 5 %; **$0.0100 / $0.0139 at 20 %**. Assumes a 0.2 miss rate with Sonnet 5.5 on a miss. Top drivers: planning big-model miss 68 % (estimate), render 11 %, ASR 9 %. 8 unique clips, not 10 (2 short) | H-0027, H-0032 |
| **C. Recipes** (`docs/RECIPE_LANGUAGE.md`, `schemas/recipe.schema.json`, `recipes/`, `src/recipes`) | Done, with a gap | **33 of 36** compiles give valid timelines (11 video recipes × clips 3, 5, 6). **`photos_to_video` fails by design** (`E_RECIPE_SOURCE_KIND`): the renderer has no still-image sources yet. Creative: 4 recipes full, 7 degraded (gaps reported as UNRENDERED). Text overlay not built. Renders in `out/h0029/`. 363 → 381 tests pass | H-0028, H-0029 |
| **B. Bench** (`bench/`) | Running | First commit in (static page, ASR, export modules). Waiting for test evidence and phone instructions | H-0030 |
| **D. Product** (prompt form, fake doors incl. per-video pricing, AdKraft entry, EXP-011) | Not started | — | H-0031 |
| Daily Assurance review | Not started | — | — |

## New findings
- The `clean` and `bold_box` caption presets sit at about 83 % of the frame height, below the style guide's 72 % bound. They need fixing (H-0029).
- Nothing calls the ledger or the usage hook yet. The first orchestrator or LLM brief must wire them in (H-0032).

## Tokens today (estimate)
About **1.2 M** in total. Subagents used about 950k: H-0024 144k, H-0025 184k, H-0026 89k, H-0027 179k, H-0028 42k, H-0029 167k, H-0032 147k. The Operator used about 250k. The H-0030 bench run is still going and is not counted.

## Needed from the Founder (updated)
1. One Arabic speech clip, since the dev set has none.
2. The render reproducibility standard (F1): byte-identical files, or a frame / PSNR check.
3. What failure and miss rates the budget should assume. At 20 % failures, the median uses up the whole $0.01 ceiling.
4. Where to host the bench page for the phone tests. Asked when B returns.
5. Whether to drop the duplicate `Download (4).mp4`.

Process: since the Founder's instruction, finished units are committed as they complete and pushed every 5 min by an Operator loop. The loop never commits and refuses to push media, cache or quarantine paths.
