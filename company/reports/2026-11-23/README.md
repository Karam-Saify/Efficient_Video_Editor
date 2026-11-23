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

---

# Part 3 (evening): Week 1 A–D finished, daily review, Founder S1 correction

## Week 1 final status
| Task | Status | Result |
|---|---|---|
| A. Cost | Done | See Part 2. Assurance reproduced the doc's numbers within 0.01 %. **But the ASR cost and P90 may be understated** if ASR is missing Arabic speech (F4) |
| B. Bench | Done | `bench/`: Whisper base→tiny on WebGPU→WASM, 30 s 1080×1920 export with a 720 fallback, watchdog, Copy results. In headless Chrome: 0 errors, ffprobe 1080×1920/30 fps/900 frames, ASR tiny-WASM RTF 0.47. WebGPU and AAC were not exercised. Phone run: see "Bench instructions" below |
| C. Recipes | Done, with a gap | 33/36 compiles valid. `photos_to_video` fails by design (no still-image sources yet). **The "3 English speech clips" choice is unverified** (F4) |
| D. Product | Done | Prompt form, 3+1 fake doors, EXP-011 Brand Brain (DRAFT: pass at ≥ 11/15 blind picks and ≥ 2/3 businesses), AdKraft entry (~$3/video = ad packs 5 for $15 / 25 for $75, source apps.shopify.com/adkraft, E1; Founder to eyeball once). Pricing-door anchors are placeholders [X] |

## Daily Assurance review H-0033: ACCEPT WITH FINDINGS (S1 0 · S2 5 · S3 8)
- **S2 (fix before anything is published or collected):**
  - F1: the consent says "not shared", but the form host and LLM provider are processors, and there is no deletion path.
  - F2: the form sends prompt text to RECIPE_BACKLOG, which breaks DATA_POLICY §5.
  - F3: EXP-011 has no rights warranty for business clips or the people in them.
  - F4: H-0027 and H-0029 rely on unverified speech/language labels.
  - F5: bench libraries, Whisper weights and fonts have no RR rows, so they can't be used under I-9 until recorded.
- **S3:**
  - F6: LLM prices cite a cached skill table, not the vendor page.
  - F7: MiB vs GB units.
  - F8: captions collide with on-screen source text.
  - F9: the bench passes ASR on a hallucinated transcript of a beep file.
  - F10: no SRI on the CDN code, and ORT web is a prerelease.
  - F11: "coming soon" fake doors imply a promise.
  - F12: an unclear error for a dev source used without `--allow-dev`.
  - F13: ADR-0014 accepts unbounded string params.
- **Rulings:**
  - ADR-0014: recommend Accept, with F13 as a condition. **Founder or M1 gate to accept.**
  - JFK sample: RR-025, usable with restrictions (bench input only, fetched at run time).
  - 90-day retention: approved as a maximum, with conditions; it needs an ADR amending DATA_POLICY §4 before the first external response.
- Reproduced: cost rows/median/P90 within 0.01 %; recipe cells byte-identical; ffprobe matches; 404 tests green; no media in git; no blocked auto-pushes.

## Founder S1 correction (late afternoon)
- The H-0024 catalog labelled clips with Arabic speech as English or no-speech. **ASR fails on Arabic; the footage is fine.**
- Recorded as **ADR-0022**: data claims need a Founder spot-check before they count as evidence.
- Inventory: only **11 MP4s** reached the Codespace, not the ~15 uploaded.
  - `Download (9)` and `(10)` moved to `quarantine/dev/` (RR-023/024).
  - `Download (4)` deleted (byte-identical to `(2)`).
  - 10 clips remain.
- `quarantine/dev/LABELS.csv` was created (git-ignored). **Waiting on the Founder to fill it in.** No ASR runs until then.
- Next: register EXP-012, the ASR diagnostic (multi-window language ID, VAD on/off/low, Demucs vocals vs raw, turbo vs large-v3, auto vs forced `ar`). Demucs is a new dependency (T2). large-v3 still has to be downloaded (~3 GB).

## Bench instructions (Founder, on a phone)
1. In the Codespace: `cd bench && python3 -m http.server 8000`.
2. Ports tab → copy the HTTPS address for port 8000 and keep it **Private**.
3. Open it in Chrome (Android) or Safari (iPhone) and sign in to GitHub once.
4. Tap **Run benchmark** and keep the screen on until it says "done". Then tap **Copy results** and paste them to the Operator. Run it twice (the second run shows the cached model load).

Note F5: under I-9 the bench's libraries and weights need RR rows before results count. Assurance can add them in the next fast-lane batch.

