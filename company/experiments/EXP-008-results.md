# EXP-008 results: Arabic + Latin caption rendering, FFmpeg + libass, declared Noto pair
- **Prereg:** `company/experiments/EXP-008.md` (LOCKED 2026-11-22). Render: H-0015 (engineering-lead). Judging: H-0016 (creative-lead, sole judge).
- **Date judged:** 2026-11-22
- **Verdict:** **FAIL** (`N_correct` = 8, `N_sev1` = 0). The locked rule is "PASS iff N_correct = 10 AND N_sev1 = 0".
- **Evidence level:** **E2** for the FAIL of this configuration (research-lead, H-0018; see §8).

## 1. Gating (from H-0015, not re-run by the judge)
`COVERAGE_OK=True`, `CTRL_OK=True`, `LOG_OK=True`, `PNG_OK=True`, `INSTRUMENT_UNCHANGED=True` (`render/exp008/coverage_check.txt`, `logcheck.txt`, `ffprobe.txt`, `company/handoffs/H-0015-return.md`). The gates hold, so this is a verdict and not INVALID.
Judge-side integrity check before viewing: `grep 'exp008/AR-..\.png' render/exp008/SHA256SUMS | sha256sum -c` gave `OK` for all 10 PNGs. The pixel scan found 1 text line per image, no blank image and no content outside the line (bboxes in §4).

## 2. Judging method (EXP-008 §5.4 step 10, §6 with O1/O2)
- **Images viewed:** exactly `render/exp008/AR-01.png` … `AR-10.png`. The judge did not open `render/exp008/control/` or `render/frames_check/` (EXP-006) and has never seen an EXP-006 or CTRL-01 image.
- **200% zoom:** for each PNG, the text bbox plus a 20 px margin was cropped and scaled ×2 (ffmpeg `crop`, `scale=iw*2:ih*2:flags=lanczos`) into scratch. The source PNGs were not modified.
- **Raw reference:** before viewing each image, the judge read the raw string from the `company/positions/04-creative/ARABIC_QA.md` table. The tagged `.ass` text was not used.
- **Categories checked for every string:** shaping/joining, RTL word and letter order, digits (direction and form), Latin (order and integrity), lam-alef, diacritics, brackets/quotes mirroring, tatweel/kashida, punctuation (، ؟ ٪ –), clipping, line wrapping / mid-word cut (O2), tofu, and font-switch at each Noto Sans ↔ Noto Sans Arabic boundary (O1).
- **O1 numbers come from pixels, not from eyeballing.** On a white-fill mask (all RGB > 200, so the black outline is excluded), I took each connected column segment and measured its native-pixel x-range, top y and bottom y. The alef reference is the isolated alef in the same line. Heights are native px.

## 3. Per-string table
| ID | String (raw) | Tested property | Verdict | Defects (category · severity) | Observation |
|---|---|---|---|---|---|
| AR-01 | مرحبا بكم في القناة | basic shaping | **PASS** | none | All 4 words are joined correctly and read right to left. ة is final and ال is joined. Single line, nothing clipped. |
| AR-02 | لا، هذا ليس صحيحاً | lam-alef + ، + tanween | **PASS** | none | The لا ligature is formed. The Arabic comma ، sits on the baseline to the left of لا. Fathatan sits above the final alef. Word order is correct. |
| AR-03 | السعر ٢٥٠ دولار فقط | Arabic-Indic digits in RTL | **PASS** | none | The digits read ٢٥٠ (most significant on the left), so the number is LTR inside RTL as required. The digits are Arabic-Indic forms, and the لا in دولار is formed. |
| AR-04 | السعر 250 دولار فقط | Western digits inside RTL | **FAIL** | font-switch (b) · **Sev-2**: ASCII digit height 37.5 px vs alef 23 px = **1.63×** (> 1.3×) | Digit order "250" is correct and so is word order. Baseline: digits bottom at 974–975, alef bottom at 974, so the offset is ≤ 1 px (no step). Weight matches. The number reads as a larger text size. |
| AR-05 | جربت iPhone 16 Pro امبارح | Latin + digits in Lebanese | **FAIL** | font-switch (b) · **Sev-2**: Latin cap "P" 37 px vs alef (امبارح) 23 px = **1.61×**; "16" 37.5 px = 1.63× | Order is correct: جربت on the right, "iPhone 16 Pro" intact and LTR, امبارح on the left. Both boundary spaces are kept and nothing collides. Baseline offset ≤ 1 px. The dialect spelling امبارح/جربت is kept. Latin x-height (28–29 px) is already 1.24× alef. |
| AR-06 | شو رأيك؟ | Levantine word + ؟ | **PASS** | none | شو is kept as dialect. The hamza sits on the alef (أ). The mirrored ؟ is at the visual left end, which is correct for RTL. |
| AR-07 | قُلْ هُوَ | harakat stacking | **PASS** | none | Damma on ق (above its dots, no collision), sukun on ل, damma on ه, fatha on و. Each mark sits over its own base letter. |
| AR-08 | "اقتباس" و(قوسين) | quotes + brackets mirroring | **PASS** | font-switch · Sev-3: quote marks span y938–950, wholly above the Arabic letter-top line (alef top 952), sitting 2 px higher. Brackets are 46 px tall vs a 31 px Arabic span (952–983) and share its bottom at 983 | The brackets are mirrored correctly and both enclose قوسين. The quotes enclose اقتباس. The space before و is kept. Anchor (b) does not apply because there is no Latin cap or ASCII digit, so this is recorded as Sev-3 only. |
| AR-09 | ـــــــ مدّ ـــــــ | tatweel / kashida | **PASS** | none | The two tatweel runs are equal and continuous (66 px each, x448–513 and x567–632) on the baseline (y968–970). The gaps to مدّ are 10 px and 11 px (the raw spaces). Shadda sits on د. |
| AR-10 | ١٠٪ خصم – ٢٠٢٦ | ٪ + dash + digits | **PASS** | font-switch · Sev-3: en dash centre y961 vs ٢٠٢٦ mid-height y963.5, so it sits **2.5 px (0.11 × digit height) high** | ١٠ has ٪ on its left, which is correct for RTL. Order: ١٠٪ on the right, then خصم, then the dash, then ٢٠٢٦ on the left with digit order correct. Anchor (b) does not apply because all digits are Arabic-Indic (class A). |

