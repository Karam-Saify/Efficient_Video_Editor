# Work log: 04-creative
<!-- Append-only. Newest at bottom. Format: company/templates/LOG_ENTRY.md. Read the last 20 lines before starting any task (FM-1.3). -->

### 2026-11-21 · SETUP · T2 · DONE
- Did: position created with charter, playbook, checklists.
- Evidence: company/positions/04-creative/
- Learned: —
- Next: contribute to M0 pre-mortem.

### 2026-11-22 · H-0011 · T2 · DONE
- Did: EXP-008 consultation; C1 agreed + O2 (add wrap/mid-word check), C2 definition kept + O1 font-switch category with Sev anchors, C3 agreed; Creative line signed with objections O1, O2.
- Evidence: company/experiments/EXP-008.md (Creative sign-off line), company/handoffs/H-0011-return.md
- Learned: mixed-font captions need numeric anchors (height ratio, baseline step) or the judge falls back to "feels off"; anchors 1.3x/0.6x are uncalibrated.
- Next: re-confirm once research-lead applies O1/O2; judge EXP-008 renders in a later brief (non-exposure to EXP-006 PNGs declared).

### 2026-11-22 · H-0016 · T2 · DONE
- Did: judged EXP-008 AR-01..10 at 200% against the raw strings (step 10, §6 with O1/O2). N_correct=8, N_sev1=0, verdict FAIL: AR-04 and AR-05 font-switch (b) Sev-2 (Latin/ASCII digit height 1.61-1.63× alef). Sev-3 notes on AR-08 and AR-10. Schema v0 + has_audio is enough.
- Evidence: company/experiments/EXP-008-results.md, company/handoffs/H-0016-return.md
- Learned: Noto Sans vs Noto Sans Arabic at the same size gives about 1.6× cap/alef, so mixed captions need a per-script size factor. Measure O1 anchors from pixel segments; my eye misjudged the AR-09 tatweel lengths, which measured equal.
- Next: Founder spot-check to calibrate the 1.3× anchor; judge the size-parity fix under its new EXP id.

### 2026-11-23 · H-0028 · T1 · DONE
- Did: wrote 12 recipes (beats, hook rule, pacing, preset, typed params, principles, needs) and a principles table; tiered against today's ops: A=4 (R01 R03 R07 R08), B=7, C=1 (R11).
- Evidence: company/handoffs/H-0028-recipes.md, company/handoffs/H-0028-return.md
- Learned: set_caption_style is global, so per-beat hook looks are a need; captions exist only for spoken words, so any unspoken text (price, title, badges) needs a text overlay; R12 stays ship-gated by the EXP-008 Sev-2 font-switch.
- Next: confirm escalation reading with Operator; judge tier-A recipes once H-0029 formalises them.
