# BRIEF H-0016 (Task C3': judge EXP-008 images)
- **To:** creative-lead
- **Tier / Milestone:** T2 / M0 (Task C; ROADMAP 0.7)
- **Date:** 2026-11-22

1. **Objective (with why):** Judge each EXP-008 caption image as an Arabic editor, against the locked rule, because a Sev-1 caption defect blocks every captioned Short.
2. **Inputs (exact paths):** the 10 judged PNGs AR-01..AR-10 in the EXP-008 output dir (as named in `company/experiments/EXP-008.md` and `company/handoffs/H-0015-return.md`); `company/experiments/EXP-008.md` (LOCKED: judging procedure step 10, §6 "correct" definition with O1/O2); `company/positions/04-creative/ARABIC_QA.md`
3. **Constraints:** You are the ONLY position allowed to view images. View exactly those 10 PNGs and nothing else: no control PNGs unless EXP-008 says the judge sees them, never the EXP-006 PNGs, no `data/golden/`, `quarantine/`, `out/`. Compare each against the raw reference string. Record per string PASS/FAIL, every defect with its severity (including O1 font-switch anchors and O2 mid-word cut), and a one-line observation. If you can't tell, mark it UNCERTAIN, which counts as not correct. Apply the locked pass rule exactly. Do not edit EXP-008.md or the PNGs. No commit.
4. **Output:** `company/experiments/EXP-008-results.md` (10-row table: ID · string · verdict · defects+severity · observation; N_correct, N_sev1, overall verdict); return `company/handoffs/H-0016-return.md`.
5. **Done when:** [ ] 10 rows · [ ] overall verdict per the locked rule · [ ] schema note: whether v0 caption fields (`text`, `start_ms`, `end_ms`, `style`, `dir`) plus the new `has_audio` source field are enough for Arabic captions at M0 (RACI 12 C) · [ ] LOG entry
6. **Out of scope:** re-rendering, renderer fixes, style guide changes.
7. **Effort budget:** max 30 tool calls · max 2 retries
8. **Escalate if:** an image is missing, the wrong size or blank.
9. **Termination condition:** results + return written; stop.
10. **Consulted positions:** Research adds the evidence level in the results afterwards; Assurance reviews.