**N_correct = 8** (AR-01, 02, 03, 06, 07, 08, 09, 10) · **N_sev1 = 0** · Sev-2 = 2 (AR-04, AR-05, both font-switch (b)) · Sev-3 = 2 (AR-08, AR-10, both font-switch, which do not affect correctness under §6). UNCERTAIN = 0.

## 4. Raw measurements (native px, white fill > 200)
```
AR-04 alef(السعر) x694-696 y952-974 h23 | "2" x525-549 y938-974 h37 | "5" y938-975 h38 | "0" y938-975 h38
AR-05 alef(امبارح) x353-355 y952-974 h23 | "P" x634-657 y938-974 h37 | "1" y938-974 h37 | "6" y938-975 h38 | o/n/e h28-29
AR-08 alef(اقتباس) x660-661 y952-974 h23 | brackets x396-406, x507-517 y938-983 h46 | quotes y938-950 h13
AR-09 tatweel L x448-513 y968-970 | مدّ x524-555 y944-970 | tatweel R x567-632 y968-970
AR-10 ٢ y953-974 (mid 963.5) | dash x501-522 y960-962 (centre 961)
Text bboxes (any non-grey): AR-01 x409-669 y942-989 ... AR-05 x272-806 y931-993 ... AR-10 x427-652 y948-993 (all single-line, h 37-63)
```

## 5. Analysis (§7)
- **Failed strings and category:** AR-04 and AR-05 fail on **font-switch (b)**, which is a Sev-2 that makes a string not correct under §6. Noto Sans Regular at the same nominal size draws caps and ASCII digits about 1.6× the height of Noto Sans Arabic's alef. The Latin/digit run therefore reads as a bigger font. Bidi order, shaping, spacing and baseline are all correct in both strings.
- **What passed:** every Arabic-only property passed, with zero Sev-1 for shaping, order, lam-alef, harakat, tatweel, mirroring, digits, wrapping or tofu.
- **Conclusion, limited to the prereg:** "FFmpeg 6.1.1 + libass 0.17.1, this style, declared Noto pair, §5.3 rule" **does not pass**. The judge does not conclude anything broader. A fix (for example a per-script size factor on the Noto Sans runs) needs a new EXP id. The result stands, with no re-render and no re-judging (§8).
- **Calibration note (Creative):** the 1.3× anchor was declared uncalibrated at H-0011. It is applied exactly as locked here. From a viewer's side the measured 1.6× is large enough to read as a different size on a phone ("iPhone 16 Pro" dominates the line), so the judge would not argue that this is a false FAIL. The Founder spot-check (§8 threats) of AR-04, 05, 07, 08 and 10 is recommended and does not decide the result.

## 6. Deviations
1. **Results author:** per §5.4 step 11, research-lead writes this file. The H-0016 brief assigns it to creative-lead, with Research adding the evidence level afterwards. The brief is followed.
2. **Zoom implementation:** "200%" was done as an ×2 Lanczos crop of the text bbox, which is equivalent for the single-line content. This is recorded so it can be reproduced.
3. None of the 10 PNGs was blank, missing or the wrong size, so there was no escalation.

