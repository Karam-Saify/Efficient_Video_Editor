# RETURN H-0019
- **From:** assurance-lead
- **STATUS:** DONE
- **SUMMARY (≤5 lines):**
  The register now has 25 risks: 15 re-scored and 10 added (R-16..R-25), including the 3 Founder-named ones (R-16 font fallback, R-18 AI-only judging, R-19/R-20 hook gaps). Closed: none.
  Every row has exactly one owner position, a mitigation and a Check (date or gate). R-08's owner moved from Operator (not a position) to Assurance.
  Sev-1 (≥ 15): 11 risks. Six of them are new or raised this session.
  One mitigation claim was false: R-15 claims a "secret scan in CI", and none exists. No HALT condition was found.
- **ARTIFACTS (paths):** `/workspaces/Efficient_Video_Editor/company/state/RISK_REGISTER.md`
- **EVIDENCE (commands + outputs / metric files):**
  - Font fallback: `company/experiments/EXP-006-results.md` l.5-15 (INVALID; render.log l.135-136 fontselect → NotoSans-Regular).
  - Size mismatch and single judge: `company/experiments/EXP-008-results.md` l.2-5, 24-25, 32, 48 (FAIL, N_correct 8, N_sev1 0, 1.6× ratio, sole judge H-0016, uncalibrated 1.3× anchor).
  - Hook coverage: `company/gates/M0/hook-test.txt` has 11 cases and none is a shell write into a protected path. Report Threats l.40.
  - Cache, has_audio, validator residuals: H-0009-review N2, N3; H-0004-review F5-F7; H-0003-review F9 (RR-002).
  - Secret scan: `grep -i -E "secret|gitleaks|trufflehog" .github/workflows/*.yml` gives no match (the matrix 3.12/3.14 is present).
  - Footage: `ls samples/` shows README.md only.
  - Privacy: DATA_RIGHTS RR-012..RR-017 are all `pending`. `git ls-files | grep -i -E "trend|tti|exp-009"` gives no match.
  - Push state: `git status -sb` shows `## t2/install-company-os...origin/t2/install-company-os`, so the branch is level with origin.
- **DONE-WHEN CHECK:**
  - ✅ The 3 Founder-named risks are added: R-16 (silent font fallback / undeclared fonts), R-18 (AI-only Arabic judging), R-19 (shell writes bypass) and R-20 (false positives on quoted text). I split (c) into two rows because they need different checks and have different scores.
  - ✅ All risks are re-scored and have owners. Every row has L, I, Score, Was, one owner position and a Check.
  - ✅ LOG entry appended to `company/positions/05-assurance/LOG.md`.
- **Re-score changes:** lowered: R-02 15→10, R-03 16→12, R-04 12→8, R-08 15→10. Raised: R-13 9→12. Unchanged: R-01, 05, 06, 07, 09, 10, 11, 12, 14, 15 (R-10 was widened to cover the uncalibrated thresholds).
- **Added:** R-16 (16), R-17 Latin/digit size mismatch (15), R-18 (15), R-19 (15), R-20 (10), R-21 no usable footage (20), R-22 third-party data/privacy (15), R-23 stale stage cache (12), R-24 has_audio not filled (12), R-25 prereg locked before feasibility (9).
- **Closed:** none. R-02 was narrowed rather than closed.
- **Top 5 by score:** R-01 ASR dialect (20) · R-21 no usable footage (20) · R-12 bus factor (16) · R-16 silent font fallback (16) · then six tied at 15: R-05, R-10, R-17, R-18, R-19, R-22. Of these I rank **R-19** (protected-file bypass) and **R-18** (single AI judge) first for M0, because each can turn a gate result false without anyone noticing.
- **DEVIATIONS FROM BRIEF:** (1) Founder risk (c) is recorded as two rows (R-19, R-20). (2) Two columns were added, "Was" and "Check", so that every row shows its re-score and its check date or gate. (3) R-08's owner moved from Operator to Assurance, because the brief requires the owner to be a position.
- **OPEN QUESTIONS (numbered, with who should answer):**
  1. Founder: when will owned sample clips arrive? R-21 blocks EXP-001, and therefore R-01 and R-06.
  2. Founder: will you do the Arabic spot check (AR-02, 04, 05, 07, 08, 10) before STOP POINT 3? This is R-18.
  3. Engineering: should R-15 get a real CI secret-scan job, or should its mitigation text be corrected?
  4. Operator: should R-19 hold the M0 gate until H-0020 is verified with shell-write cases?
- **CONFIDENCE:** Medium (biggest reason for doubt: L and I scores are judgement on a 1–5 scale with no calibration data; the R-19 bypass was not exercised live, by design, because H-0020 is out of scope and the hook blocks such tests).
- **NEXT RECOMMENDED STEP:** at /close, the Operator informs the owners of the 11 Sev-1 rows through STATE. Assurance re-runs the hook self-test with shell-write and quoted-text cases on the H-0020 return.
