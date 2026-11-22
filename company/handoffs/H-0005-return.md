# RETURN H-0005
- **From:** research-lead
- **STATUS:** DONE
- **SUMMARY (≤5 lines):**
  EXP-006 (FFmpeg + libass Arabic caption correctness) is preregistered and LOCKED, and nothing has been rendered.
  It contains the 10 ARABIC_QA strings verbatim with fingerprints, fixed render parameters (Noto Sans Arabic 72, white with black outline 4, Alignment 5, `Encoding: -1`, grey 1080×1920), the exact ffmpeg command, the judging protocol, and the Founder pass rule (10/10 correct AND 0 Sev-1, otherwise FAIL).
  It adds an INVALID outcome for invalidating deviations, a re-execution rule (re-runs allowed only before any PNG is judged), and the rule that a FAIL leads to a new EXP id.
  It gives an operational definition of "correct" (no Sev-1, no Sev-2, and no defect in the property the string tests). Creative must confirm this.
- **ARTIFACTS (paths):**
  - /workspaces/Efficient_Video_Editor/company/experiments/EXP-006.md (LOCKED)
  - /workspaces/Efficient_Video_Editor/company/positions/02-research/LOG.md (entry appended)
- **EVIDENCE (commands + outputs / metric files):**
  - `grep -n "Lock:\*\* LOCKED" company/experiments/EXP-006.md` → `2:- **Lock:** LOCKED · 2026-11-22`
  - Strings are verbatim: `diff` of the AR- table columns (ID, string, what it tests) between ARABIC_QA.md and EXP-006.md → no differences (`VERBATIM_OK`)
  - Invisible-character scan (categories Cf/Cc, U+200B..200F, U+061C, U+FEFF, U+00A0) → none found. The only non-Arabic code points are ASCII digits, Latin, `" ( )` and U+2013. Escalation trigger 8 was not met.
  - Environment seen: `ffmpeg version 6.1.1-3ubuntu5`; libass9 0.17.1-2build1, libharfbuzz0b 8.3.0-2build2, libfribidi0 1.0.13-3build1; `fc-list` → /usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf present
  - `src/render/__init__.py` already uses `ass=...:shaping=complex`. The EXP-006 command uses the same filter.
- **DONE-WHEN CHECK:**
  - ✅ EXP-006.md has hypothesis (§2), the 10 strings verbatim with IDs (§4), procedure (§5.3), fixed parameters (§5.2), judge (§5.3 step 6, §10), metric (§3, §6), pass rule (§6), deviations policy (§8), results path `company/experiments/EXP-006-results.md` (last section)
  - ✅ `**Lock:** LOCKED · 2026-11-22` present (line 2)
  - ✅ Entry appended to company/positions/02-research/LOG.md
- **DEVIATIONS FROM BRIEF:**
  1. SOP-R2 step 3 and `/prereg` say to consult Engineering, Creative and Assurance *before* locking. The brief required the lock now, so those confirmations are still pending. This is recorded in EXP-006 §10. If anyone objects, the fix is a new EXP id, not an edit.
  2. The PLAYBOOK register defines EXP-006 as "FFmpeg/libass vs Remotion". As briefed, it is scoped to the FFmpeg arm only, and this is stated in the file header.
- **OPEN QUESTIONS (numbered, with who should answer):**
  1. creative-lead: do you accept the §6 definition of "correct", including that a Sev-3 defect in the property a string tests (e.g. AR-06 `؟`, AR-02 `،`) makes that string incorrect?
  2. assurance-lead / H-0002: DATA_RIGHTS RR-001 (Noto Sans Arabic) was still "pending" on 2026-11-22. EXP-006 §5.1.1 makes resolving it a precondition, so H-0006 cannot start until H-0002 records it.
  3. Operator: the brief cites "M0 exit criterion 0.3". In ROADMAP.md, 0.3 is the schema criterion. EXP-006 lock is **0.7**. Please use 0.7 in STATE and the gate record.
  4. engineering-lead: please confirm H-0006 can run §5 as written. `render/` does not exist yet and may need a .gitignore decision; the PNGs and ENV.txt are evidence, so they should probably be committed.
  5. Founder: will you do the optional non-decisive spot-check of AR-02/05/07/08? The only judge is an LLM agent reading images. This is the main construct-validity threat.
  6. research-lead (later task): add assumption A-11 (libass caption correctness) to ASSUMPTIONS.md. No row exists yet.
- **CONFIDENCE:** High that the prereg is complete and locked. Medium that it measures what we care about (biggest doubt: one LLM judge for fine Arabic glyph detail, and font size 72 / wrap behaviour were chosen without a render, so AR-05 may wrap to two lines. This is allowed but not separately tested).
- **NEXT RECOMMENDED STEP:** Assurance C review of the lock (git history of company/experiments/EXP-006.md). Then get the Creative and Engineering confirmations (Q1, Q4) and close RR-001 (Q2). Then H-0006 render.