## 7. Schema note (RACI 12 C)
The v0 caption fields (`text`, `start_ms`, `end_ms`, `style`, `dir`) plus the source field `has_audio` are **enough for Arabic captions at M0**. Font assignment per run is derived by code from `text` (§5.3), so it needs no field. `dir: rtl` is needed and present. No caption in this test wrapped. The FAIL is about size parity between the two fonts. That belongs in the named `style` definition (for example a Latin/digit scale factor resolved by the renderer), not in a new per-caption field. If the style guide cannot express it, this is an ADR for Engineering and Product to decide, not a Creative decision.

## 8. Research analysis (research-lead, H-0018; SOP-R3, EXP-008 §7)
Written after reading §1 to §7 above and `company/handoffs/H-0015-return.md`, `H-0016-return.md`. Creative's table (§3) and measurements (§4) are not altered. No image was viewed by research-lead.

### 8.1 Verdict confirmation against the locked rule
| Metric (EXP-008 §6) | Value | Pass threshold | Kill threshold | Outcome |
|---|---|---|---|---|
| Gating `cov_ok`, `ctrl_ok`, `log_ok` | True, True, True (`render/exp008/coverage_check.txt`, `logcheck.txt`, H-0015) | all True | any False → INVALID | gates hold, a verdict is due |
| `N_correct` | 8 (AR-04, AR-05 not correct) | = 10 | ≤ 9 | **kill** |
| `N_sev1` | 0 | = 0 | ≥ 1 | pass |
| **Verdict** | | PASS iff N_correct = 10 AND N_sev1 = 0 | otherwise FAIL | **FAIL, confirmed** |

The FAIL follows mechanically from the locked rule: AR-04 and AR-05 each carry a Sev-2 under font-switch (b) (ASCII digit / Latin cap height above 1.3× alef), and §6 makes any Sev-2 a non-correct string. The measured ratios (1.61× to 1.63×, §4: 37 to 38 px against a 23 px alef) exceed the anchor by about 0.3×, i.e. ~14 px of digit height at this size, so the outcome does not hinge on a 1 to 2 px measurement error. No threshold has been or will be moved; the result stands (§8 of the prereg: no re-render, no re-judging).

### 8.2 Evidence level and the exact, limited claim
**Evidence level: E2** (preregistered metric, locked before the run, deterministic instrument reproduced in two identical runs, no validity-affecting deviation; see 8.3). The "golden set" here is the fixed Creative string set `ARABIC_QA.md` AR-01..AR-10, as preregistered; there is no held-out set, so E3 is not available.

Claims, each limited to "FFmpeg 6.1.1 + libass 0.17.1, the §5.2 style (Noto Sans Arabic 72, single line, grey 1080×1920), the declared Noto pair, the §5.3 run-splitting rule, these 10 strings":
1. **Main claim (E2, confidence High):** this configuration **does not pass** EXP-008. It is therefore **not adopted** as the Phase 1 caption renderer on this evidence.
2. **What failed (E2, High):** cross-font size matching. At equal nominal size, Noto Sans caps and ASCII digits render at 1.61× to 1.63× the Noto Sans Arabic alef height (AR-04, AR-05). Baseline offset ≤ 1 px and weight were within limits; only criterion (b) failed.
3. **What passed, as component observations inside the failing run (E2 for this configuration, confidence Medium for the judged items because of the single AI judge, High for the code-checked item):**
   - Per-run font assignment (code-checked, High): every code point was covered by its assigned declared file (`COVERAGE_OK=True`), no glyph resolved outside the declared pair and no `Glyph … not found` occurred for the 10 strings (`LOG_OK=True`), with the detector shown to fire on the positive controls C0, C1, C2 (`CTRL_OK=True`).
   - Arabic shaping (joining, lam-alef, harakat, tatweel, hamza) and bidi (RTL word order, LTR digit and Latin runs inside RTL, bracket/quote mirroring, ، ؟ ٪ placement): zero defects in their tested property across all 10 strings, N_sev1 = 0 (judged, Medium).
   - libass `\fn` overrides did not change visual order (consultation item E1 holds for these strings).
4. **Not claimed:** that the per-run font method works with any size correction; anything about karaoke, wrapping, bold/display fonts, video backgrounds, Remotion, or `src/render` (which does not yet implement §5.3). Item 3 is not an adoption claim; it only says which parts a successor need not change.

**Transfer to Arabic dialect Shorts:** AR-05 is the Lebanese code-switching case (dialect + brand name + digits), which is the common pattern in our target market, so the size defect is not an edge case; it will appear in most product or tech captions.

