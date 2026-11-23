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
