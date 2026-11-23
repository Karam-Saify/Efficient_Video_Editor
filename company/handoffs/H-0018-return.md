# RETURN H-0018
- **From:** research-lead
- **STATUS:** DONE
- **SUMMARY (≤5 lines):**
  EXP-008 verdict FAIL is confirmed against the locked rule (N_correct 8 ≤ 9 = kill; N_sev1 0). Evidence level E2, no downgrade: no deviation affects validity.
  Limited claim: FFmpeg 6.1.1 + libass 0.17.1, §5.2 style, declared Noto pair, §5.3 rule, 10 strings does not pass. Failed: cross-font size matching only (Latin caps / ASCII digits 1.61–1.63× alef vs 1.3× limit).
  Passed inside the run: per-run font assignment (code-checked, High), Arabic shaping and bidi (single AI judge, Medium).
  Successor named EXP-010 (per-font scale factor for the Latin font in the caption `style` definition); not drafted.
  Recommendation: the Founder calibrates the 1.3× anchor (upper and lower band) before EXP-010 is locked.
- **ARTIFACTS (paths):**
  - `company/experiments/EXP-008-results.md` §8 "Research analysis" (appended), plus the header "Evidence level" placeholder filled
  - `company/positions/02-research/LOG.md` (entry appended)
- **EVIDENCE (commands + outputs / metric files):**
  - Metric values from `company/experiments/EXP-008-results.md` §3–§4 (Creative) and gates from `company/handoffs/H-0015-return.md` (`COVERAGE_OK=True CTRL_OK=True LOG_OK=True PNG_OK=True INSTRUMENT_UNCHANGED=True`).
  - Locked rule and E2 clause: `company/experiments/EXP-008.md` §6, §7; deviation policy §8.
  - Deviations D1 (raw-log non-determinism) and D2 (U+061C) from H-0015 Dev. 1 and 3.
  - Free id: `grep -rln "EXP-010" --include=*.md --include=*.py --include=*.json .` gave no hits; EXP-007 reserved (PLAYBOOK register), EXP-009 referenced in `company/positions/05-assurance/DATA_RIGHTS.md` RR-014.
  - A-11 absent: `grep -n "A-1[01]" company/state/ASSUMPTIONS.md` shows only A-10.
- **DONE-WHEN CHECK:**
  - ✅ Verdict confirmation against the locked rule: §8.1 table.
  - ✅ Evidence level and exact, limited claim (passed: shaping, bidi, per-run font assignment; failed: cross-font size matching): §8.2.
  - ✅ Engineering deviations (raw logs; U+061C) and validity effect: §8.3, both non-invalidating, no downgrade.
  - ✅ Threats (single AI judge; uncalibrated 1.3×): §8.4.
  - ✅ Successor named with a free id, not drafted: §8.5, EXP-010.
  - ✅ Founder calibration recommendation: §8.5, yes, before the EXP-010 lock.
  - ✅ Creative's table not altered; no images viewed; no commit.
- **DEVIATIONS FROM BRIEF:**
  1. Besides appending §8, I replaced the header placeholder line "Evidence level: *(research-lead adds this after the judging…)*" with "E2 … see §8". That placeholder was reserved for Research by H-0016; no Creative content was touched.
- **OPEN QUESTIONS (numbered, with who should answer):**
  1. (Founder) Calibrate the acceptable Latin cap / ASCII digit height band relative to alef before EXP-010 is locked, on explore stills (not EXP-010 outputs). Who prepares the stills: Engineering in `company/experiments/explore/`?
  2. (Operator) Add A-11 to `company/state/ASSUMPTIONS.md` with status "Refuted for this configuration (E2, EXP-008)" (SOP-R3.4), and register EXP-010 in the PLAYBOOK register.
  3. (assurance-lead) T2 review of the results and §8 (SOP-R3.5).
- **CONFIDENCE:** High for the FAIL and its cause (pixel-measured, 0.3× above the limit, deterministic). Medium for the "passed" observations (biggest reason for doubt: single AI judge, no agreement measure).
- **NEXT RECOMMENDED STEP:** assurance-lead reviews H-0018; then Founder calibration; then research-lead drafts EXP-010 with Engineering and Creative consulted.
