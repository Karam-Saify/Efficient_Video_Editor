# EXP-006 results: Arabic caption rendering correctness, FFmpeg + libass path
- **Preregistration:** `company/experiments/EXP-006.md` (LOCKED 2026-11-22, not edited)
- **Owner:** research-lead · **Brief:** H-0010 (write-up) · Run: H-0006 (engineering-lead) · Ruling: `company/handoffs/H-0006-ruling.md`
- **Date:** 2026-11-22
- **VERDICT: INVALID.** No PASS and no FAIL is declared. `N_correct` and `N_sev1` are **not measured**.
- **Evidence level of any claim about the FFmpeg + libass caption path from this run:** none (E0). The run does not feed the component-adoption decision.
- **Successor:** `company/experiments/EXP-008.md` (DRAFT; declared font pair Noto Sans Arabic + Noto Sans).

## 1. Why INVALID
During rendering, libass resolved a second font file, `/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf`, for three of the ten strings. EXP-006 §8 lists "different font file resolved" as invalidating, and its non-invalidating list explicitly excludes font fallback ("extra log warnings that are not font fallback"). The full reasoning from the locked text is in `company/handoffs/H-0006-ruling.md` §1.

Evidence, `render/frames_check/render.log`:
```
l.135  Glyph 0x69 not found, selecting one more font for (Noto Sans Arabic, 400, 0)        [AR-05]
l.136  fontselect: (Noto Sans Arabic, 400, 0) -> /usr/share/fonts/truetype/noto/NotoSans-Regular.ttf, 0, NotoSans-Regular
l.224-225  Glyph 0x22 not found ... -> NotoSans-Regular.ttf                                  [AR-08]
l.284-285  Glyph 0x2013 not found ... -> NotoSans-Regular.ttf                                [AR-10]
```
libass logs only the first missing glyph per event. A charset check by research-lead (`fc-query --format='%{charset}'` on both font files, re-run 2026-11-22 for H-0010) gives the full extent:

