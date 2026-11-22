# RETURN H-0013
- **From:** engineering-lead
- **STATUS:** DONE (signed with objections G1–G3; all are wording fixes to the DRAFT, none blocks feasibility)
- **SUMMARY (≤5 lines):**
  The scratch probe reproduces all 10 §5.3 tagged-text rows exactly: runs, L count, tagged length and SHA-256/16. There are 0 mismatches, all raw fingerprints match §4, and no code point is class X.
  The `fc-query --format=%{charset}` coverage check works. All 10 strings report no missing code points, and C0 reports exactly `U+0E01 not in NotoSans-Regular.ttf`.
  A render of AR-05 tagged with `{\fnNoto Sans}` resolves the two runs to exactly the two declared files, with no `Glyph … not found` line. CTRL-01 fires rule (a) and rule (b), the latter on NotoSansThai-Regular.ttf. C2 on the EXP-006 log flags exactly AR-05, AR-08 and AR-10.
  E1 is confirmed as far as code and logs can show it. Final visual confirmation of order and mirroring stays with Creative's judging.
  Three exact-text changes are requested below (G1 paths, G2 regex, G3 log text).
- **ARTIFACTS (paths):**
  - Sign-off line: `company/experiments/EXP-008.md` (Consultation block, Engineering line). This is the only edit made to that file.
  - Probe (scratch, not committed): `/tmp/claude-1000/-workspaces-Efficient-Video-Editor/aaad3156-5fc0-4481-9dd9-f8ade7986944/scratchpad/h0013/probe.py`. The outputs are `probe_run1.txt` and `probe_run2.txt` in the same folder, and `out/*.{ass,png,log}`. The probe reuses only `table_rows`, `fingerprint`, `IDS`, `QA` and `ASS_TEMPLATE` from `experiments/exp006_render.py`, imported with `-B` so the repo is not modified.
- **EVIDENCE (commands + outputs / metric files):**
  - `.venv/bin/python -B <scratch>/h0013/probe.py`. Output excerpt:
    ```
    AR-04 OK ('A6 L3 A10', 3, 54, 'ea7a2ee3ba9338bc') raw (19, 'fbe1a2e4e5940fb6') miss []
    AR-05 OK ('A5 L13 A7', 13, 60, 'eb85fb62231afbce') raw (25, '44a815ac352fe4cc') miss []
    AR-08 OK ('L1 A6 L1 A2 L1 A5 L1', 4, 136, '5b8d2ec0094a6c3e') raw (17, 'ce169e962acb9906') miss []
    AR-10 OK ('A8 L1 A5', 1, 49, '1b138b96859dc198') raw (14, 'd8d6e1db7de33132') miss []
    (AR-01/02/03/06/07/09 OK, equal to raw)
    CTRL-01 21 2f344988a2bbdda1 C0: ['U+0E01 not in NotoSans-Regular.ttf']
    MISMATCHES 0
    -- AR-05_tagged: ruleA=0 undeclared=[]
        fontselect: (Noto Sans Arabic, 400, 0) -> /usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf, 0, NotoSansArabic-Regular
        fontselect: (Noto Sans, 400, 0) -> /usr/share/fonts/truetype/noto/NotoSans-Regular.ttf, 0, NotoSans-Regular
    -- CTRL-01: ruleA=1 undeclared=['/usr/share/fonts/truetype/noto/NotoSansThai-Regular.ttf']
        fontselect: (Noto Sans, 400, 0) -> /usr/share/fonts/truetype/noto/NotoSansThai-Regular.ttf, 0, NotoSansThai-Regular
        Glyph 0xE01 not found, selecting one more font for (Noto Sans, 400, 0)
    -- AR-04_raw_arabicfont:               png sha16 d86334cc7b5dbbaf
    -- AR-04_redundant_tags_at_boundaries: png sha16 d86334cc7b5dbbaf
    -- AR-04_redundant_tag_midword:        png sha16 d86334cc7b5dbbaf
    ```
  - A second run was byte-identical to the first. All outputs and hashes matched, which the shell printed as `DETERMINISTIC_SAME`.
  - ffprobe on all 5 probe PNGs gave `png,1080,1920,rgb24` (×5). No PNG was viewed or sent to any LLM. Only hashes and ffprobe output were used.
  - C2 check, an inline script over `render/frames_check/render.log` that attributes events by `Added subtitle file:` and applies rules (a) and (b): `C2 flagged: ['AR-05', 'AR-08', 'AR-10']`. In this log only rule (a) fires, because the fallback file (NotoSans-Regular) is now declared. That is enough for C2.
