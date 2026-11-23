# REVIEW H-0033: daily Assurance review of Week 1 A to D (ADR-0006)
- **Reviewer:** assurance-lead · **Date:** 2026-11-23 · **Range:** `511dbb7~1..e655739` (22 commits, 103 files)
- **Reviewed:** H-0027 (cost baseline), H-0028/H-0029 (recipes + compiler), H-0030 (device bench), H-0031 (product copy), H-0032 (cost per successful export)
- **Repro log:** `company/handoffs/H-0033-repro.txt` · scratch outputs: `out/h0033/` (git-ignored)
- **Method note:** I wrote this verdict before reading any builder CONFIDENCE line. I read the returns only for repro commands and claims. This file is also the return for H-0033, because the brief limits writes to the review, the repro, LOG.md and DATA_RIGHTS.

## STATUS: DONE · VERDICT: ACCEPT WITH FINDINGS (S1: 0 · S2: 5 · S3: 8)

None of the brief's escalation triggers fired:
- No media or dev-derived text is in git.
- The bench sends no user media off-device.
- Every cost figure I checked reproduced within 0.01 %. The 5 % escalation threshold was not reached.

There is no HALT.

The Founder can trust the Week 1 numbers and the compiler mechanics as reported, with one exception: the language and speech labels behind them are unverified (F4, ADR-0022). The product consent text is **not ready to publish** until F1 to F3 are fixed. No collection has started, so nothing has been breached yet.

## Rulings requested by the brief
1. **ADR-0014 (`provenance.recipe`): Assurance recommends ACCEPT**, with one condition (F13).
   - The change is additive: an optional, closed object in the schema diff (`git diff 511dbb7~1..HEAD -- schemas/timeline.schema.json`, +13 lines).
   - A timeline without the block still validates.
   - An extra key, a bad id pattern and a missing required key are each rejected with `E_SCHEMA`.
   - The full suite passes (404 passed). It is a two-way door.
   - Condition: the ADR says no personal text goes in `params`, but nothing enforces that. A 3,500-character Arabic string with RLM marks validated. Bound string params before any free-text param exists.
2. **JFK sample: recorded as RR-025, usable with restrictions.**
   - The speech text is public domain: it is a work of the US Government made in official duties (17 U.S.C. §105).
   - Who made the 1961 audio recording has not been verified from a primary source. That is the residual risk.
   - Permitted use: an internal on-device bench input only. It is fetched at run time from a pinned URL, never stored in the repo, and never used in outputs, marketing, rubric anchors or the golden set.
3. **90-day retention: APPROVED as the maximum** for prompt-form responses, waitlist emails and EXP-011 materials, with these conditions:
   - (a) The 90 days are counted from the date of collection.
   - (b) Deletion covers the hosting tool, every export and every local copy, and each deletion is logged with its date.
   - (c) The consent text says what is kept after 90 days (see F2). Only anonymised aggregate tallies may be kept.
   - (d) It must be recorded by an ADR that amends DATA_POLICY item 4 before the first external response. DATA_POLICY says "extend only by ADR", so this ruling alone does not change the policy.
   - (e) F1 must be fixed first.
4. **H-0027 D2 (is the measurements file "derived data"?): acceptable.** It holds only numbers: timings, byte counts, word, segment and scene counts, and sha256 hashes. It contains no content. Keep it that way.