### 8.3 Deviations (engineering and judging) and their effect on validity
| # | Deviation | Source | Affects validity? | Reason |
|---|---|---|---|---|
| D1 | Raw ffmpeg `.log` files are not byte-identical between the two runs (ASLR context pointers; timing-dependent `frame=… speed=` stats lines). 5 of 11 logs differ after pointer normalisation, only in stats lines. | H-0015 Dev. 1 | **No** | The differing lines are neither rule (a) nor rule (b), which the prereg §8 lists as non-invalidating. The decision-relevant summary `logcheck.txt` is byte-identical between runs, and every PNG, `.ass` and check file is byte-identical. Reproducibility of the outcome is intact; only raw-log byte reproducibility is lost. Successor EXPs should add `-nostats` to the locked command. |
| D2 | U+061C (ARABIC LETTER MARK) lies inside the class-A range U+0600–U+06FF but is also named in class X. The instrument treats it as X (the explicit example wins, failing loudly). | H-0015 Dev. 3 | **No** | U+061C occurs in none of the 10 strings (§4 integrity scan, `strings_check.txt`), so no output changed. It is a specification ambiguity of the locked prereg, to be resolved explicitly in the successor's class table. |
| D3 | Two full runs before judging, run 1 moved to scratch; run 2 is the final. | H-0015 Dev. 2 | No | No error, no instrument fix (0 of 2 used); identical outputs. Strengthens, not weakens, the result. |
| D4 | Extra file `render/exp008/ffprobe.txt`, listed in SHA256SUMS. | H-0015 Dev. 4 | No | Adds a record; changes no step. |
| D5 | Results first authored by creative-lead (H-0016 brief) instead of research-lead (§5.4 step 11); 200% zoom done as ×2 Lanczos crop. | §6 above | No | Authorship is procedural; Research adds this analysis. The crop is equivalent for single-line content and is reproducible. |

No deviation affects validity, so no downgrade under SOP-R3.3: the evidence level stays E2.

### 8.4 Threats to validity
- **Single AI judge, no agreement measure (construct).** All judged outcomes rest on one creative-lead pass by an LLM agent. Mitigations: fixed category checklist, 200% zoom, raw reference, and for the failing criterion pixel measurements rather than eyeballing (§4), which a second rater can recompute from the PNGs and the method in §2. The FAIL itself is therefore less exposed to judge error than the PASS observations in 8.2 item 3, which could hide a subtle mark or shaping defect. The recommended Founder spot-check (AR-04, 05, 07, 08, 10) is non-decisive and does not change the verdict.
- **The 1.3× anchor is not calibrated against Founder taste (construct).** It was declared uncalibrated at H-0011. It is applied as locked, and with ratios of 1.6× the FAIL would only flip if the acceptable limit were ≥ 1.64×, which is implausible for a caption line (Creative §5 calibration note agrees). Calibration cannot reinterpret EXP-008; it matters for the successor.
- **Ratio measured on a single reference glyph (construct).** Alef height is one anchor; Latin x-height (28 to 29 px, 1.24× alef) shows that a single scale factor cannot match caps, digits and x-height to Arabic proportions at once. This is a design question for the successor, not a flaw in this result.
- **External:** one line on plain grey, one size (72), one weight; see prereg §8 threats.

### 8.5 Recommended successor
**EXP-010** (free: EXP-007 is reserved for revision diffs, EXP-009 is referenced for the Trend coding work in `DATA_RIGHTS.md`; no file or register entry uses EXP-010, checked by `grep -rln "EXP-010"`, no hits). Working title: *"Arabic + Latin caption rendering with a per-font scale factor for the Latin/digit font, carried in the caption `style` definition."* Named only; not drafted. It must also fix D1 (`-nostats`) and D2 (U+061C class) in its locked text.

**Should the Founder calibrate the 1.3× threshold before EXP-010 is locked? Yes.** The successor's pass/kill line is exactly this ratio, and the scale factor will be tuned towards it, so an uncalibrated anchor would let us "pass" against a number nobody has checked against taste. The calibration should be done before the EXP-010 lock, on stills that are not EXP-010 outputs (for example the existing AR-04/AR-05 PNGs plus a few scaled variants made in `company/experiments/explore/`), giving the Founder's acceptable band for Latin cap / ASCII digit height relative to alef (an upper and a lower bound). That band then goes into EXP-010 §6 at lock and is never moved. The calibration does not change EXP-008's verdict.

### 8.6 Status
- Proposed assumption A-11 ("FFmpeg + libass renders Arabic captions correctly on our caption style") is not yet in `company/state/ASSUMPTIONS.md`; on this evidence its status would be **Refuted for this configuration (E2, EXP-008)**. Adding the row is left to the Operator (SOP-R3.4; outside this brief).
- Next: Assurance verification (SOP-R3.5) against `render/exp008/SHA256SUMS` (excluding `.log` and ENV.txt lines, per H-0015), `coverage_check.txt` and `logcheck.txt`, before anyone uses this conclusion.
