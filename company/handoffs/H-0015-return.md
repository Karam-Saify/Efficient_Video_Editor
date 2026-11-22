# RETURN H-0015
- **From:** engineering-lead
- **STATUS:** DONE (uncommitted, on branch `t2/install-company-os`; T2, waits for Assurance)
- **SUMMARY (≤5 lines):**
  `experiments/exp008_render.py` runs EXP-008 §5.4 steps 1–9 as locked. All four §5.1 preconditions pass, the 10 raw and tagged fingerprints match (ALL_MATCH=True) and COVERAGE_OK=True with 0 missing code points.
  All three controls fire: C0 reports exactly `U+0E01 not in NotoSans-Regular.ttf`, C1 hits rule (a) and rule (b) on NotoSansThai-Regular.ttf, and C2 flags exactly AR-05, AR-08 and AR-10. CTRL_OK=True.
  All 10 logs are CLEAN (LOG_OK=True). Each one resolves exactly the declared file set, and no undeclared font appears for AR-01..10. All 10 PNGs are png/1080×1920/rgb24, and the instrument hash is the same at step 1 and step 9.
  I ran the procedure twice from a clean `render/exp008/`. Every PNG, .ass and check file is byte-identical between the runs. The raw ffmpeg `.log` files are not, because of ffmpeg pointer addresses and progress-stat lines (see Deviations).
  Nothing was judged or viewed. The ready-to-judge files are `render/exp008/AR-01.png` … `AR-10.png`. The control is separate, in `render/exp008/control/`.
- **ARTIFACTS (paths):**
  - Instrument: `experiments/exp008_render.py` (sha256 `c98d1c699ade6b94fb941711d120f1c81ec9de0a3f6d9547eece5ff55b660af6`)
  - Unit test (run-splitter): `tests/unit/test_exp008_splitter.py` (17 tests)
  - Output dir (run 2, final): `render/exp008/`, which holds `AR-01..AR-10.{ass,png,log}`, `control/CTRL-01.{ass,png,log}`, `ENV.txt`, `strings_check.txt`, `coverage_check.txt`, `logcheck.txt`, `ffprobe.txt` and `SHA256SUMS` (38 entries)
  - Run 1 copy, used for the comparison and kept out of the repo: `/tmp/claude-1000/-workspaces-Efficient-Video-Editor/aaad3156-5fc0-4481-9dd9-f8ade7986944/scratchpad/h0015/run1/`
- **RERUN COMMAND (one line, from the repo root, needs an empty `render/exp008/`):**
  `rm -rf render/exp008 && .venv/bin/python experiments/exp008_render.py && sha256sum -c render/exp008/SHA256SUMS 2>&1 | grep -v '\.log: \|ENV.txt: '`
  Expected output: `COVERAGE_OK=True CTRL_OK=True LOG_OK=True PNG_OK=True INSTRUMENT_UNCHANGED=True`, and every PNG, .ass and .txt line reports `OK`. The logs and ENV.txt differ by design (see Deviations).
- **EVIDENCE (commands + outputs / metric files):**
  - Run 1 and run 2 both printed `COVERAGE_OK=True CTRL_OK=True LOG_OK=True PNG_OK=True INSTRUMENT_UNCHANGED=True`, `done: render/exp008`, with EXIT=0. Each run took 2.3 s wall time.
  - Preconditions are checked in code, `preconditions()`, which stops with exit 2 on any failure:
    - RR-001 and RR-011 are recorded with commercial use Yes.
    - `fc-match -v` gives exactly `/usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf` and `/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf`, and both sha256 values match §5.1 (see ENV.txt).
    - `render/exp008/` was empty, and `git status --porcelain render/frames_check` was empty.
    - The prereg is LOCKED with both sign-offs.
  - `strings_check.txt`: 10× `OK` and `ALL_MATCH=True`. Runs, L counts, tagged lengths and SHA-256/16 all equal the §5.3 table, which is parsed from EXP-008.md, not retyped. The file lists each code point with its class and file.
  - `coverage_check.txt`:
    ```
    AR-01..AR-10  missing=[]   (all 10)
    COVERAGE_OK=True
    CTRL-01  missing=['U+0E01 not in NotoSans-Regular.ttf']  expected=['U+0E01 not in NotoSans-Regular.ttf']  C0_OK=True
    ```
  - `logcheck.txt` (controls):
    ```
    C2 flagged=['AR-05', 'AR-08', 'AR-10'] expected=['AR-05', 'AR-08', 'AR-10'] C2_OK=True
    == C1 CTRL-01  FLAGGED=True  rule_a=1  rule_b=1  files=['NotoSans-Regular.ttf', 'NotoSansArabic-Regular.ttf', 'NotoSansThai-Regular.ttf']
        rule(a)    | Glyph 0xE01 not found, selecting one more font for (Noto Sans, 400, 0)
        rule(b)    | fontselect: (Noto Sans, 400, 0) -> /usr/share/fonts/truetype/noto/NotoSansThai-Regular.ttf, 0, NotoSansThai-Regular
    C1 rule_a_fired=True rule_b_fired=True fontselect_visible=True C1_OK=True
    CTRL_OK=True
    ```
  - `logcheck.txt` (real strings): AR-01, 02, 03, 06, 07 and 09 have `FLAGGED=False rule_a=0 rule_b=0 files=['NotoSansArabic-Regular.ttf'] CLEAN=True`. AR-04, 05, 08 and 10 have `FLAGGED=False rule_a=0 rule_b=0 files=['NotoSans-Regular.ttf', 'NotoSansArabic-Regular.ttf'] CLEAN=True`. Result: `LOG_OK=True`.
  - `ffprobe.txt`: 10× `png,1080,1920,rgb24`, then `PNG_OK=True` and `INSTRUMENT_UNCHANGED=True` (step 1 = step 9 = `c98d1c69…0af6`). CTRL-01.png also gives `png,1080,1920,rgb24`.
  - Two-run comparison: `diff <(grep -v ENV.txt run1/SHA256SUMS) <(grep -v ENV.txt render/exp008/SHA256SUMS)` shows differences only on the 11 `.log` lines. All 10 PNGs, 11 .ass files, CTRL-01.png and the four check .txt files are byte-identical. That includes `logcheck.txt`, so every fontselect and Glyph line is identical too. ENV.txt differs only in the `date -u` line (17:15:09Z vs 17:15:20Z).
  - Comparing hashes with `render/frames_check/SHA256SUMS` (hash lines only, no image opened): the AR-01, 02, 03, 06, 07 and 09 PNGs are byte-identical to EXP-006, and AR-04, 05, 08 and 10 differ. This is exactly what §5.3 predicts, and it is non-invalidating under §8.
  - `.venv/bin/ruff check .` gives `All checks passed!`. `.venv/bin/python -m pytest -q` gives `125 passed, 8 skipped`. The 8 skips are the existing full-runtime-lock checks in `test_runtime_imports.py`, and they predate this brief.
