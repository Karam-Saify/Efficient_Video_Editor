# BRIEF H-0022 (draft EXP-001 Arabic ASR prereg; do NOT lock)
- **To:** research-lead · **Tier / Milestone:** T1 (docs, ADR-0005 fast lane) / M0 (0.7) · **Date:** 2026-11-22
1. **Objective (with why):** Draft the EXP-001 preregistration (Arabic ASR quality) now, so it can be consulted on and locked the day usable footage arrives.
2. **Inputs:** `company/positions/02-research/PLAYBOOK.md` (EXP register, SOP-R2), `company/templates/EXPERIMENT.md`, `company/experiments/EXP-008.md` (structure, including the consultation block), `experiments/E1.md`/`e1_asr.py` if present (exploratory only), `company/state/ASSUMPTIONS.md`, `data/golden/MANIFEST.md` (read only; clips are UNVERIFIED, not usable)
3. **Constraints:** Status `**Lock:** DRAFT`. **Founder: do NOT lock until footage with rights exists.** Leave the dataset section as a requirement (number of clips, duration, dialect mix, rights status) rather than naming files; never name or use the 4 UNVERIFIED clips, `quarantine/` or `data/heldout/`. Include the metric (e.g. WER/CER with Arabic normalisation rules fixed in advance), the reference-transcript procedure (who transcribes, Lebanese spelling policy per ARABIC_QA.md), pass/kill thresholds, deviations policy, and an Engineering + Creative + Assurance consultation block. No ASR runs. No commit.
4. **Output:** `company/experiments/EXP-001.md` (DRAFT); return `company/handoffs/H-0022-return.md`.
5. **Done when:** [ ] draft complete with thresholds and normalisation rules · [ ] consultation block · [ ] LOG entry
6. **Out of scope:** running ASR, locking, EXP-010 (the caption size successor).
7. **Effort budget:** max 20 tool calls · max 2 retries
8. **Escalate if:** thresholds can't be set without a Founder or Product decision; list them as open questions.
9. **Termination condition:** draft + return written; stop.
10. **Consulted positions:** Engineering (instrumentation), Creative (reference transcripts), Assurance (lock) sign later.
