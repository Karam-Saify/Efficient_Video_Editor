# RETURN H-0022
- **From:** research-lead
- **STATUS:** DONE (draft only; lock is blocked by design until footage with rights exists and O1 is answered)
- **SUMMARY (≤5 lines):**
  EXP-001 drafted as `**Lock:** DRAFT`: two models (faster-whisper 1.2.1 large-v3, large-v3-turbo; CPU int8, beam 5, VAD, forced `ar`, seed 0), dataset stated as a requirement only (≥ 4 Lebanese clips with verified rights, ≥ 8 min, ≥ 1,200 ref words, ≥ 1 code-switch clip, 1 MSA control), blind human references with the ARABIC_QA dialect policy, human word boundaries for 30 sampled words/clip.
  Normalisation fixed in 9 ordered steps with 10 test vectors (all 10 reproduced by a scratch implementation). Primary metrics WER_LB and P90 boundary error (A-02, 150 ms); secondary CER, hallucination rate, RTF; verdict rules, selection rule, deviations policy, threats and a 3-way consultation block (Eng E1–E6, Creative C1–C4, Assurance A1–A3).
  Fast-lane doc items: A-11 added to ASSUMPTIONS.md with the Operator's status text; PLAYBOOK register now has a Status column: EXP-006 INVALID, EXP-008 FAIL, EXP-010 registered (not drafted), EXP-001 DRAFT.
- **ARTIFACTS (paths):**
  - `company/experiments/EXP-001.md` (new, DRAFT)
  - `company/state/ASSUMPTIONS.md` (A-11 row added)
  - `company/positions/02-research/PLAYBOOK.md` (experiment register: Status column; EXP-008, EXP-009, EXP-010 rows)
- **EVIDENCE (commands + outputs / metric files):**
  - `grep -n "Lock:" company/experiments/EXP-001.md` → line 2 `**Lock:** DRAFT`.
  - Normalisation check: scratch script `/tmp/claude-1000/-workspaces-Efficient-Video-Editor/aaad3156-5fc0-4481-9dd9-f8ade7986944/scratchpad/norm.py` run on the §6.2 table → `10 True`. First run found my own wrong expected value (رئيس → "رييس", not "ريس"); the vector was corrected to what the rule produces and a note was added. No rule was changed.
  - Installed versions read for §3: `pip show` → faster-whisper 1.2.1, ctranslate2 4.9.0; `ctranslate2.set_random_seed` exists (True); `ffmpeg -version` → 6.1.1.
  - No ASR run; no clip opened; no `quarantine/` or `data/heldout/` access; EXP-006*/EXP-008* files not touched (`git status --short` shows only the three files above plus an untracked `H-0023-repro.txt` that is not mine).
- **DONE-WHEN CHECK:**
  - ✅ draft complete with thresholds and normalisation rules: EXP-001 §6.1–6.3 (thresholds marked † are proposals awaiting O1).
  - ✅ consultation block: EXP-001 "Consultation before lock" (Engineering, Creative, Assurance, all unsigned).
  - ✅ LOG entry: `company/positions/02-research/LOG.md`, H-0022.
- **DEVIATIONS FROM BRIEF:**
  1. Added an EXP-009 row to the register ("referenced, not drafted"), because `DATA_RIGHTS.md` RR-014 already uses that id; this prevents another id collision like EXP-007. Doc-only.
  2. Noted in EXP-001 that `experiments/e1_asr.py`'s normalisation (regex, no NFKC, no hamza-carrier rule) must be replaced by the §6.2 rule (Engineering item E3). I did not edit code.
- **OPEN QUESTIONS (numbered, with who should answer):**
  1. (Founder / product-lead) O1: confirm or replace the † thresholds: WER_LB pass ≤ 30% / kill > 50%, CER_LB 15% / 30%, RTF 1.5 / 5.0. These come from the product use, not from literature (dialect WERs in papers are on other dialects/datasets and do not transfer). Lock is blocked until this is answered.
  2. (Founder) O2: who transcribes and marks boundaries (default: Founder; must be a native Lebanese speaker; ≈ 3–5 h of human time).
  3. (Founder) O3: is a second transcriber available for the reliability check (inter-transcriber WER > 12% → INCONCLUSIVE)?
  4. (Operator / product-lead) O4: add a third ASR candidate before lock (new dependency, separate brief)?
  5. (Founder) O5: confirm the ARABIC_QA.md dialect policy (still "Founder to confirm").
- **CONFIDENCE:** Medium (biggest reason for doubt: the threshold numbers are my proposals and the dataset depends on a footage type that is still TBD; the boundary metric has survivorship bias toward easy words, which is reported but not removed).
- **NEXT RECOMMENDED STEP:** Founder answers O1–O5; then brief Engineering (E1–E6), Creative (C1–C4) and Assurance (A1–A3) to sign the consultation on the DRAFT. Lock only when footage with verified rights is in the manifest.