## Done-when verification
| Item | Result | Evidence |
|---|---|---|
| Cost: one row recomputed + median | PASS | I wrote my own script without importing the builder's code. `Download (1)` = 6.363 m$ (asr 0.330, und 0.152, plan 5.400, render 0.355, storage 0.126), and the doc says the same. Median 7.986, P90 11.087 (nearest rank). The doc, the code and my hand calculation agree. Repro §A. |
| Cost: every price cites a source | PASS with F6 | A1–A3 cite primary URLs with a fetch date. A5/A6 (LLM prices) cite a cached skill table, not a primary page. |
| Cost per successful export | PASS | `tests/unit/test_cost.py` 17 passed. Hand check: (c + c(f+f²))/(1−f³) at c = 6.363, f = 0.2 gives 7.95375, and the code returns 7.95375. Per-success medians recomputed: 20 % = 9.983 / 13.859; 5 % = 8.406 vs 8.407 in the doc (rounding). f ∈ {1, −0.1, 1.5, NaN} raises ValueError. Repro §A2. |
| Recipes: 3 cells | PASS | R05×Download (3) and R01×Download (5) are byte-identical to the committed outputs. `photos_to_video` on img_set2 exits 2 with `E_RECIPE_SOURCE_KIND`, writes no timeline and lists 6 UNRENDERED items. Repro §C. |
| UNRENDERED complete for 1 degraded recipe | PASS | R02, field by field: all 5 render fields are listed as unrendered, the 5 prose fields are listed as advisory, and the beats are disclosed as proportional windows (RECIPE_LANGUAGE.md:83). |
| ffprobe one render vs its timeline | PASS | `Download5__R01.mp4`: 1080×1920, 30/1, 1050 frames = 35.000 s. The timeline is 35000 ms. |
| Captions on 1 frame | PASS with F8 | At 14.4 s caption cap11 is present and correctly timed. It sits on top of the source's own burned-in text. |
| Bench: dev clips, CDN pins, off-device data | PASS with F5, F9, F10 | No dev clip is referenced. Every URL is pinned to a version or a commit. There is no POST, beacon or analytics. A user file stays in memory, and only its size and MIME type are recorded. The committed transcript in the smoke JSON comes from a 28,028,273-byte file. No dev clip has that size, so this is a Whisper hallucination on the synthetic beep, not dev text. |
| JFK licence → RR row | DONE | RR-025 in DATA_RIGHTS.md. |
| Product: consent, retention, deletion vs DATA_POLICY / ADR-0013 | FAIL until fixed (F1–F3) | See findings. |
| Fake doors honest, no payment capture | PASS with F11 | All 4 doors state that nothing is charged. No payment field exists. |
| Hygiene: no media or dev text in git | PASS | I checked `git log --stat` over the range for media extensions: none. I grepped the committed JSON transcripts: JFK (public domain) and the hallucination only. |
| Auto-push log | PASS | 4 lines, all "pushed". None is blocked or failed. The branch is 3 ahead at 14:25, which is inside the 5-minute cadence. |
| Suite + ruff | PASS | In a clean worktree of HEAD: 404 passed, 8 skipped. `ruff check .` gives "All checks passed!". |

Ladder:
- L1 PASS: unit tests.
- L2 PASS: schema, with 5 ADR-0014 cases.
- L3 PASS: compile determinism. Two cells are byte-identical. I did not rerun render determinism today; that stays with H-0026 §C4.
- L4 PASS: ffprobe.
- L5: not exercised. No Arabic speech clip has a verified label (F4).
- L6: not done. Creative was not consulted.
- L7 PASS: cost.

Adversarial attempts: 21. They covered empty input, extreme length, the RLM-suffixed enum (AR-08-style), an Arabic enum value, NaN, out-of-range values, a path-traversal recipe id, empty and mismatched sources, a missing `--allow-dev`, and failure rates of 1, −0.1, 1.5 and NaN. All 21 were rejected with the correct code except one misattribution (F12). Repro §Adversarial.

Invariant scan:
- I-1: the claims I checked carry evidence.
- I-3 and I-4: no LLM is in the path yet. Zoom times and durations are computed by code.
- I-5: EXP-011 is DRAFT and unlocked, which is correct.
- I-6: held-out data was not touched, and I did not name its path.
- I-7: ADR-0013 was not edited in the range.
- I-8: auto-push is running.
- **I-9: gap.** The bench's third-party libraries, weights and fonts have no RR rows (F5).
- I-2 and I-10: no breach.