## Tokens today (final estimate)
About **1.45 M**. Subagents ~1.18 M:
- H-0024 144k, H-0025 184k, H-0026 89k
- H-0027 179k, H-0028 42k, H-0029 167k
- H-0030 107k, H-0031 27k, H-0032 147k, H-0033 98k

The Operator used ~270k. No LLM is in the product loop yet, so a Short costs 0 tokens.

## Needed from the Founder
1. **Fill `quarantine/dev/LABELS.csv`.** It blocks EXP-012.
2. Re-upload the ~4 clips that didn't arrive.
3. Accept ADR-0014 now, or defer it to the M1 gate.
4. Pricing-door anchor numbers; pick the form tool (no collection before F1–F3 are fixed).
5. Still open: the F1 render-determinism standard, and the failure/miss rate to budget for.

---

# Part 4 (night): Founding Creator Data Program, pilot day 0 (Daily, pilot)

## Decision
**ADR-0023**: the Founding Creator Data Program runs as a zero-cost concierge pilot. Tools are local and open-source; annotation and Director reasoning happen inside Claude Code sessions, with no paid API. Targets for days 1–10: 5 partners, 20–30 rights-cleared source videos, 5 jobs × 2 versions, every choice and correction logged. Daily reporting goes through the new `/daily` command.

## Done
| Item | Status | Evidence |
|---|---|---|
| Consent kit, ar + en: 3 separate permissions (evaluation / product development / training, **default OFF**), partner warranty, withdrawal without email | Done | `company/positions/05-assurance/CONSENT_KIT.md` |
| Partner intake form + feedback form (fields 1:1 with the ADR-0023 job fields) | Done | `PARTNER_INTAKE_FORM.md`, `PARTNER_FEEDBACK_FORM.md` |
| H-0033 S2 findings F1 (consent "not shared"), F2 (prompts in the backlog), F3 (rights warranty), F5 (bench RR rows) | **Closed** | H-0034 return; RR-031..037 |
| ADR-0024: 90-day maximum retention, amending DATA_POLICY §4 | Proposed, **Founder to sign** | `company/decisions/` |
| Eval-set licences (primary sources, 2026-11-23) | Done | RR-026..030 |
| Annotation schema + Footage Intelligence v0 storyboard (H-0035) | **Running** (schema in progress) | — |
| Common Voice Arabic baseline EXP-013 (H-0036) | Queued after H-0035 | brief |

## Eval-set licence verdicts
| Set | Verdict |
|---|---|
| Common Voice Arabic 27.0 | **Usable**, internal eval (CC0; no re-hosting, no speaker identification; whether download needs a sign-in is unverified) |
| SHAMS (Levantine) | **NOT usable**. The card says BY-SA, but LangMedia's own page says BY-NC-SA, which covers all 316 Lebanese rows. The other 393 rows are BY-NC-ND. **Escalated to the Founder** |
| Arabic Speech Corpus | **Usable**, internal eval only. It is CC BY 4.0, not non-commercial; ADR-0023 is corrected |
| TimelineBench | Apache-2.0 code/tasks: reference only, never training. Media: **NOT usable** (no access; contradictory terms) |

## Pilot progress (targets for days 1–10)
| Metric | Now | Target |
|---|---|---|
| Partners recruited (with signed consent) | 0 | 5 (Founder's store = #1) |
| Source videos with rights | 0 | 20–30 |
| Jobs delivered (2 versions each) | 0 | 5 |
| human_verified labels / feedback records | 0 / 0 | all choices + corrections |

## Cost and plan usage
- **Cash cost today: $0.** No paid API calls, tools or storage; everything ran locally or inside this Claude Code session.
- **Plan usage today (estimate): ~1.6 M tokens.** Subagents used ~1.29 M, the Operator ~300k. The pilot share so far is H-0034 at 108k, about 7 %. H-0035 is still running and not counted.

## Founder asks (updated, in order)
1. **Confirm that the Claude account's model-training setting is OFF** before any partner data reaches a session.
2. **Sign ADR-0024** (90-day retention).
3. **SHAMS:** ask LangMedia or the authors for written permission, get a lawyer's opinion, or drop it and find another Lebanese eval source?
4. **Fill `quarantine/dev/LABELS.csv`**; it blocks EXP-012.
5. Partner #1 (your store): intake form + signed consent, then upload the clips.
6. Common Voice: if the download needs an account, research-lead will send you the steps.
7. Still open: re-upload the ~4 missing clips; ADR-0014; pricing-door anchors; form tool; the F1 determinism standard; the budget failure rate.
