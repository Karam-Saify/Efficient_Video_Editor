# BRIEF H-0007 (Task C3: judge EXP-006 images)
- **To:** creative-lead
- **Tier / Milestone:** T2 / M0 (exit criterion 0.3)
- **Date:** 2026-11-22

1. **Objective (with why):** Judge each EXP-006 caption image as a native-reading Arabic editor, because only a human-style visual check can catch shaping or RTL defects that code cannot see, and a Sev-1 here blocks every captioned Short.
2. **Inputs (exact paths):**
   - `render/frames_check/AR-01.png … AR-10.png` (you are the ONLY position allowed to view images; view these 10 and nothing else)
   - `render/frames_check/run_log.txt` (codepoints per string)
   - `company/experiments/EXP-006.md` (LOCKED: judging procedure + pass rule), `company/positions/04-creative/ARABIC_QA.md` (severity scale, intended strings)
   - `schemas/timeline.schema.json` (after H-0004) for the consultation in item 10
3. **Constraints (invariants, tools allowed/forbidden, budget):**
   - For each string, check shaping/joining, RTL word order, digits (Arabic-Indic and Western, direction inside RTL), Latin words and their placement, lam-alef ligature, diacritics stacking, quotes/brackets mirroring, tatweel, punctuation (، ؟ ٪ –), clipping/cut-off. Compare against the intended string in ARABIC_QA.md.
   - Record per string: PASS/FAIL, severity of each defect (Sev-1/2/3 or none), one-line description of what you saw. Be specific and conservative: if you cannot tell, mark it UNCERTAIN, and treat that as not passing.
   - Apply the locked pass rule exactly: PASS = 10/10 correct AND zero Sev-1.
   - Do not view any other image or video (no `data/golden/`, `quarantine/`, `out/`). Do not edit EXP-006.md or the PNGs. No commit.
4. **Output (format + exact path):** `company/experiments/EXP-006-results.md` (per-string table + overall verdict + notes); return in `company/handoffs/H-0007-return.md`.
5. **Done when:**
   - [ ] 10-row table: ID · string · verdict · severity · observation
   - [ ] Overall EXP-006 verdict per the locked rule
   - [ ] Schema consultation answered (item 10)
   - [ ] Entry appended to `company/positions/04-creative/LOG.md`
6. **Out of scope:** Fixing the renderer, re-rendering, style guide changes.
7. **Effort budget:** max 30 tool calls · max 2 retries per failing action
8. **Escalate if:** an image is missing, the wrong size, or blank; or a string in run_log codepoints differs from ARABIC_QA.md.
9. **Termination condition:** results file + return written; stop.
10. **Consulted positions (from RACI) and what they must confirm:** You are consulted on the timeline schema (RACI 12 C): state in the return whether v0 caption fields (`text`, `start_ms`, `end_ms`, `style`, `dir`) suffice for Arabic captions at M0, and list any field you need later (do not change the schema).
