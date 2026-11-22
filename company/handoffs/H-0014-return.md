# RETURN H-0014
- **From:** research-lead
- **STATUS:** DONE
- **SUMMARY (≤5 lines):**
  EXP-008 is LOCKED (2026-11-22). Engineering's G1–G3 are applied verbatim from H-0013-return.md: 14 `render/exp008/` paths, 2 `experiments/exp008_render.py` references, the rule-(b) regex and the `0xE01` text.
  The stale §8 "C2" threats row now points to the O1 resolution. The Operator ruling (no Creative re-sign) is recorded under the consultation block.
  No "exp007"/"EXP-007" remains except the ID note. The file was written with a single Write and is byte-identical to a pre-verified scratch build.
- **ARTIFACTS (paths):**
  - `company/experiments/EXP-008.md` (LOCKED, sha256 `5d3cdb5419e88c97656511dc0b45673567547a3ce426001c33ec62ed7a9773da`)
  - Scratch build and transform script (not committed): `/tmp/claude-1000/-workspaces-Efficient-Video-Editor/aaad3156-5fc0-4481-9dd9-f8ade7986944/scratchpad/h0014/{t.py,EXP-008.final.md}`
- **EVIDENCE (commands + outputs / metric files):**
  - Transform script with exact-count assertions on every replacement. Output: `render paths 14`. The 2 script-path replacements were asserted.
  - `diff scratch/EXP-008.final.md company/experiments/EXP-008.md` → `IDENTICAL_TO_VERIFIED`. Both files have the same sha256, shown above.
  - `git diff --stat` → `EXP-008.md | 41 ++++----, 21 insertions(+), 20 deletions(-)`
  - `grep -n -i "exp007\|exp-007"` → line 5 only (the ID note).
- **DONE-WHEN CHECK:**
  1. G1, G2 and G3 applied verbatim: ✅
     - G1: §5.1 precondition 3, §5.2 paths, §5.4 steps 1/2/3/6/7/8/9, the §8 instrument-fix rule and §10 Roles.
     - G2: the §5.4 step-7 rule (b) sentence was replaced with Engineering's exact text.
     - G3: §5.5 now reads `Glyph 0xE01 not found …`, followed by "(measured 2026-11-22, H-0013)".
     - The rule (a) regex is already case-insensitive.
  2. Stale §8 C2 threats row fixed: ✅. The mitigation now reads "Resolved at consultation (H-0011, O1): the "font-switch" category in §6 …".
  3. Operator ruling recorded as a one-line note under the consultation block: ✅
  4. No remaining exp007/EXP-007 except the ID note: ✅ (grep above). The Engineering sign-off line was rephrased to "rename the drafted instrument paths/script to …" so it no longer quotes `exp007`.
  5. Complete file written with a single Write, with `- **Lock:** LOCKED · 2026-11-22`: ✅ (line 2).
- **DEVIATIONS FROM BRIEF:** Three wording-only edits beyond G1–G3, made because they were stale at lock time. None of them changes the procedure, the thresholds or the "correct" definition.
  - (a) Header Brief field now reads "H-0010 (draft), H-0014 (lock)".
  - (b) §6 "(EXP-006 §6, unchanged unless creative-lead objects at consultation)" now reads "(EXP-006 §6, kept unchanged at consultation H-0011)".
  - (c) The consultation preamble "is resolved by editing this DRAFT" now reads "was resolved by editing the DRAFT".
  - In addition, each sign-off line carries an "applied verbatim" annotation.
  - Engineering's *optional* step-3 sentence (fc-query returns no charset or more than one face → INVALID) was **not** added. It was not a condition of sign-off and is outside the G1–G3 brief. It can still be met in code without a spec change, because an empty charset already makes COVERAGE_OK=False.
- **OPEN QUESTIONS (numbered, with who should answer):**
  1. (assurance-lead) My pre-lock checklist item "Assurance confirmed verifiability" was not separately signed before this lock. The EXP-008 consultation block requires only Eng + Creative. Please treat the H-0014 T2 review as that confirmation. Any objection now needs a new EXP id.
  2. (Operator) Brief engineering-lead to write `experiments/exp008_render.py` and run §5.4 steps 1–9 (Engineering suggested this in H-0013).
- **CONFIDENCE:** High. Every replacement was asserted by count, and the written file is byte-identical to the verified build. The biggest doubt is the Assurance pre-lock item above, which is a process gap rather than a content gap.
- **NEXT RECOMMENDED STEP:** assurance-lead reviews H-0014 (lock and git history of EXP-008). Then the Operator issues the Engineering render brief.