## Founder correction (ADR-0022): which conclusions depend on unverified labels
- **H-0027 / COST_BASELINE.** The computed cost figures are exact for the runs that happened. These statements rest on the unverified ASR labels:
  - "None of the clips is Arabic speech"
  - the two "no-speech" clips
  - "`Download (8)` is ar with 3 words"
  - "`Download (2)`… VAD drops its music-only audio"
  - The ASR row describes failing ASR. If speech was missed, the ASR CPU, the transcript tokens and the P90 clip's cost are understated (F4).
- **H-0029.** These statements rest on the same labels:
  - the clip choice "3 English speech clips"
  - "the dev set has no Arabic speech clip"
  - The captions in every compiled timeline are ASR output.
  - What still holds: the compiler mechanics, determinism and UNRENDERED.
  - What is unverified: whether any of the 33 timelines carries correct-language captions, and whether the Arabic FILLERS/GREETINGS paths were ever exercised on real speech.
- **H-0025 / H-0024.** Every language, wpm and speech/no-speech column in `dev_manifest.csv` / `LABELS.csv` is unverified until the Founder spot-checks it.
- I did not rerun ASR, as instructed.

## Findings
| # | Sev | Finding | Evidence | Required action | How the fix is verified |
|---|---|---|---|---|---|
| F1 | S2 | The consent texts say "we do not share them with anyone", but the form host (the Founder's tool) and, for EXP-011, the LLM API provider are third-party processors. The form has no deletion channel for a respondent who left no email, because "reply to our email" has nothing to reply to. | PROMPT_COLLECTION_FORM.md consent block (AR+EN); FAKE_DOOR_COPY waitlist line; EXP-011 consent | Name the processors ("stored in <tool>; processed by <LLM provider> under its no-training API terms"). Add a contact address and a response ID or code shown on submit, so deletion works without an email. Add an age line (18+). | Assurance re-reads the AR and EN text before the Founder publishes. I check that the AR and EN versions say the same thing. |
| F2 | S2 | The form sends "anonymised prompt text" to `RECIPE_BACKLOG.md`. That contradicts DATA_POLICY item 5 (the backlog holds no user content) and ADR-0013 (prompts are sensitive). The consent also never says that anonymised excerpts outlive the 90 days. | PROMPT_COLLECTION_FORM.md "Rules" line vs DATA_POLICY.md item 5 | Keep prompt text out of the repo (store it access-controlled, outside git), or amend DATA_POLICY by ADR. The consent must say which derived data is kept after 90 days, if any. | grep the repo for prompt text after collection. Check that the ADR or form revision exists. |
| F3 | S2 | EXP-011 takes business clips and brand notes with no rights warranty and no permission for people who appear in the clips. There is no RR intake step (I-9). | EXP-011 §5 step 2, consent block | Add "you own or have permission for these clips and the people in them" to the consent. Record one RR row per business before any clip is touched. | Checked at the EXP-011 lock (Assurance locks). |
| F4 | S2 | Conclusions in H-0027 and H-0029 depend on automatic speech and language labels that ADR-0022 now treats as unverified. ASR may be failing on Arabic speech. | COST_BASELINE §4 and §6; H-0029 return line 28; Founder correction 2026-11-23 | Mark the cited statements "label unverified (ADR-0022)" in COST_BASELINE and the H-0029 matrix. After the Founder spot-check, re-measure ASR on the corrected speech clips and add 1 verified Arabic-speech clip to the recipe matrix. | Rerun the cost report and compare the median and P90 with today's values (7.986 / 11.087). Assurance repeats this recompute. |
| F5 | S2 | The bench loads third-party assets that have no DATA_RIGHTS rows: transformers.js 4.3.2, an onnxruntime-web dev build, mp4-muxer 5.2.2, the Xenova whisper-base and whisper-tiny weights (whose OpenAI MIT origin also needs recording), and the fontsource Noto woff2 files. I-9 says no record means no use. | bench/libs.js, bench/README.md:55-62; `grep -ci xenova\|transformers\|mp4-muxer DATA_RIGHTS.md` returns 0 | Before the Founder runs the bench on devices, Engineering supplies the primary licence proof for each asset and Assurance records the RR rows. | The rows exist with a URL, a quoted clause and a date. |
| F6 | S3 | The LLM prices A5 and A6 cite a cached skill table dated 2026-11-03, not a primary pricing page. | COST_BASELINE §2; cost_baseline.py ASSUMPTIONS comment | Cite the vendor pricing URL with its fetch date. | Read the doc. |
| F7 | S3 | Units are not stated. Memory and storage use MiB/GiB (÷1024), while vendors price per GB. The effect is up to 7 % on storage and memory, below 0.05 m$ at the median. | src/cost/model.py:25,30 | State the unit in the doc, or switch to the vendor's unit. | Read the doc. |
| F8 | S3 | The caption is burned on top of the source's own on-screen text, so both are hard to read. There is no collision or safe-zone logic. The TikTok handle and watermark are visible (already H-0026 F8). | out/h0033/f1_14400.png (R01×Download (5), 14.4 s) | Add a caption-position or collision item to the RECIPE_LANGUAGE backlog. Creative rates it. | The next render review frame. |
| F9 | S3 | The bench counts ASR as "ok" whenever any text comes back. On the beep-only synthetic file it returned a fluent invented sentence and passed. This matches the Founder's report that ASR fails silently. | experiments/results/H-0030_smoke_fallback_file.json step 5; size check in repro §B | Report a WER against the known JFK text. Flag any non-empty transcript on known non-speech input as a hallucination. Label `file_asr` "speed only, quality unknown". | A smoke rerun shows a WER field and a hallucination flag. |
| F10 | S3 | There is no SRI or hash check on the CDN code. ORT web is a prerelease. The page text "Nothing is uploaded" is true for media, but the device does contact jsDelivr and Hugging Face, which see its IP address and user agent. | bench/libs.js; index.html:31 | Record the sha256 of each fetched module in the results, or self-host it. Add one sentence naming the CDNs contacted. | Static read. |
| F11 | S3 | The fake-door modals say "Coming soon", but the kill rules may drop the feature, so this is an implied promise. The waitlist deletes emails at 90 days, which may be before launch. | FAKE_DOOR_COPY doors 1, 2 and 4 | Use "We're considering building this" (AR to match). Say that the email is kept for 90 days at most even if there is no launch. | Read the doc. |
| F12 | S3 | A dev source without `--allow-dev` surfaces as `E_RECIPE_OP: set_duration … E_OP_INVALID` instead of an upfront `E_SOURCE_PATH`, so the error points at the wrong step. | repro §Adversarial, "no --allow-dev" line | Check the source path before compiling. | A CLI rerun shows E_SOURCE_PATH first. |
| F13 | S3 | ADR-0014: `params` accepts unbounded strings, so the ADR's "no personal text" assumption is not enforced. | out/h0033/adr0014_adv.txt (adv_freetext VALID) | Restrict string params to the recipe's enum values, or add a maxLength, before any free-text param ships. This is the acceptance condition. | Schema test with the freetext case giving E_SCHEMA. |

## Open questions (for the Operator)
1. Who accepts ADR-0014: the Founder now, or the M1 gate? Assurance has no objection once F13 is ticketed.
2. Which ADR number records the 90-day retention (DATA_POLICY item 4), and who drafts it: Product, with Assurance reviewing?
3. Should the F5 RR rows for the bench come before the Founder's phone run? I recommend yes.

## Next recommended step
1. Product fixes F1–F3 and Assurance re-reads the text before anything is published.
2. Engineering supplies the F5 licence proofs.
3. After the Founder's label spot-check, run the F4 re-measure.