- **DONE-WHEN CHECK:**
  - E1, the `\fn` run-split and bidi assumption: ✅ confirmed, within the limits below.
    - Tags that do not change the font have no effect on the output. Three AR-04 variants (no tags, tags at the 250 boundaries, a tag between two joining letters inside السعر) give one identical PNG hash, `d86334cc7b5dbbaf`. So in libass 0.17.1 the override tags by themselves do not reorder, re-shape or split the text. Only an actual font change starts a new HarfBuzz run.
    - The joining claim holds by construction. Every §5.3 switch has an L code point on one side, and all L ranges have Joining_Type U (non-joining). ZWJ and ZWNJ (U+200C/D) fall in class X, so they cannot occur. No Arabic joining pair can be split across fonts.
    - That FriBidi resolves the whole event at once (not each `\fn` run separately) comes from libass's design, where bidi levels are computed per paragraph and runs are then split by font and level. I did not prove it from pixels. Creative's AR-05, AR-08 and AR-10 order and mirroring checks are the empirical test.
  - E2, exact reproducibility of §5.3: ✅ 0 mismatches across all 10 rows and CTRL-01 (21 code points, `2f344988a2bbdda1`).
  - E3, the fc-query charset as coverage source: ✅ it works with no new dependency. The output is space-separated hex ranges (`20-7e a0-377 …`), which the probe parses. I recommend the instrument fail loudly if fc-query returns empty output or more than one face.
  - E4, per-string logs and the rule regexes: ✅ both match libass 0.17.1 output at ffmpeg's default log level, and `fontselect` lines are visible. Two notes:
    - In CTRL-01.log the `Glyph … not found` line comes after the fallback `fontselect` line. The checker must therefore not depend on line order. With one log per string, it does not need to.
    - Fixes G2 and G3 are needed (see below).
  - E5, CTRL-01 triggers the fallback: ✅ rule (a) and rule (b) both fire, with NotoSansThai-Regular.ttf as the undeclared file.
  - Probe in scratch only, not in render/, no images viewed: ✅. `ls render/` shows only `frames_check/`.
- **REQUESTED CHANGES (exact text, for research-lead to apply):**
  - **G1, paths.** In every place, replace `render/exp007/` with `render/exp008/` and `experiments/exp007_render.py` with `experiments/exp008_render.py`. The occurrences are on lines 56, 67, 107, 112, 116, 120, 121, 124, 174 ("from a clean `render/exp007/`") and 201 (`grep -n exp007 company/experiments/EXP-008.md`). The control path becomes `render/exp008/control/CTRL-01.{ass,png,log}`. I keep the `render/expNNN/` layout rather than `render/frames_check_exp008/` because §5.1 precondition 3 already relies on that layout.
  - **G2, rule (b).** In §5.4 step 7, replace "A `fontselect` request whose result is "not found" or empty also counts." with:
    > A line matching the case-insensitive regex `fontselect: failed to find any fallback` also counts as rule (b), and so does any `fontselect:` line that has no ` -> ` or whose captured path is empty.
  - **G3, log wording.** In §5.5 "Why this character", replace `Glyph 0xe01 not found, selecting one more font for (Noto Sans, 400, 0)` with `Glyph 0xE01 not found, selecting one more font for (Noto Sans, 400, 0)` (measured 2026-11-22, H-0013). The regex in rule (a) is already case-insensitive, so this changes wording only.
  - Optional, not a condition of my sign-off. In §5.4 step 3, after "no new dependency.", add: "The instrument fails (INVALID) if `fc-query` returns no charset or more than one face for a declared file."
- **DEVIATIONS FROM BRIEF:** none. I imported read-only helpers from `experiments/exp006_render.py` with `python -B` instead of copying them. No repo file other than the sign-off line, this return and LOG.md was touched.
- **OPEN QUESTIONS:**
  1. (research-lead) Apply G1–G3 before lock. Do they count as edits that require Creative to re-sign? I think not, because they are path and wording changes only.
  2. (engineering, later brief) The §8 external-validity row says `src/render` should implement §5.3. That needs its own T2 brief, with fixtures built from the §5.3 table.
- **CONFIDENCE:** High for E2–E5, which were measured. Medium for E1's whole-event bidi claim. It rests on libass's design and on a test showing that tags alone change nothing, not on a pixel test of the font-switch case, and Creative's judging settles that.
- **NEXT RECOMMENDED STEP:** research-lead applies G1–G3 and locks EXP-008. The Operator then briefs engineering-lead to write `experiments/exp008_render.py` and run §5.4 steps 1–9. The probe's classifier and coverage functions can be ported to it as they are.
