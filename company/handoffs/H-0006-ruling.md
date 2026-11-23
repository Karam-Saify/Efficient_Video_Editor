# RULING on H-0006 (EXP-006 render run): validity under §8
<!-- Written by research-lead, owner (A) of EXP-006. Format follows company/templates/RETURN.md. -->
- **From:** research-lead
- **Date:** 2026-11-22
- **STATUS:** DONE
- **VERDICT:** **EXP-006 run = INVALID** (no PASS/FAIL verdict). Do not judge the PNGs. Remedy is a new EXP id (EXP-007).
- **SUMMARY (≤5 lines):**
  - libass resolved a second font file (`NotoSans-Regular.ttf`) for AR-05, AR-08 and AR-10. Under the locked text this is invalidating: §8 says "different font file resolved", and §8's non-invalidating list carves font fallback out by name.
  - The fallback is not cosmetic. It covers the very property three strings exist to test: Latin words in AR-05, quotes **and brackets** in AR-08, and the en dash in AR-10. Those properties would be judged on a font the prereg does not name.
  - A rerun of EXP-006 cannot cure this. The render is deterministic, so the same fallback would recur, and the cause is a design gap in my prereg, not an execution error. No rerun is needed, and none would be useful.
  - Remedy: preregister EXP-007, referencing EXP-006, with a declared font stack that covers every code point in the 10 strings, plus a coded pre-render coverage check. EXP-006 gets a results file that records INVALID.
  - The H-0007 judging brief should be put on hold or withdrawn. Nobody, Creative included, should view the 10 PNGs.

## 1. Valid or invalid? Reasoning from the locked text
Evidence that a second font file resolved (`render/frames_check/render.log`):
```
135: Glyph 0x69 not found, selecting one more font for (Noto Sans Arabic, 400, 0)       [AR-05]
136: fontselect: (Noto Sans Arabic, 400, 0) -> /usr/share/fonts/truetype/noto/NotoSans-Regular.ttf
224: Glyph 0x22 not found ...  -> NotoSans-Regular.ttf                                   [AR-08]
284: Glyph 0x2013 not found ... -> NotoSans-Regular.ttf                                  [AR-10]
```
libass logs only the first missing glyph per event. My coverage check below shows the true extent. It compares each string with the fontconfig charset of `NotoSansArabic-Regular.ttf` (`fc-query --format=%{charset}`):
```
AR-04 missing from NotoSansArabic: []
AR-05 missing from NotoSansArabic: ['U+0050','U+0065','U+0068','U+0069','U+006E','U+006F','U+0072']   (P e h i n o r)
AR-08 missing from NotoSansArabic: ['U+0022','U+0028','U+0029']                                          (" ( ))
AR-10 missing from NotoSansArabic: ['U+2013']                                                             (–)
```
ASCII digits (AR-04, AR-05) are covered by Noto Sans Arabic. All Arabic-block glyphs in all 10 strings came from the primary file.

Reading the prereg:
1. **§8 invalidating list:** "different font file resolved". A second font file did resolve: the log line `fontselect: … -> NotoSans-Regular.ttf` says so literally. Nothing in the text limits the clause to the primary `fc-match` result.
2. **§8 non-invalidating list:** "extra log warnings **that are not font fallback**". The prereg names font fallback explicitly so that it does *not* fall in the harmless category. This is the strongest textual signal. If fallback were meant to be a harmless recorded observation, that qualifier would have no purpose.
3. **§5.3 step 4, "record any in the results":** this is an instruction to detect and record. It does not classify. §8 opens with "Deviations … are listed in the results, never hidden", so invalidating deviations are *also* recorded. "Record any" therefore does not conflict with INVALID.
4. **Threats table, "Silent font fallback (glyphs from another font) would test the wrong font":** the stated harm is exactly what happened, for the tested property of 3 of the 10 strings. The mitigations (precondition 5.1.2, `fc-match` capture, step-4 log check) did what they were for: they *detected* the threat. They could not prevent it. Detection is not mitigation of the consequence.
5. **§1 question:** "...and the font Noto Sans Arabic, render all 10 ...". For AR-05/08/10, a PASS would not answer this question. It would answer a different one, about the libass + fontconfig fallback chain.
6. **Tie-break:** the owner is reinterpreting an ambiguous locked rule after seeing the deviation. Reading it in the permissive direction would weaken I-5 (thresholds and rules are not bent after the fact). I-10 says that when in doubt, go stricter. The cost of INVALID is low: no PNG has been seen and a rerun is cheap, about 3 s CPU.

**Ruling: INVALID.** I give the alternative "valid with deviation, downgrade one level" no weight. It would still yield an E1-level claim that cannot support the component-adoption decision (which needs E2), and the claim itself would be about an unnamed configuration.

**Root cause (owned by research-lead):** §4 of my prereg listed the non-Arabic code points (ASCII Latin, `"` `(` `)`, U+2013), but I did not check that Noto Sans Arabic covers them. The prereg was also locked before Engineering confirmed feasibility (§10). This is a preregistration design flaw, not an Engineering error. Engineering's run followed §5 and was deterministic: SHA256SUMS were byte-identical across 2 runs, per `company/handoffs/H-0006-return.md`.

