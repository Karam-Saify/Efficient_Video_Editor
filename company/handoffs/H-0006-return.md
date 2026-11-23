# RETURN H-0006
- **From:** engineering-lead
- **STATUS:** DONE (render step only; not judged. One finding Research must classify before H-0007: libass font fallback for 3 non-Arabic glyphs, see Deviations / Q1)
- **SUMMARY (≤5 lines):**
  - All 3 EXP-006 §5.1 preconditions checked and held. I then ran the §5.3 steps 1 to 4 with the §5.2 parameters, using `experiments/exp006_render.py`, which reads the strings programmatically from ARABIC_QA.md.
  - All 10 string fingerprints match the EXP-006 §4 table, and the Dialogue text read back from each `.ass` is identical to the prereg text. Result: 10 PNGs, each png/1080x1920/rgb24.
  - I ran the full procedure twice into a fresh directory each time. The SHA256SUMS were byte-identical across runs: 10 PNGs + 10 `.ass`. The second run's outputs are kept as final.
  - render.log shows font fallback for AR-05 (U+0069 'i'), AR-08 (U+0022 '"') and AR-10 (U+2013 '–'). Those glyphs came from `NotoSans-Regular.ttf` (Latin Noto Sans). All Arabic glyphs came from `NotoSansArabic-Regular.ttf`.
  - Nothing was judged. No image was viewed or sent to an LLM: only ffprobe, stat and sha256 were used.
- **ARTIFACTS (paths):**
  - `experiments/exp006_render.py` (new, untracked; sha256 8f083554…6222c after the post-run lint fix, see Deviations)
  - `render/frames_check/ENV.txt`, `strings_check.txt`, `render.log`, `SHA256SUMS`, `AR-01.ass … AR-10.ass`, `AR-01.png … AR-10.png` (run 2, final)
  - Run 1 copy for comparison: `/tmp/claude-1000/-workspaces-Efficient-Video-Editor/aaad3156-5fc0-4481-9dd9-f8ade7986944/scratchpad/run1/` (scratch, not durable)
- **EVIDENCE (commands + outputs / metric files):**
  - Preconditions:
    - 5.1.1: RR-001 in DATA_RIGHTS.md is recorded as "SIL OFL 1.1 … Yes … 2026-11-22 (H-0002, recorded)". The script also checks this: the row must exist, must not say "pending", and must contain "Yes".
    - 5.1.2: `fc-match "Noto Sans Arabic"` → `NotoSansArabic-Regular.ttf: "Noto Sans Arabic" "Regular"`; the file is `/usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf`, sha256 `504d7407d86875acf7d04dfaa0fd7524d0b8797723bc4aa18022f29db25b0b6e`, which matches the RR-001 prefix 504d7407…b6e.
    - 5.1.3: `render/` was absent before run 1 (`ls: cannot access 'render'`). The script refuses to run if the directory is non-empty. Run 1 was moved to the scratchpad before run 2.
  - Environment (ENV.txt): ffmpeg 6.1.1-3ubuntu5, libass9 1:0.17.1-2build1, libharfbuzz0b 8.3.0-2build2, libfribidi0 1.0.13-3build1, fonts-noto-core 20201225-2, kernel 6.8.0-1070-azure, nproc 2. render.log also reports `libass source: tarball: 0.17.1` and `Shaper: FriBidi 1.0.13 (SIMPLE) HarfBuzz-ng 8.3.0 (COMPLEX)`. All match the §3 versions.
  - strings_check.txt: AR-01..AR-10 all `OK`, `ALL_MATCH=True`. Each string's count and sha256_16 equal the §4 values (e.g. `AR-05 OK codepoints=25 (expected 25) sha256_16=44a815ac352fe4cc`). U+ code points and UTF-8 hex are listed per string. The checks also confirm: no BOM, no CR, one Dialogue line, no `{}\`.
  - Renders: 10 × `exit=0` in render.log; wall time 2.6 s per full run.
  - ffprobe (`ffprobe -v error -select_streams v:0 -show_entries stream=codec_name,width,height,pix_fmt -of csv=p=0`) + size:
    ```
    AR-01 png,1080,1920,rgb24 20624B
    AR-02 png,1080,1920,rgb24 20016B
    AR-03 png,1080,1920,rgb24 20317B
    AR-04 png,1080,1920,rgb24 20997B
    AR-05 png,1080,1920,rgb24 25063B
    AR-06 png,1080,1920,rgb24 17146B
    AR-07 png,1080,1920,rgb24 16294B
    AR-08 png,1080,1920,rgb24 22247B
    AR-09 png,1080,1920,rgb24 13558B
    AR-10 png,1080,1920,rgb24 18110B
    ```
  - Determinism: `diff run1/SHA256SUMS render/frames_check/SHA256SUMS` → identical (SHA256SUMS_IDENTICAL). `sha256sum -c render/frames_check/SHA256SUMS` → 20 OK. strings_check.txt is identical across runs. render.log differs only in heap pointers and ffmpeg progress-line interleaving. ENV.txt differs only in the date line.
  - PNG sha256 (both runs): AR-01 4f3512da…0771, AR-02 3fec42b0…55eb, AR-03 d6bae2b4…6b81, AR-04 d86334cc…4ce9, AR-05 60f170c9…ee29, AR-06 bda6b84c…adf, AR-07 2a2e97a6…6f67, AR-08 08de7a25…f4f3, AR-09 77e9bcaa…a0a, AR-10 969635a9…66e7. Full values are in `render/frames_check/SHA256SUMS`.
  - Step 4, font fallback (taken from render.log, mapped per ID):
    ```
    AR-05: Glyph 0x69 not found, selecting one more font for (Noto Sans Arabic, 400, 0) -> NotoSans-Regular.ttf
    AR-08: Glyph 0x22 not found, selecting one more font ... -> NotoSans-Regular.ttf
    AR-10: Glyph 0x2013 not found, selecting one more font ... -> NotoSans-Regular.ttf
    ```
    The fallback font is `/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf`, sha256 `89c3c497f618fdaa0b2d1e98fef93582f28c71debd2c4a8cdf41f190ced2909d`, from the same fonts-noto-core package. libass logs only the first missing glyph per event, so the other Latin letters in AR-05 ("Phone", "Pro") probably come from the same fallback font. That is unverified. The other 7 strings have no fallback. Arabic glyphs in every string come from NotoSansArabic-Regular.ttf.
  - Lint: `.venv/bin/ruff check experiments/exp006_render.py` → All checks passed.
