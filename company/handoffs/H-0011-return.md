# RETURN H-0011
- **From:** creative-lead
- **STATUS:** DONE (sign-off line filled, with 2 requested changes for research-lead to make before lock)
- **SUMMARY (≤5 lines):**
  C1 (judging procedure) agreed, plus one missing check: wrapping / mid-word cut (Sev-1 in ARABIC_QA.md), see O2.
  C2: the §6 "correct" definition stays as it is. A visual mismatch between the two fonts gets its own category and objective severity anchors. It is not part of any string's tested property (O1).
  C3 (judge sees the raw string, not the tagged text) agreed with no change.
  No escalation. The Noto pair is designed to harmonise and can produce acceptable captions in principle. The main risk is a size mismatch, which is a FAIL here (Sev-2). Fixing it would need a new EXP id (see Q2).
  I have not viewed any image in this invocation or earlier (LOG.md has only the SETUP entry). Non-exposure to the EXP-006 PNGs is declared.
- **ARTIFACTS (paths):** `company/experiments/EXP-008.md` (Creative sign-off line only, line 206); this file; `company/positions/04-creative/LOG.md` (appended).
- **EVIDENCE (commands + outputs / metric files):** read EXP-008.md §4–§8 and the consultation block (lines 198–206); `ARABIC_QA.md` severity list and check procedure; `STYLE_GUIDE.md` Font row; `grep` of EXP-006-results.md (lines 44 and 75: no PNG viewed; Noto Sans Arabic lacks ASCII Latin, `"` `(` `)`, U+2013). No images opened. No renders run.

## Item answers
**C1, judging procedure vs ARABIC_QA.md: agreed, with O2.** Step 10 matches the ARABIC_QA check procedure (1080×1920 neutral frame, 200% zoom, pass/fail plus severity per string, Sev-1 means veto/FAIL). The path is `render/exp007/` rather than `render/frames_check/`. That is fine and keeps the EXP-006 evidence untouched. The category list in step 10 leaves out one ARABIC_QA Sev-1 item, "caption cut mid-word" (wrapping). It cannot be assumed away. The style uses 72 pt with 60 px margins, and libass may wrap. A wrap at a font switch could split "iPhone 16 Pro" or reorder lines.

**C2, "correct" definition: keep it unchanged. Font-switch inconsistency is classified per O1.** Rationale: the tested properties of AR-04/05/08/10 are order, direction, integrity and mirroring. Typographic harmony between the two declared fonts is not one of them. A Sev-3 harmony note must not decide the experiment. A mismatch a viewer would read as "different text size or a broken line" is Sev-2, because it is the same viewer harm as the existing Sev-2 "Latin words breaking line order". That makes the string incorrect under the existing general rule, so the experiment would FAIL on it. That is the right outcome for a Shorts caption.

**C3, raw reference: agreed, no change.** The judge sees the raw verbatim string from §4 plus the "What it tests" column. The judge does not see the tagged text. The judge can locate font switches from the raw string alone (Latin letters, ASCII digits, `"` `(` `)` and `–` are the Noto Sans runs).

## Requested changes (research-lead edits EXP-008.md; exact text)
**O1 (add to §6, directly after the "Definition of correct" paragraph):**
> **Font-switch consistency (category "font-switch", decided at consultation H-0011).** At every boundary between a Noto Sans run and a Noto Sans Arabic run, the judge compares the two runs and records:
> - **Sev-1:** glyphs of the two runs overlap or collide, any glyph is clipped, or the boundary space has gone (words run together). These count as Sev-1 under the existing clipping, tofu and order rules.
> - **Sev-2:** (a) the baseline of the Latin/digit run visibly steps up or down from the Arabic baseline, so the line reads as two lines or as a superscript or subscript; or (b) the Latin cap height or ASCII digit height is above 1.3× or below 0.6× the height of Arabic alef (ا) in the same line, so it reads as a different text size; or (c) the stroke weight differs enough that one run reads as bold next to regular.
> - **Sev-3:** any smaller visible difference in size, weight, spacing or dash/quote vertical position (for example the en dash in AR-10 sitting higher or lower than the digits' mid-height).
>
> Font-switch consistency is **not** part of the tested property of any string. A Sev-3 font-switch note alone does not make a string incorrect. Sev-1 or Sev-2 does, under the general rule. For each boundary, the judge writes the estimated height ratio or baseline offset in the note, as a number, and never as "looks off".

**O2 (step 10 category list, insert after "clipping,"):**
> line wrapping (the text must render on one line; any wrap that cuts a word, separates a Latin run from its Arabic neighbours or reorders lines is Sev-1 "caption cut mid-word" / order),

## Comments outside my decision rights (no decision, for research-lead/engineering-lead)
- The output paths and instrument name still say `exp007` (`render/exp007/`, `experiments/exp007_render.py`) after the renumbering to EXP-008. They are consistent within the file, so this is not an objection. Renaming them before lock would avoid confusion later.

- **DONE-WHEN CHECK:**
  - ✅ C1 and C2 (and any other Creative items) answered: C1, C2 and C3 are answered above.
  - ✅ Sign-off line filled: EXP-008.md line 206, "creative-lead, 2026-11-22, H-0011, objections: (O1)…(O2)…".
  - ✅ LOG.md entry appended to `company/positions/04-creative/LOG.md`.
- **DEVIATIONS FROM BRIEF:** none. Only the Creative sign-off line of EXP-008.md was edited. No other section was changed, no EXP-006 file was touched, no image was viewed and nothing was committed.
- **OPEN QUESTIONS (numbered, with who should answer):**
  1. research-lead: accept O1/O2 as worded, or reword? If reworded, the Creative line has to be re-signed before lock.
  2. Operator → Founder (later, not blocking): if EXP-008 FAILs only on the O1(b) size ratio, the obvious fix is a per-run size or scale correction. That needs tags (`\fs`/`\fscx`) that this EXP forbids, so it would mean a new EXP id. Do we want to pre-plan that successor now?
  3. Founder: confirm the 1.3× / 0.6× anchors in O1(b) when the first FOUNDER_TASTE calibration happens. They are my calibrated guess, not yet checked against Founder agreement.
- **CONFIDENCE:** Medium (biggest reason for doubt: the O1 numeric anchors are uncalibrated against the Founder, and an LLM judge estimating height ratios from a still at 200% zoom is imprecise near the thresholds).
- **NEXT RECOMMENDED STEP:** research-lead applies O1 and O2 to EXP-008 §6 and step 10, Creative re-confirms in one line, engineering-lead signs its line, then research-lead locks.
