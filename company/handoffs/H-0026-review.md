# REVIEW H-0026 · assurance-lead · 2026-11-23
<!-- The ONE daily engine review under ADR-0006. Inputs: H-0024-return.md, H-0025-return.md, src/ diff 85dca48..HEAD (HEAD b9c477b). -->
- **From:** assurance-lead
- **STATUS:** DONE
- **VERDICT:** **ACCEPT WITH FINDINGS** (S1: 0 · S2: 1 · S3: 7). No HALT: no media or derived dev data is committed, and no invariant is breached.
- **SUMMARY:**
  - Run 1 reproduced from the H-0025 return alone, in a clean detached worktree (no `cache/`, no `out/`), into a fresh `out/h0026/`. Timeline and `.ass` are byte-identical to the original. The MP4 is **not**: 3 more renders of the identical timeline gave 3 more hashes (F1, S2). The differences are encoder-level (PSNR above 50 dB).
  - All 4 demo outputs are 1080x1920 at 30/1 fps, and each video stream is within 1 frame of its timeline (differences 0, 12, 0 and 33 ms). Run 4 sits exactly on the limit.
  - Captions were checked on 3 frames whose times I took from the caption and effect tracks. All 3 are mid-zoom. The font pair is right, nothing is tofu, and the direction is right. The honesty checks pass. Suite (266 passed, 8 skipped) and ruff are clean in the worktree.
  - D1 (`allow_dev`) is **accepted** with condition F2. The set_duration music behaviour is **acceptable for now** as F3 (S3).
- **ARTIFACTS:** `company/handoffs/H-0026-review.md` (this file), `company/handoffs/H-0026-repro.txt` (raw log, sections A to Q). The scratch outputs, all git-ignored, are in `out/h0026/`: the repro MP4 with its `.timeline.json` and `.ass`, `rr_main_{1,2}.mp4`, `rr_wt.mp4`, `F1..F3*.png`, and `z_none`/`z_2x`.