## 2. Consequences if valid
Not applicable (the run is INVALID). For the record, a valid reading would have meant a one-level downgrade (PLAYBOOK SOP-R3.3, EXP-006 §7) from E2 to E1. That is below the E2 the adoption decision needs, so even that reading would not have fed the decision.

## 3. Remedy
- **New EXP id: EXP-007**, a superseding Arabic caption-rendering test on FFmpeg + libass that references EXP-006. Research drafts it in a separate brief. It is not drafted here. Requirements I will carry into it:
  1. A declared font stack. Either a primary font that covers Arabic and Latin, or an explicit primary + fallback map (code point → expected font file). Every file in the stack must have a DATA_RIGHTS row. The choice of caption font is Creative's call (C); the coverage requirement is Research's.
  2. A coded pre-render coverage check. Every code point of every string must be checked against the declared stack's cmap/charset. Do not rely on libass logs, which report only the first missing glyph per event.
  3. A log-check positive control. The detection script must flag a known-fallback string before the real run. This fixes the step-4 detection failure in H-0006 (the regex `fallback|glyph not found` did not match `Glyph 0x69 not found`).
  4. The invalidation rule written without ambiguity: "any glyph resolved to a file not in the declared stack map".
  5. Engineering and Creative are consulted *before* the lock, unlike EXP-006 (§10).
- **EXP-006 itself:** never edited and never re-run (§7). Research writes `company/experiments/EXP-006-results.md` with verdict **INVALID**, this deviation, ENV.txt contents, SHA256SUMS reference, and the script-edit note. Null and invalid results get the same rigour as any other result.
- **The 10 PNGs:** keep them as artifacts of the invalid run (hashes in `render/frames_check/SHA256SUMS`). Do **not** show them to creative-lead or anyone else, even as exploration. Under EXP-007, 7 of the 10 strings may render byte-identically if the Arabic font is unchanged, and prior exposure would bias the EXP-007 judge.

## 4. Rerun with the edited script?
- **Permitted:** technically yes. §8 allows up to 2 identical re-executions before any PNG is judged. One has been used (the determinism run), so one is left.
- **Needed:** **no**. The re-execution rule exists to repair *execution errors*. This is a design gap. The render is deterministic, so a rerun reproduces the same fallback and the run stays INVALID. A rerun would only show that the post-run script edit (stdout regex + `ruff format`) leaves output files unchanged. That has no value for an invalid run.
- **Recommendation:** do not rerun under EXP-006. Engineering can carry the edited `experiments/exp006_render.py` forward as the starting point for the EXP-007 instrument, where it gets verified by the positive control in §3.3. Record the script hash mismatch (outputs produced by the pre-edit version; current sha256 8f083554…6222c) as a deviation in EXP-006-results.md.

## EVIDENCE
- `company/experiments/EXP-006.md` §1, §5.3 step 4, §8 (both lists, re-execution rule), threats table row "Silent font fallback". Read only, not edited.
- `render/frames_check/render.log` lines 135-136, 224-225, 284-285. The other 7 strings have only the primary `fontselect` line.
- Coverage command output (fc-query charset of `/usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf`) is pasted in §1.
- No PNG was opened, viewed or hashed by research-lead.

## DONE-WHEN CHECK
- ✅ Q1, valid or invalid: INVALID, with textual justification (§1).
- ✅ Q2, consequences if valid: not applicable; the counterfactual is stated (§2).
- ✅ Q3, remedy: EXP-007, not drafted, requirements listed (§3).
- ✅ Q4, rerun: permitted but not needed; recommendation is no rerun (§4).
- ✅ LOG.md appended; nothing committed.

## DEVIATIONS FROM BRIEF
- The request came in chat and is not a 10-field brief file. Escalate-if, termination and consulted-positions were not stated. I proceeded because the task is fully specified, sits inside my own experiment and is blocking. The Operator may want to file it retroactively as a brief.
- The return is written to this ruling file, not `H-0006-return.md`, which is Engineering's and must not be overwritten.

## OPEN QUESTIONS
1. Operator: put H-0007 (Creative judging brief) on hold or withdraw it, and brief research-lead to write EXP-006-results.md (INVALID) and draft EXP-007.
2. creative-lead (C): which caption font stack should EXP-007 test? Options are Noto Sans Arabic + Noto Sans as a declared pair, or a single Arabic+Latin display font (e.g. Cairo, Tajawal, IBM Plex Sans Arabic). The choice affects the product, not only the test.
3. assurance-lead: add a DATA_RIGHTS row for `NotoSans-Regular.ttf` (sha256 89c3c497…909d), which appeared in output (H-0006 return Q2). Review this ruling (T2).
4. Operator: `render/` and PNGs are not git-ignored (H-0006 Q3). Recommend committing ENV/log/SHA256SUMS/strings_check as evidence of the INVALID run. Whether to commit the PNGs is the Operator's or Assurance's call.

## CONFIDENCE
High on INVALID. The §8 carve-out "not font fallback" is explicit, and the fallback hits the tested properties of AR-05/08/10. The biggest doubt: a reader could argue that "different font file resolved" meant only the primary `fc-match`. I have addressed this in §1 points 2 and 6.

## NEXT RECOMMENDED STEP
Assurance reviews this ruling. Then the Operator briefs research-lead for (a) EXP-006-results.md with verdict INVALID and (b) the EXP-007 prereg, with Engineering and Creative consulted before the lock.
