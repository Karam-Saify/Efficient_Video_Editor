# RETURN H-0012
- **From:** research-lead
- **STATUS:** DONE
- **SUMMARY:**
  O1 inserted in `company/experiments/EXP-008.md` §6 directly after the "Definition of correct" paragraph (lines 139-144); O2 inserted in §5.4 step 10 after "clipping," (line 125). Both texts are copied character-for-character from `company/handoffs/H-0011-return.md` (only the markdown blockquote `> ` prefixes were dropped so they render as body text; no word, severity or threshold changed: 1.3x / 0.6x, Sev-1/2/3 as written).
  Creative sign-off line (line 213) now ends with "*(O1/O2 applied verbatim by research-lead 2026-11-22, H-0012 ...)*". `**Lock:** DRAFT` unchanged. Nothing committed. src/, tests/, company/decisions/ untouched.
- **ARTIFACTS:** `company/experiments/EXP-008.md`; `company/positions/02-research/LOG.md` (appended); this file.
- **EVIDENCE:** `git diff --stat company/experiments/EXP-008.md` -> 1 file, 9 insertions(+), 2 deletions(-) (the 2 are the step-10 and sign-off lines edited in place). Python `assert s.count(anchor)==1` on all three anchors passed before replacement.
- **WORDING I WOULD CHANGE:** none in O1/O2.
- **OPEN QUESTIONS:**
  1. Operator: two stale items outside this brief should be fixed before lock (research-lead, T0/T1): §8 threats table row "Construct" still says "Open consultation item C2 for creative-lead, settled before lock" (now settled by O1); and the `render/exp007/` / `experiments/exp007_render.py` names (Creative comment, H-0011). Neither changes thresholds; do them in the lock brief, after Engineering signs, so Engineering reviews the final paths.
  2. Founder (from H-0011 Q3): calibrate the O1(b) 1.3x / 0.6x anchors at the first FOUNDER_TASTE session. Not blocking.
- **CONFIDENCE:** High that the text is verbatim (programmatic insert from the return text).
- **NEXT:** engineering-lead signs E1-E5; then research-lead locks EXP-008.