- **DONE-WHEN CHECK:**
  - ✅ All §5.1 preconditions pass (code-checked, see above, and ENV.txt).
  - ✅ The coverage check reports 0 missing for AR-01..10 (`coverage_check.txt`, COVERAGE_OK=True).
  - ✅ Controls are detected as specified: C0, C1 (rule a + b, fontselect visible) and C2 exact, so CTRL_OK=True.
  - ✅ 10 PNGs at 1080×1920 (`ffprobe.txt`).
  - ✅ The two runs are identical for every image, .ass and check file. ⚠ The raw ffmpeg logs are not byte-identical (Deviation 1).
  - ✅ ruff and pytest are green.
  - ✅ LOG entry appended to `company/positions/03-engineering/LOG.md`.
- **DEVIATIONS FROM BRIEF:**
  1. **The raw `.log` files are not byte-identical across runs.** The locked §5.4 step 8 command keeps the default log level and the stats output, and I may not add `-nostats`. Two things therefore vary between runs:
     - the `[Parsed_ass_0 @ 0x…]` context pointers (ASLR);
     - ffmpeg's timing-dependent progress lines (`frame=… speed=N/A` vs `speed=0x`, and whether a `frame=0` stats line is printed before a warning).

     After normalising the pointers, 5 of 11 logs still differ, and only in those stats lines. Neither kind of line is rule (a) or rule (b). `logcheck.txt`, which strips the pointer prefix, is byte-identical. This is non-invalidating under §8 ("log warnings that are neither rule (a) nor rule (b)"). Research should record it in the results.
  2. **"Two runs".** The brief requires two full runs, and EXP-008 §8 talks about re-execution only after an execution error. I ran the identical procedure twice before anything was judged. I moved run 1 out to scratch so that run 2 started from an empty `render/exp008/` (precondition 3). Run 2 is the final output. Neither run hit an error, and no instrument fix was made, so 0 of the 2 allowed fixes were used.
  3. **Interpreting U+061C.** The §5.3 A row covers U+0600–U+06FF, but the X row names U+061C explicitly. The instrument treats U+061C as X, so the explicit example wins and the instrument fails loudly. U+061C occurs in none of the 10 strings, so this changes no output.
  4. **Extra file `render/exp008/ffprobe.txt`.** It holds the step 9 ffprobe and instrument-hash result, and it is listed in SHA256SUMS. §5.4 names no file for these.
- **OPEN QUESTIONS (numbered, with who should answer):**
  1. (research-lead) Record Deviation 1 (log non-determinism from pointers and stats) and Deviation 3 (U+061C overlaps the A range and the X list in §5.3) in `EXP-008-results.md`. Any future EXP that wants byte-identical logs should add `-nostats` to its locked command.
  2. (assurance-lead) For the reproducibility check, use `sha256sum -c render/exp008/SHA256SUMS` excluding the `.log` and ENV.txt lines, and compare `logcheck.txt` as the deterministic summary of the logs.
- **CONFIDENCE:** High. Every gate is code-checked and passed twice. The biggest remaining doubt is outside this brief: the fc-query charset vs the real cmap. That is mitigated, because the log check agrees, with 0 rule (a) hits.
- **NEXT RECOMMENDED STEP:** Assurance reviews the H-0015 diff, which is the instrument and test plus `render/exp008/`, using the rerun command above. After ACCEPT and merge, the Operator briefs creative-lead to judge `render/exp008/AR-01..AR-10.png` (step 10). The control PNG must not be shown.
