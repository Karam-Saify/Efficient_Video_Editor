# ADR-0023: Founding Creator Data Program, run as a zero-cost concierge pilot
- **Status:** Accepted · **Date:** 2026-11-23 · **Decider:** Founder · **Door:** one-way-ish (real partners and their personal data) · **Review:** day 10 of the pilot (2026-12-03)
- **Process note:** a Founder decision recorded directly, with no T3 vote. Assurance keeps its veto on consent and rights: no partner footage is ingested before the consent kit exists and the partner has signed it.

**Decision:** Run a concierge pilot with founding creator partners. The tooling is zero-cost:
- ASR, scenes, keyframes and audio signals use local, open-source tools only.
- Annotation and Director reasoning are done inside Claude Code sessions (no paid API) during the pilot. Self-serve API usage is optional and capped.

Deliverables:
1. `schemas/annotation.schema.json` covers each source video (scenes, keyframes, transcript with a language per segment, audio signals, creative roles hook/product_intro/demo/proof/cta, `label_origin` = machine | human_verified, `rights_id`) and each job (brief, audience, platform, objective, the partner's published version, likes/dislikes, edits delivered, partner choice, corrections, would-publish, would-pay).
2. A consent kit (Assurance) with three SEPARATE permissions: evaluation; product development; future model training (default OFF). It is in Arabic and English, with a partner intake form and a feedback form.
3. Footage Intelligence v0 (Engineering) turns a partner's clips into a storyboard (keyframes, scene descriptions, suggested roles) that the partner can correct. Corrections are stored as `human_verified`.
4. Public eval sets:
   - Common Voice Arabic (CC0): baseline now.
   - SHAMS (Levantine, including Lebanese): after Assurance confirms its licence.
   - Arabic Speech Corpus: MSA, non-commercial, internal eval only.
   - TimelineBench: evaluation reference only, never training data.
5. Targets for days 1–10: 5 partners (the Founder's store is #1), 20–30 source videos with rights, 5 jobs delivered with 2 versions each, and every choice and correction logged.

Cost (target $0) and plan usage are reported daily via `/daily`.

**Consistent with:** ADR-0013 (edit diffs are sensitive), ADR-0020 (no training; the training permission is collected but unused), ADR-0022 (human-verified labels are evidence; machine labels are not).