- **DONE-WHEN CHECK:**
  - ✅ 10 PNGs, each 1080×1920. The ffprobe output is pasted above.
  - ✅ The log has versions, font hash and code points. Per the Operator's instruction, the prereg file set (ENV.txt + strings_check.txt + render.log + SHA256SUMS) replaces run_log.txt. The font hash is recorded in this return, not in ENV.txt, because §5.3 step 1 does not list it.
  - ✅ Rerun regenerates identical PNGs: SHA256SUMS is byte-identical across 2 full runs.
  - ✅ Entry appended to `company/positions/03-engineering/LOG.md`.
- **DEVIATIONS FROM BRIEF:**
  1. run_log.txt is replaced by the EXP-006 §5.3 file set, as the Operator instructed. Not a deviation from EXP-006.
  2. **EXP-006 step 4 finding, which Research must classify; I make no judgement.** Font fallback to NotoSans-Regular.ttf for U+0069, U+0022 and U+2013. §8 lists "different font file resolved" as invalidating, but precondition 5.1.2 (fc-match) held, and step 4 says only "record any in the results". Whether this is invalidating, non-invalidating or expected (the threats table names "silent font fallback" as an internal threat) is Research's call.
  3. Script edited after the final run. In run 1 and run 2, the step-4 warning regex (`fallback|glyph not found`) did not match libass's actual wording ("Glyph 0x69 not found"), so the script's stdout said "warnings: none". That was wrong. I found the fallback by grepping render.log by hand. After run 2 I widened the regex and ran `ruff format`; both changes affect stdout and layout only, not any output file. I did not run a third time (only one rerun is left under the §8 rule, so I kept it). The current script is therefore not byte-identical to the one that produced the outputs. Assurance can verify it with the repro command below, after moving `render/frames_check/` aside, before H-0007 judging starts.
  4. Re-execution rule: the procedure ran 2 times in total (the original run plus 1 rerun, done for the determinism check, as instructed). No PNG has been judged or shown to anyone.
- **REPRODUCTION (one line, repo root; requires `render/frames_check/` absent or empty):**
  `mv render/frames_check /tmp/fc_prev 2>/dev/null; .venv/bin/python experiments/exp006_render.py && diff /tmp/fc_prev/SHA256SUMS render/frames_check/SHA256SUMS && echo IDENTICAL`
- **OPEN QUESTIONS (numbered, with who should answer):**
  1. research-lead: is the libass fallback to NotoSans-Regular.ttf (AR-05, AR-08, AR-10) invalidating under §8, or a recorded non-invalidating observation? This must be decided before H-0007 starts, because no rerun is allowed once judging begins.
  2. assurance-lead: NotoSans-Regular.ttf (Latin) is now used in output but is not in DATA_RIGHTS. It comes from the same package (likely OFL 1.1) and needs its own RR row.
  3. Operator: `render/` is not git-ignored, and `.gitignore` has no `*.png` rule. Should these 20 small files (about 200 KB total) be committed as experiment evidence, or ignored? I committed nothing.
  4. Operator/Assurance: should a third verification run be done now with the edited script (the last allowed rerun) so that the committed script is the one that produced the outputs?
- **CONFIDENCE:** High that the render matches the §5 procedure and is deterministic. Medium on validity, because the fallback classification (Q1) is open.
- **NEXT RECOMMENDED STEP:** Research classifies Q1. If it is not invalidating, the Operator briefs creative-lead for H-0007 with `render/frames_check/AR-*.png` and SHA256SUMS. Engineering should not describe the images.
