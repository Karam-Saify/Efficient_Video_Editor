# BRIEF H-0034 (pilot · consent + licences)
- **To:** assurance-lead · **Tier / Milestone:** T2 (consent and rights are your veto domain; a Founder-mandated deliverable) / pilot day 1 · **Date:** 2026-11-23

1. **Objective (with why):** Make the Founding Creator pilot legally clean before any partner footage or public dataset is touched (ADR-0023). Consent and licences are the one-way doors in this program.
2. **Inputs:** `company/decisions/ADR-0023`, `ADR-0013`, `ADR-0020`, `ADR-0022`; `company/positions/05-assurance/DATA_POLICY.md`, `DATA_RIGHTS.md`; `company/handoffs/H-0033-review.md` (F1–F3, F5); `company/positions/01-product/PROMPT_COLLECTION_FORM.md`, `company/experiments/EXP-011-brand-brain.md`; `bench/README.md` (asset list).
3. **Constraints:**
   - Plain language in Arabic (Levantine-friendly MSA) **and** English. This is not legal advice: mark the clauses that need a lawyer before scale.
   - **Three separate permissions**, each its own checkbox, each revocable, none bundled:
     - (1) evaluation;
     - (2) product development;
     - (3) future model training, **default OFF**, unused until an ADR lifts ADR-0020.
   - Cover: third-party processors (the form host, GitHub/Codespaces, and Anthropic if Claude Code sees keyframes or transcripts); people appearing in clips (the partner warrants they have permission); music in clips; retention (90 days max unless renewed, per your H-0033 ruling); deletion request path without email (e.g. a WhatsApp/DM keyword, or the form); the Lebanese Law 81/2018 note.
   - Licences: read **primary sources** and cite URL + fetch date.
     - Common Voice Arabic: CC0, but check the access terms; download may need an account or acceptance.
     - SHAMS: the licence and whether commercial evaluation is allowed.
     - Arabic Speech Corpus: confirm non-commercial status; internal eval only.
     - TimelineBench: licence, evaluation reference only, never training.
     - If a source can't be read, record "unverified" and not usable.
4. **Output:**
   - `company/positions/05-assurance/CONSENT_KIT.md`: consent text ar + en, the three permissions, partner warranty, withdrawal.
   - `company/positions/05-assurance/PARTNER_INTAKE_FORM.md`: business, platforms, audience, footage list with a rights declaration per clip.
   - `company/positions/05-assurance/PARTNER_FEEDBACK_FORM.md`: per job: which version was chosen, likes/dislikes, corrections, would-publish, would-pay. Fields must map 1:1 to the ADR-0023 job fields.
   - DATA_RIGHTS rows: RR-026+ for the public eval sets and the H-0033 F5 bench assets.
   - The ADR amending DATA_POLICY §4 retention (next free ADR number; Proposed, Founder signs).
   - Patch PROMPT_COLLECTION_FORM and EXP-011 for F1–F3 (fast lane).
   - Return at `company/handoffs/H-0034-return.md`.
5. **Done when:**
   - [ ] The three permissions are separate, and training is default OFF in both languages.
   - [ ] Each eval set has a licence verdict with a primary source, or "unverified, not usable".
   - [ ] The feedback form fields match the ADR-0023 job fields (include the mapping table).
   - [ ] H-0033 F1, F2, F3 and F5 are closed, or each is explicitly carried over with a reason.
6. **Out of scope:** schema files (engineering-lead writes `annotation.schema.json` next, from your field mapping); contacting partners; downloading datasets.
7. **Effort budget:** max 35 tool calls.
8. **Escalate if:** a dataset forbids even internal commercial evaluation; the consent model needs a lawyer before even pilot day 1 (say so plainly).
9. **Termination condition:** files committed (`Role: assurance-lead`, `Tier: T2`), but not pushed. Commit each finished file as you go.
10. **Consulted:** product-lead's files are patched by you under the fast lane. Engineering consumes the field mapping.
