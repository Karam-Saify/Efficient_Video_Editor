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

### 2026-11-22 · H-0010 · T2 · DONE
- Did: wrote EXP-006-results.md (verdict INVALID, deviations D1-D5, evidence hashes, no PNG judged). Drafted EXP-007 (Lock: DRAFT) with the declared pair Noto Sans Arabic + Noto Sans, an exact run-splitting rule with expected tagged-text fingerprints, a coded coverage check, controls C0/C1/C2 and a consultation block.
- Evidence: company/experiments/EXP-006-results.md; company/experiments/EXP-007.md; company/handoffs/H-0010-return.md; fc-query charset coverage of both fonts (Noto Sans covers every non-Arabic code point; U+0E01 is in neither).
- Learned: the ID "EXP-007" was already reserved in the PLAYBOOK register, ROADMAP 4.2 and A-05 (revision diffs, M4). Check the register before assigning ids. libass \fn makes per-run fonts expressible, so no escalation.
- Next: Operator resolves the ID collision; Eng + Creative sign the consultation; then lock EXP-007.

### 2026-11-22 · H-0012 · T1 · DONE
- Did: applied creative-lead objections O1 (font-switch category, §6 after the "correct" definition) and O2 (line wrapping, §5.4 step 10 after "clipping,") to EXP-008.md verbatim from H-0011-return.md; added the "applied verbatim" note to the Creative sign-off line. Lock stays DRAFT; not committed.
- Evidence: company/experiments/EXP-008.md (lines 125, 139-144, 213); `git diff --stat` = 9 insertions, 2 deletions (step-10 line and sign-off line changed in place); company/handoffs/H-0012-return.md.
- Learned: two stale spots remain outside the brief: §8 threats row "Open consultation item C2" and the `exp007` paths/instrument name; fix before lock, not now.
- Next: engineering-lead signs E1-E5; Creative one-line re-confirm (optional, text is verbatim); then research-lead locks EXP-008.

### 2026-11-22 · H-0014 · T2 · DONE
- Did: LOCKED EXP-008. Applied Eng G1–G3 verbatim (14 render/exp008 paths, 2 exp008_render.py, rule-(b) regex, 0xE01). Fixed stale §8 C2 threats row (O1 resolved it). Recorded the Operator ruling that Creative need not re-sign. Single Write of the complete file. Not committed.
- Evidence: company/experiments/EXP-008.md sha256 5d3cdb54…73da, byte-identical to the asserted scratch build (diff → IDENTICAL_TO_VERIFIED); grep exp007 → ID note only; company/handoffs/H-0014-return.md.
- Learned: build the locked text with count-asserted replacements in scratch and diff it after the Write. Assurance pre-lock verifiability was not signed separately. Add Assurance to future consultation blocks.
- Next: Assurance reviews H-0014; Operator briefs engineering-lead for exp008_render.py and §5.4 steps 1–9.

### 2026-11-22 · H-0018 · T2 · DONE
- Did: appended §8 "Research analysis" to EXP-008-results.md: FAIL confirmed (N_correct 8, N_sev1 0), E2 with no downgrade, limited claim (failed: cross-font size 1.61–1.63× alef vs 1.3×; passed: per-run font assignment, shaping, bidi), deviations D1–D5 all non-invalidating, threats, successor named EXP-010; filled the header evidence-level placeholder.
- Evidence: company/experiments/EXP-008-results.md §8; company/handoffs/H-0018-return.md; grep for EXP-010 returned no hits.
- Learned: a single nominal font size cannot match Latin caps, digits and x-height to Arabic alef at once (x-height already 1.24×); the successor needs a Founder-calibrated band (upper and lower), set before lock.
- Next: Assurance T2 review; Founder calibrates the ratio band; Operator adds A-11 and registers EXP-010; then draft EXP-010.

### 2026-11-22 · H-0022 · T1 · DONE
- Did: drafted EXP-001 (Arabic ASR, 2 faster-whisper models, blind human references, 9-step normalisation with 10 test vectors, WER_LB + P90 boundary error primary, Eng/Creative/Assurance consultation block); Lock stays DRAFT per Founder. Fast-lane docs: A-11 added to ASSUMPTIONS.md; register now has Status (EXP-006 INVALID, EXP-008 FAIL, EXP-009 reserved, EXP-010 registered). Not committed.
- Evidence: company/experiments/EXP-001.md (line 2 DRAFT); scratch normaliser reproduces all 10 vectors; company/handoffs/H-0022-return.md.
- Learned: write the normalisation test vectors and run them before they go into a prereg; one of my expected values (رئيس) was wrong. E1's "hand-correct one model's output" reference method biases toward that model, so EXP-001 requires blind references.
- Next: Founder answers O1 (thresholds) to O5; three consultation sign-offs; lock only when footage with verified rights exists.

### 2026-11-23 · H-0036 · T2 · BLOCKED
- Did: stopped under brief field 3: Common Voice ar 27.0 (RR-026, CC0) needs an MDC account and terms acceptance by the Founder. No download, no EXP-013. Gave the Founder 5 exact steps. One endpoint probe was denied by the classifier and not retried.
- Evidence: company/handoffs/H-0036-return.md; H-0034 F7; RR-026.
- Learned: probe download gates with a plain page GET only; never guess API endpoints.
- Next: Founder downloads the test split to quarantine/; then lock EXP-013 and run.
