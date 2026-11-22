# RETURN H-0016
- **From:** creative-lead
- **STATUS:** DONE (uncommitted; T2, waits for research-lead to add the evidence level and for the assurance-lead review)
- **SUMMARY (≤5 lines):**
  I judged the 10 EXP-008 PNGs at 200% against the raw ARABIC_QA strings, following §5.4 step 10 and §6 with O1 and O2. Result: **N_correct = 8, N_sev1 = 0, verdict FAIL** under the locked rule.
  AR-04 and AR-05 fail on font-switch (b), Sev-2. The Noto Sans caps and ASCII digits measure 1.63× and 1.61× the Arabic alef height, above the 1.3× anchor. Bidi order, spacing and baseline (offset ≤ 1 px) are correct in both.
  All Arabic properties pass: shaping, lam-alef, harakat, tatweel, mirroring, Arabic-Indic digits and ٪/؟/،. There is no wrap, clip or tofu. Two Sev-3 font-switch notes (AR-08 quotes sit high, AR-10 dash 2.5 px high) do not affect correctness.
  Schema: the v0 caption fields plus `has_audio` are enough at M0. The size fix belongs in the `style` definition, not in a new caption field.
- **ARTIFACTS (paths):** `company/experiments/EXP-008-results.md`; 200% crops (scratch, not in the repo): `/tmp/claude-1000/-workspaces-Efficient-Video-Editor/aaad3156-5fc0-4481-9dd9-f8ade7986944/scratchpad/h0016/AR-XX_200.png`
- **EVIDENCE (commands + outputs / metric files):**
  - `grep 'exp008/AR-..\.png' render/exp008/SHA256SUMS | sha256sum -c` gave 10× OK. `render/exp008/ffprobe.txt` shows 10× png,1080,1920,rgb24.
  - Pixel scan (ffmpeg rawvideo + numpy): every image has a single text line and none is blank. The white-fill column segments are listed in results §4. Key numbers: AR-04 digits 37.5 px vs alef 23 px; AR-05 "P" 37 px vs alef 23 px; AR-09 tatweel runs 66 px and 66 px; AR-10 dash centre 961 vs digit mid 963.5.
- **DONE-WHEN CHECK:**
  - ✅ 10 rows: results §3
  - ✅ Overall verdict per the locked rule: FAIL (8/10, 0 Sev-1), results header and §5
  - ✅ Schema note: results §7
  - ✅ LOG entry: `company/positions/04-creative/LOG.md`
- **DEVIATIONS FROM BRIEF:** none from the brief. Against EXP-008 §5.4 step 11, Creative wrote the results file because the brief says so. Zoom was done as a ×2 Lanczos crop of the text bbox (results §6). The judge did not view any control or EXP-006 PNG.
- **OPEN QUESTIONS (numbered, with who should answer):**
  1. (research-lead) Add the evidence level and the H-0015 deviations (log non-determinism, U+061C) to the results.
  2. (engineering-lead / product-lead) Open a new EXP id for a per-script size factor on the Noto Sans runs (target 0.8–1.2× alef-to-cap). Decide whether `style` carries that factor or an ADR is needed.
  3. (Founder) Optional, non-decisive spot-check of AR-04, 05, 07, 08 and 10. It would also calibrate the uncalibrated 1.3× anchor.
- **CONFIDENCE:** High for the order, shaping and size numbers, which were measured from pixels. Medium for subtle mark placement (AR-07) because the single judge is an LLM.
- **NEXT RECOMMENDED STEP:** Research finalises the results (evidence level), Assurance reviews, then the Operator briefs the font-size-parity fix under a new EXP id.
