# RETURN H-0010
- **From:** research-lead
- **STATUS:** DONE (EXP-007 is a DRAFT on purpose. It must not be locked until the Engineering and Creative sign-offs are in, and the ID collision in Q1 is resolved.)
- **SUMMARY (≤5 lines):**
  - `EXP-006-results.md` records verdict **INVALID**, with no PASS or FAIL. It gives the reason (fallback to undeclared NotoSans-Regular.ttf for AR-05/08/10, with the full charset gap), deviations D1 to D5 (including the missed fallback detection and the script edit after run 2), the evidence hashes, and the fact that no PNG was judged or viewed.
  - `EXP-007.md` DRAFT: declared pair Noto Sans Arabic + Noto Sans with file paths and sha256; an exact 3-step run-splitting rule (classes A/L/S/X, a space rule, explicit `{\fnNoto Sans}` / `{\fnNoto Sans Arabic}` tags); an expected tagged-text table with fingerprints for all 10 strings; a coded pre-render coverage check; per-string logs; and log-check rules (a)/(b).
  - Controls: C0 (coverage check on the control), C1 (rendered known-fallback CTRL-01 = `مرحبا {\fnNoto Sans}ก`, U+0E01 in neither declared font), and C2 (log checker rerun on the EXP-006 log must flag exactly AR-05/08/10). The pass rule and the §6 "correct" definition are unchanged.
  - ASS/libass can express per-run fonts (`\fn` override), so there was no reason to escalate. The bidi-unaffected assumption is listed for Engineering to confirm (item E1).
- **ARTIFACTS (paths):**
  - `company/experiments/EXP-006-results.md` (new)
  - `company/experiments/EXP-007.md` (new, `**Lock:** DRAFT`)
  - `company/positions/02-research/LOG.md` (entry appended)
- **EVIDENCE (commands + outputs / metric files):**
  - Coverage, measured with `fc-query --format='%{charset}'` on both font files and a scratch script over the 10 ARABIC_QA strings. Noto Sans Arabic lacks U+0022 U+0028 U+0029 U+0050 U+0065 U+0068 U+0069 U+006E U+006F U+0072 U+2013. Noto Sans covers all of them. All 39 Arabic-block code points are in Noto Sans Arabic, and none are in Noto Sans. U+0020 and ASCII digits are in both.
  - Control candidate: U+0E01 is in neither declared file. `fc-list ':charset=0e01'` lists `NotoSansThai-Regular.ttf` (undeclared).
  - `fc-match "Noto Sans"` → `/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf`. The sha256 values of both font files match RR-001 and RR-011.
  - The tagged-text fingerprints in EXP-007 §5.3 come from a scratch implementation of the rule (scratchpad, not repo code). For example, AR-05 is 60 code points, `eb85fb62231afbce`.
  - Evidence hashes in EXP-006-results §5: render.log `3efeef4c…a5ec`, SHA256SUMS `f2cea1e5…d4bc`, ENV.txt `2eb911ee…32d3`, strings_check.txt `58364e73…80d`, exp006_render.py `8f083554…222c`.
  - `git diff --stat -- company/experiments/EXP-006.md` → empty, so EXP-006 was not edited.
- **DONE-WHEN CHECK:**
  - ✅ EXP-006-results.md records INVALID with evidence (§1, §2, §5).
  - ✅ EXP-007.md drafted (DRAFT), with font pair (§5.1), run-splitting rule (§5.3), coverage check (§5.4 step 3), fallback control (§5.5), pass rule (§6), deviations policy (§8) and consultation block (end of file).
  - ✅ LOG.md entry appended.
- **DEVIATIONS FROM BRIEF:**
  - I added a second, no-render log-check control (C2: replay the checker on the EXP-006 log) and a coverage-check control (C0), on top of the one rendered control the brief asked for. They cost nothing and validate the detector against a real observed failure.
  - Per-string logs replace the single combined render.log. This is the only render-procedure change besides paths and Dialogue text.
  - No rendering, no images, no repo code. Scratch scripts only, used to measure coverage and compute fingerprints. PNGs were not opened.
- **OPEN QUESTIONS (numbered, with who should answer):**
  1. **Operator:** "EXP-007" is already reserved for "Revision diff size and tokens" (M4) in `company/positions/02-research/PLAYBOOK.md` l.55, ROADMAP 4.2 and ASSUMPTIONS A-05. Either renumber the M4 experiment, or I rename this draft before lock. ROADMAP is outside my rights.
  2. **engineering-lead:** sign items E1 to E5. E1 is the most important: do `\fn` tags leave FriBidi ordering and `Encoding: -1` unaffected in libass 0.17.1?
  3. **creative-lead:** sign items C1 to C3. Should a visible mismatch between the two fonts (size, weight, baseline) in AR-04/05/08/10 count as a defect of the tested property?
  4. **research-lead (later task):** add A-11 to ASSUMPTIONS.md, and record the new prereg checklist item "every code point is covered by its assigned font".
- **CONFIDENCE:** Medium-High. The coverage facts and fingerprints are measured. The biggest doubt is the libass behaviour at font switches (item E1), which I inferred and did not test.
- **NEXT RECOMMENDED STEP:** The Operator resolves Q1 and briefs Engineering and Creative to sign the consultation block. Research then locks EXP-007, Assurance reviews it, and Engineering runs the render brief.

> **Operator note 2026-11-22:** Q1 resolved. The draft is renumbered to `company/experiments/EXP-008.md`, because EXP-007 stays reserved for M4. References to "EXP-007" above mean EXP-008.
