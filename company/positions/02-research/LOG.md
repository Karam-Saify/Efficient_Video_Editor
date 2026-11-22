# Work log: 02-research
<!-- Append-only. Newest at bottom. Format: company/templates/LOG_ENTRY.md. Read the last 20 lines before starting any task (FM-1.3). -->

### 2026-11-21 · SETUP · T2 · DONE
- Did: position created with charter, playbook, checklists.
- Evidence: company/positions/02-research/
- Learned: —
- Next: contribute to M0 pre-mortem.

### 2026-11-22 · H-0005 · T2 · DONE
- Did: preregistered and LOCKED EXP-006 (FFmpeg + libass Arabic caption correctness, Founder rule 10/10 correct and 0 Sev-1). Fixed params, exact command, fingerprints, INVALID/deviation and re-execution rules.
- Evidence: company/experiments/EXP-006.md (line 2 LOCKED); company/handoffs/H-0005-return.md; strings verbatim (diff vs ARABIC_QA.md clean, no invisible chars).
- Learned: lock was required before Eng/Creative consultation (SOP-R2 step 3 out of order). RR-001 font licence is still pending and is now a precondition. Brief criterion "0.3" is ROADMAP 0.7.
- Next: Assurance lock review; Creative confirms the "correct" definition; H-0006 render after RR-001 is recorded.

### 2026-11-22 · H-0006-ruling · T2 · DONE
- Did: ruled the EXP-006 render run (H-0006) INVALID under §8: libass resolved NotoSans-Regular.ttf for AR-05 (P e h i n o r), AR-08 (" ( )), AR-10 (–), which are exactly the properties those strings test. No rerun (deterministic, design gap, not execution error). Remedy: new EXP-007 with a declared font stack, coded cmap coverage check and a log-check positive control. PNGs must stay unviewed.
- Evidence: company/handoffs/H-0006-ruling.md; render/frames_check/render.log l.135-136, 224-225, 284-285; fc-query charset coverage output in ruling §1.
- Learned: my prereg listed non-Arabic code points but never checked font coverage for them; the prereg checklist needs a "font covers every code point" item. libass logs only the first missing glyph per event, so a log grep underestimates fallback.
- Next: Assurance review of the ruling; write EXP-006-results.md (INVALID); draft EXP-007 with Eng + Creative consulted before the lock; H-0007 on hold.