| String | Code points missing from NotoSansArabic-Regular.ttf | Covered by NotoSans-Regular.ttf? | Property the string tests |
|---|---|---|---|
| AR-05 | U+0050 U+0065 U+0068 U+0069 U+006E U+006F U+0072 (P e h i n o r) | yes, all | Latin + digits mixed |
| AR-08 | U+0022 U+0028 U+0029 (" ( )) | yes, all | quotes and brackets mirroring |
| AR-10 | U+2013 (–) | yes | percent sign + dash + digits |
| other 7 | none | n/a | n/a |

All 39 Arabic-block code points used in the 10 strings are covered by Noto Sans Arabic. ASCII digits and U+0020 are covered by both fonts. In AR-05, AR-08 and AR-10, the fallback font produced exactly the glyphs those strings exist to test. A judgement on them would have been a judgement on an undeclared configuration, not the one in EXP-006 §1.

**Root cause (owned by research-lead):** EXP-006 §4 listed the non-Arabic code points but never checked that the declared font covers them. The file was also locked before Engineering confirmed feasibility (§10). This was a preregistration design flaw. It was not an execution error.

## 2. Deviations (all listed, none hidden)
| # | Deviation | Effect on validity |
|---|---|---|
| D1 | A font file other than the declared one resolved for AR-05, AR-08, AR-10 (see §1) | **Invalidating** (EXP-006 §8) |
| D2 | **Missed fallback detection.** In both runs, the step-4 warning check in `experiments/exp006_render.py` used the regex `fallback\|glyph not found`, which does not match libass's wording `Glyph 0x69 not found` (capital G, hex code between the words). The script printed "warnings: none". Engineering found the fallback by grepping `render.log` by hand (`company/handoffs/H-0006-return.md`, Deviations 3). | Did not change outputs. It shows that the step-4 instrument was never validated. EXP-008 adds a known-fallback control. |
| D3 | **Script edited after run 2.** After the final run, Engineering widened the regex and ran `ruff format`. The committed script is not byte-identical to the one that produced the outputs. Current sha256 `8f08355430c836ddbfa21b2a0c5597bb13ccb7fe336b71ca81ce7ca07c46222c`. The hash of the pre-edit version was not recorded. | Not output-affecting per Engineering (stdout and layout only). Unverified, because no rerun was done. Moot given D1. EXP-008 requires the instrument hash to be recorded before the run and checked after it. |
| D4 | The procedure was executed twice (original run plus one determinism rerun). SHA256SUMS were byte-identical across the runs. | Allowed by the §8 re-execution rule (max 2). Not invalidating. |
| D5 | The brief's milestone criterion label ("0.3") differs from ROADMAP 0.7. | Clerical. None. |

No re-execution under EXP-006. The cause is a design gap and the render is deterministic, so a rerun would reproduce D1 (ruling §4).

## 3. Judging status
**No PNG has been judged.** No PNG has been viewed by anyone. Engineering used only ffprobe, stat and sha256. Research did not open or hash any PNG. The H-0007 judging brief was not executed. Do not view the 10 PNGs from now on, including for exploration. Under EXP-008, 6 of the 10 strings (AR-01, 02, 03, 06, 07, 09) have Dialogue text identical to EXP-006, so their renders will probably be byte-identical. Prior exposure would bias the EXP-008 judge.

Per-string table (EXP-006 §5.3 step 7): not applicable. `correct_i` and `sev1_i` were never recorded.

## 4. Environment (from `render/frames_check/ENV.txt`, captured 2026-11-22T16:47:15Z)
- ffmpeg 6.1.1-3ubuntu5 (`--enable-libass --enable-libharfbuzz --enable-libfribidi --enable-libfontconfig`); `ass` filter present
- libass9 1:0.17.1-2build1 (render.log: `libass source: tarball: 0.17.1`), libharfbuzz0b 8.3.0-2build2, libfribidi0 1.0.13-3build1; shaper line `FriBidi 1.0.13 (SIMPLE) HarfBuzz-ng 8.3.0 (COMPLEX)`
- fonts-noto-core 20201225-2. `fc-match "Noto Sans Arabic"` → `/usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf`, sha256 `504d7407d86875acf7d04dfaa0fd7524d0b8797723bc4aa18022f29db25b0b6e` (RR-001)
- Fallback file: `/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf`, sha256 `89c3c497f618fdaa0b2d1e98fef93582f28c71debd2c4a8cdf41f190ced2909d` (RR-011, recorded after the run by H-0008)
- Linux 6.8.0-1070-azure x86_64, nproc 2, Codespace, CPU only
- All versions match EXP-006 §3.

## 5. Evidence hashes (sha256, files committed in 95f37ef)
| File | sha256 |
|---|---|
| `render/frames_check/render.log` | `3efeef4caacbb21af7b0676af6ca3e4b06e146bf6ad0714c1c8744b879baa5ec` |
| `render/frames_check/SHA256SUMS` (hashes of the 10 PNG + 10 .ass) | `f2cea1e55f437f221398d73fd3dc6c8885f97d4d599fc0d0a97f7cc59b0cd4bc` |
| `render/frames_check/ENV.txt` | `2eb911ee1b0820d9f7265cbcaa28b7841dff4aa5d89e7571bcf25241ebf832d3` |
| `render/frames_check/strings_check.txt` (10/10 fingerprints OK, `ALL_MATCH=True`) | `58364e734a6ed54c694af8cdbd3d2ae51b00a5ed301ede663214b9225efac80d` |
| `experiments/exp006_render.py` (post-edit, see D3) | `8f08355430c836ddbfa21b2a0c5597bb13ccb7fe336b71ca81ce7ca07c46222c` |

The PNG hashes are listed in `render/frames_check/SHA256SUMS`. Engineering reported (H-0006 return) that `sha256sum -c` gave 20 OK. Research has not re-verified them, so that no image file is touched.

## 6. Metrics against thresholds
| Metric | Threshold pass / kill | Value | Outcome |
|---|---|---|---|
| `N_correct` | = 10 / ≤ 9 | not measured | n/a (INVALID) |
| `N_sev1` | = 0 / ≥ 1 | not measured | n/a (INVALID) |
| Verdict | PASS iff both pass | n/a | **INVALID** |

## 7. What we learned (null and invalid results count)
1. Noto Sans Arabic (v2.005, fonts-noto-core 20201225-2) does not contain ASCII Latin letters, `"` `(` `)` or U+2013. It does contain U+0020, ASCII digits, Arabic-Indic digits and ٪ ، ؟ ـ. Evidence level E3 for that fact (direct cmap measurement on our machine), confidence high.
2. libass + fontconfig fall back silently. Only the first missing glyph per event is logged, so a log grep is a lower bound, not a coverage check.
3. A detection check that was never shown to fire can report "none" while the event happens (D2). Every detector needs a positive control.
4. Process: a prereg locked before the Engineering and Creative consultation produced a design gap that consultation might have caught. EXP-008 is consulted before it is locked.

## 8. Follow-ups
- ASSUMPTIONS.md: proposed row A-11 ("FFmpeg + libass renders Arabic captions correctly on our caption style") stays **Untested**. EXP-006 provides no evidence. The test plan moves to EXP-008. (The row is added in a separate research-lead task, as stated in EXP-006.)
- Assurance: verify this file against `render/frames_check/SHA256SUMS`, `ENV.txt` and `render.log` (T2 review).
