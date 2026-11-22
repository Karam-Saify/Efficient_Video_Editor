# RETURN H-0021
- **From:** product-lead
- **STATUS:** DONE (with one roadmap flag for the Operator; not resolved, per brief field 8)
- **SUMMARY (≤5 lines):**
  PRFAQ v0 written for the chat-editor MVP. It opens with the stated reading: chat → small `timeline.json` change, the LLM decides, code enforces, local render.
  The target user is P1, the Founder-creator. P2 is an explicit hypothesis and P3 is out of the MVP. The problem statement is sourced for 2 competitors' Arabic/RTL gaps.
  The draft contains a press release, 5 customer FAQs and 5 internal FAQs (assumption IDs A-02..A-10), a "will not build" list and 9 open questions for the Founder.
  All business numbers are labelled E0/[H]. Competitor prices are cited from 5 web sources [S1–S5], seen through search summaries only.
  Possible T3 conflict: if the chat editor is meant to come before or replace M2–M3, the milestone order changes.
- **ARTIFACTS (paths):** `company/positions/01-product/PRFAQ.md` (draft v0); this return; LOG entry in `company/positions/01-product/LOG.md`
- **EVIDENCE:** PRFAQ §1–§5 and its Sources list. Inputs read: ROADMAP.md (M4 = natural-language revisions; M0 0.9), PERSONAS.md,
  ASSUMPTIONS.md (A-01..A-10), the reports/2026-11-22 README (0.9 not started), and the EXP-008 FAIL 8/10 result (commit `1cd79e1`). UNIT_ECONOMICS.md and COMPETITORS.md were empty templates.
- **DONE-WHEN CHECK:**
  - ✅ Target user v0 + problem statement: PRFAQ §1
  - ✅ PR + customer FAQ + internal FAQ: PRFAQ §2, §3, §4 (cost per Short, risks and "will not build" are in §4)
  - ✅ Open-questions list for the Founder: PRFAQ §5 (9 items)
  - ✅ LOG entry: `company/positions/01-product/LOG.md`
- **DEVIATIONS FROM BRIEF:**
  1. Competitor facts were not written into `COMPETITORS.md`, because it is not a brief output. They live only in the PRFAQ Sources. Proposed follow-up: a SOP-P5 entry.
  2. Sources were read through web-search summaries, not fetched pages, to stay inside the 20-call budget. They are labelled "E1 at best", and Research should verify them at T2/T3.
  3. SOP-P1 calls a PR/FAQ T2 (Research checks evidence, Assurance checks risks). The brief runs it as T1 fast lane, and I did not change that. Recommend a review at the pivot T3.
- **ROADMAP FLAG (brief field 8, noted, not resolved):** The chat editor matches **M4 (Editing loop)**, which sits after M1 ASR, M2 MILP skeleton and M3 LLM scoring.
  If the Founder means the chat editor *is* M4, built on M1–M3, there is no contradiction. If he means it comes first, or replaces auto-selection
  (M2 2.1–2.4, M3 3.2–3.3 and the M3 kill criterion), the milestone definitions change. That is a T3 change (ROADMAP.md header). → Founder Q1.
- **OPEN QUESTIONS (numbered, with who should answer):**
  1. Founder: is the chat editor M4-on-top-of-M1–M3, or does it come before or replace M2–M3? (decides whether a T3 is needed)
  2. Founder: is the MVP for P1 only, or for P2 from day one?
  3. Founder: may transcript text go to a cloud LLM? (privacy answer in customer FAQ 4)
  4. Founder: the remaining Qs 3–9 in PRFAQ §5 (chat surface, starting cut, footage type, dialect, definition of done, token cap)
  5. Research: verify [S1–S5] and add CapCut and other Arabic-capable tools before any competitive claim is used at a gate.
- **CONFIDENCE:** Medium (biggest reason for doubt: the reading of "chat-editor MVP" is a guess without the Founder's prompt, and every business claim is E0)
- **NEXT RECOMMENDED STEP:** Operator puts PRFAQ §5 Q1–Q3 to the Founder. If the answer to Q1 is "before or instead of M2–M3", open a T3 roadmap change. Otherwise mark M0 0.9 as having an evidence path.

Sources: [S1] https://opus.pro/pricing · [S2] https://help.opus.pro/docs/article/does-opusclip-support-languages-right-left ·
[S3] https://www.castmagic.io/blog/opus-clip-pricing · [S4] https://help.descript.com/script-editing/supported-transcription-languages.md ·
[S5] https://sonix.ai/resources/descript-pricing/