## Done-when check
| # | Criterion (brief) | Result | Evidence (repro.txt section) |
|---|---|---|---|
| 1 | One demo run reproduced from the H-0025 return alone into fresh `out/h0026/` and compared with the original | ✅ with F1 | §C, C2, C3, C4. Worktree at b9c477b with a copy of `Download (5).mp4`, sha256 equal to the original (`f4da94a6…`). The run had no cache and took 80 s. `.timeline.json` `bda8d7eb…` and `.ass` `45e76b3e…` are identical. The MP4 is `38eb3fe5…` against `c63fc6dc…`. The decoded audio MD5 is identical. Decoded video: 23 of 520 frames differ (from frame 469), with PSNR 52 to 92 dB. Re-rendering the same timeline gave `bb6a9667…` and `38eb3fe5…` in the main repo and `1a89ebed…` in the worktree, so the cause is render non-determinism and not the clean cache. |
| 2 | 3 demo outputs: ffprobe within 1 frame of timeline; 1080x1920, 30 fps | ✅ | §D. Run 1: 17333 ms against v 17.333 s (0). Run 2: 35755 against 35.767 (+12). Run 3: 30000 against 30.000 (0), 11 clips, 900 frames. Run 4 (weak): 30033 against 30.033 (0), but its target is 30000 (+33, F7). All are `1080x1920`, r/avg 30/1. |
| 3 | Captions on 3 frames chosen from the caption track; right text, font pair, no tofu, direction; ≥1 mid-zoom or preset | ✅ | §E. **F1** run 4 at t=0.600: "لنصنع لبن أمو", rtl, joined, `bold_box` box, mid-zoom x1.2. **F2** run 2 at t=22.700: "velociraptor we are slashing", `clean`, Noto Sans, mid-zoom x1.4 (a different time from the engineer's 22.2). **F3** presets_ar_en at t=3.300: "وين بتلاقيه؟ Link in bio", `hook`, Arabic on the right and Latin on the left, `؟` placed correctly, mid-zoom x1.3. The libass log shows only `NotoSansArabic-Regular` and `NotoSans-Regular`, with no glyph-not-found or fallback lines, for all 3 `.ass` files. I viewed exactly 3 PNGs. |
| 4 | Honesty: stub exits non-zero, no manifest; one UNSUPPORTED_FIELD; CAPABILITIES vs renderer for 2 fields | ✅ | §K: `src.score` and `src.select` exit 2 with `NOT_IMPLEMENTED: <stage>` and leave 0 files. A planted stale manifest is deleted. §F-J: `tracks.audio[].gain_db` gives `UNSUPPORTED_FIELD /tracks/audio/0/gain_db` (doc says rendered n). §M: `tracks.effects[].scale` (doc says rendered y), checked on a synthetic 2 s clip: no zoom against x2.0 gives PSNR 11 dB inside the window and 32 dB after it, so the zoom renders. §N: every op in the 3 ops files shows up in the saved timeline and `.ass` (trim, presets, deleted words, 2+1+1 zooms, set_duration). No op is silently ignored. |
| 5 | Full suite + ruff in a clean worktree | ✅ | §B: `git worktree add --detach` at b9c477b. `All checks passed!` and `266 passed, 8 skipped in 4.14s`. The 8 skips are the existing runtime-lock tests. |
| A1 | Addendum: `allow_dev` off by default; cannot admit other `quarantine/` paths; nothing outside `src.demo` sets it | ✅ with F2 | §F-G and §N. The default path is rejected: `validate()` without the flag gives `E_SOURCE_PATH … protected root 'quarantine/'` for all 4 saved timelines, through the CLI as well. With `allow_dev=True` these are still rejected: `quarantine/devX/`, `quarantine/other/`, `quarantine/dev/../other/` and a symlink in `quarantine/dev/` that points into `data/golden/` (it reports `data/golden/`). The absolute path and the directory itself are rejected too. §P: the only programmatic setter is `src/demo/__main__.py:75`. The validate and render CLIs pass a user-typed `--allow-dev` through, which is an explicit human opt-in. `EditContext.allow_dev` defaults to False. |
| A2 | Addendum: set_duration "no words = silence" on music | Ruled | F3: acceptable for now, S3 (see below). |

## Verification ladder
L1: 266 passed. L2: the saved timelines validate with `--allow-dev`, and adversarial timelines get coded issues. L3: timeline and ASS are deterministic, the MP4 is not (F1). L4: ffprobe for all 4 outputs. L5: AR-05 and AR-08 pass validation, and real and synthetic Arabic frames were checked. L6: not requested; caption sizing and grouping are already with creative-lead (H-0024 OQ2, H-0025 OQ4). L7: 80 s wall time for an uncached CPU run of a 37 s clip, 0 LLM tokens.

## Adversarial attempts (31, §F-L)
- **Paths:** 7 allow_dev path shapes, all handled.
- **Ops through `src.demo._apply`:** word index 9999, end before start, scale 2.5, NaN, zoom past the end, negative duration, set_duration 0, -1 and 1e9, unknown preset, unknown op and undo at v0 all get coded `OpError`s. The input v0 is unchanged afterwards (no mutation).
- **Gaps found:**
  - `scale:"abc"` and a non-dict step crash with a traceback (F4).
  - Deleting every word leaves 5.5 s of word-free video with 0 captions (F3).
  - Caption text: AR-05, AR-08, RLM-led and 2000 chars all validate. An empty string is `E_SCHEMA`. A time out of range is `E_CAPTION_BOUNDS`. An emoji validates but the renderer refuses it (F5). 2000 chars has no bound (F6).

## Findings
**F1 · S2 · MP4 render is not byte-deterministic (I-1 overclaim in H-0025 "a rerun gave a byte-identical MP4").**
- *Evidence:* §C4. The same `timeline.json` (`bda8d7eb…`) rendered 4 times on the same machine gave 4 different sha256 values: `38eb3fe5`, `bb6a9667`, `38eb3fe5` and `1a89ebed`. H-0025 saw `c63fc6dc` twice. Audio is bit-identical. The video differs in a few frames, at PSNR above 50 dB, so it cannot be seen. The H-0025 match was luck, not a property.
- *Required action (engineering-lead):* Find the source of the nondeterminism. Likely suspects are thread-count-dependent x264 or filter-graph threading, so try `-threads 1` or fixed x264 threads as a test. Then either make the render byte-deterministic or restate the determinism claim as "decoded-frame identical, or PSNR ≥ X". A threshold change needs Founder or ADR sign-off, not Engineering alone. Until then, no return may claim a byte-identical MP4 from one rerun.
- *Verification:* Assurance renders one timeline 5 times, including under parallel CPU load, and compares sha256 (or framemd5 under the restated criterion).

**F2 · S3 · D1 accepted, but dev outputs are not marked as dev.**
- *Evidence:* §N and §P. The opt-in is scoped correctly (A1). However, the saved `*.timeline.json` and MP4 carry no `dev_only` marker. Only the source path shows ADR-0006 status, and a re-encode or copy would lose it.
- *Required action (engineering-lead):* Whenever `allow_dev` is used, the demo writes `provenance.selection` (or an equivalent existing meta field, so no schema change) containing `ADR-0006 dev-only`. Any future publish or export step must refuse a timeline that carries this marker.
- *Verification:* grep the saved timeline of a dev run for the marker, and run one negative test on the export step once it exists.

**F3 · S3 · set_duration and delete_words treat "no ASR words" as removable or keepable silence; this is wrong on music and B-roll.**
- *Evidence:* H-0025 run 4: 30 s of music was cut from the middle. §H12: target 5000 gives 4999 ms with the tail cut. §H13: deleting all 88 words leaves 5501 ms in 11 clips with 0 captions, and no error. The docstring calls these gaps "silence".
- *Ruling:* acceptable for now. The target market is speech-led Shorts, the behaviour is deterministic and documented in code, and only dev clips are affected. It becomes S2 when non-speech footage enters scope (CLAUDE.md "Source footage" TBD).
- *Required action:* Rename the gaps to "no-word gaps" in the docstring and in CAPABILITIES or the ops README. Raise `E_OP_EMPTY` (or similar) when an op leaves no words. Leave the audio-energy test (H-0025 OQ2) to engineering-lead with creative-lead.
- *Verification:* a unit test showing that delete-all raises, and a doc grep.

**F4 · S3 · Malformed ops.json crashes with a traceback instead of a coded error.**
- *Evidence:* §L. `{"ops":["trim"]}` gives `AttributeError` and `"scale":"abc"` gives `ValueError`. Each exits 1 with a Python traceback. `run()` catches only `OpError`.
- *Required action:* Validate each step's shape and types (dict, numeric fields) and raise a `DemoError`.
- *Verification:* rerun the two §L files and expect a one-line coded error with no traceback.

**F5 · S3 · The validator passes caption text that the renderer will refuse.**
- *Evidence:* §I. An emoji caption ("جربت 🔥") validates with `[]`. CAPABILITIES says that a character outside both fonts fails the render (H-0024 D4). I did not reproduce the render failure. This breaks the spirit of rule 3 ("validate before render") and the CAPABILITIES contract ("never carries an instruction the renderer silently ignores"): it fails loudly, but too late.
- *Required action:* `validate()` reports the out-of-range character with its JSON path. Reuse the fontrun coverage check.
- *Verification:* validate the §I emoji case and expect a coded issue.

**F6 · S3 · There is no caption length or overflow bound.**
- *Evidence:* §I. A 2000-character caption validates.
- *Required action:* engineering-lead, with creative-lead setting the number, adds a max characters per caption (or wraps and checks height) in the validator.
- *Verification:* a fixture in `invalid/`.

**F7 · S3 · Run 4 lands exactly on the 1-frame tolerance (30033 against target 30000).**
- *Evidence:* §D. This is H-0025 OQ3: the tail snap is in source time.
- *Required action:* snap the tail on the output grid, as Engineering proposed.
- *Verification:* rerun run 4 (or a unit test with an offset source grid) and expect exactly 30000 ms.

**F8 · S3 · Rights flag, for the Founder and the RR register (not a decision).**
- *Evidence:* §C3. The output MP4 inherits the source container's `comment` tag, which carries the third-party platform video ID (redacted in the repro log), because global metadata is copied by default. The zoom crops out the platform watermark (frame F2, and H-0025 noted the same). The frames show an identifiable third-party person and creator handles.
- *Assessment:* Both are inside ADR-0006 "internal development testing only", but both would be problems on any publish path. Stripping a watermark from third-party content is a rights red flag, and leaking the source ID is a provenance and privacy leak (see RR-014).
- *Required action (engineering-lead):* the renderer passes `-map_metadata -1`.
- *Required action (Assurance):* add a DATA_RIGHTS or RISK note that watermark-cropping on third-party clips is dev-only.
- *Verification:* ffprobe the format tags of a new render and expect no `comment`.

> Count note: S3 findings are F2 to F8, which makes 7.

## Invariant scan
- **I-1:** F1 is an overclaim. Every other H-0024 and H-0025 claim that I sampled reproduced: ffprobe values, frame counts, fontselect lines, test counts, NOT_IMPLEMENTED behaviour and UNSUPPORTED_FIELD.
- **I-2:** independent review. I am not the builder.
- **I-3:** no LLM in the pipeline. I viewed 3 frames, which is the brief's cap.
- **I-4:** all times come from code (ops and snapping).
- **I-5:** no experiment touched.
- **I-6:** held-out not accessed, and no held-out path is named in any command or log. The symlink probe targeted `data/golden/`.
- **I-7:** no ADR edited.
- **I-8:** n/a for this review. The Operator closes the session.
- **I-9:** dev clips are under ADR-0006. F8 is flagged.
- **I-10:** no tier growth.
- **Committed media:** none. §A: `git log --diff-filter=A 85dca48..HEAD` adds no media, CSV, `.ass`, `out/`, `cache/` or `quarantine/` file. The only tracked PNGs are the pre-existing synthetic EXP-008 renders. `quarantine/`, `out/` and `cache/` are git-ignored. `examples/ops/*.json` contain no dev-derived content.

## Deviations from brief
- I ran the repro in a detached worktree of HEAD, using a copy of the dev clip, so that there was truly no cache. The output was written to the main `out/h0026/`. The copy and the worktree were removed afterwards.
- §K first attempt: the stub CLIs need `--input/--out`. Without them argparse exits 2. That was not a NOT_IMPLEMENTED test, so I retried it once with the arguments.
- §C: `/usr/bin/time` is missing. I retried once using bash `SECONDS`.

## Open questions
1. **F1:** is "decoded-identical or PSNR ≥ X" an acceptable determinism criterion, if byte-determinism costs too much encode speed? Owner: Founder, on an engineering-lead proposal.
2. **F8:** should the renderer strip all source metadata by default, as a product rule and not only for dev? Owner: engineering-lead, with assurance for rights.

## Next recommended step
Engineering fixes F1 (investigation) together with F4, F5 and F8. Each is small and inside `src/`. F2, F3, F6 and F7 go into the next H-brief. Tomorrow's daily review reruns §C4 (5 renders) and §L.

- **CONFIDENCE:** High that the outputs meet the brief (durations, sizes, captions, honesty). Medium on F1's root cause, which was not isolated within the budget.
