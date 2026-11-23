# ADR-0025: Annotation record schema v0.1 (source + job) and the Footage Intelligence v0 hand-off
- **Status:** Proposed (Founder signs; assurance-lead reviews H-0035)
- **Date:** 2026-11-23 · **Tier:** T2 · **Door:** two-way while no partner record exists; one-way-ish after (records must be migrated)
- **Decider:** Founder · **Recommender:** engineering-lead (H-0035) · **Agree (veto holders):** assurance-lead · **Input:** ADR-0016, ADR-0022, ADR-0023, H-0034 (PARTNER_FEEDBACK_FORM FF-v0.1 mapping)

## Context
ADR-0023 item 1 asks for `schemas/annotation.schema.json` covering each source and each job, with `label_origin`
on every label and a `rights_id`. ADR-0022 says only human-verified data counts as evidence, so the record must
show, per label, who produced it and what the machine said before a person changed it.

## Options considered
1. One record per source and one per job, in one schema (`oneOf` on `record_type`). **Chosen.**
2. A single record per partner holding sources and jobs: big files, hard diffs, and deletion per clip gets harder.
3. Labels as flat item fields with one `label_origin` per scene: cannot say "partner fixed the role, not the description".

## Decision
- `schemas/annotation.schema.json` v0.1, validated by `src/describe/schema.py` (`python -m src.describe validate`).
- **Label shape:** every label is `{value, label_origin, machine_value?}`. Structural items (scene and segment
  boundaries, keyframes, the audio block, the transcript block) carry their own `label_origin`. A `human_verified`
  label on a source must keep `machine_value` (`E_DIFF_MISSING` otherwise).
- **Source record:** `video_id`, `rights_id` (`RR-<nnn>` or `RR-P<partner>-<n>`, PARTNER_INTAKE_FORM C10), media
  facts (probe metadata, not labels), provenance (ASR model, detector, VAD, rules version, describer, imported
  correction hashes), transcript with a language label per segment, audio signals, scenes with keyframes,
  description and role. Roles: `hook, product_intro, demo, proof, cta` (ADR-0023) plus `other`, so a partner can
  say "none of these".
- **Audio flags:** low words per speech-minute is `ASR_SUSPICIOUS`; low VAD coverage is `LOW_VAD_SPEECH`. There is
  no "no speech" flag (Founder rule from the S1 correction).
- **Job record:** the 11 keys of the FF-v0.1 mapping, 1:1, each wrapped as `{value, label_origin}` with the
  mapped origin fixed by `const` (`edits_delivered` = machine, the other 10 = human_verified). Admin keys:
  `job_id, partner_id, rights_ids[], consent_version, permissions{evaluation, product_development,
  training_consented}, training_usable` (`const false` while ADR-0020 stands). A job without permission 1 or 2 is
  `E_PERMISSION`. Free text is bounded (brief 1,000; audience and objective text 300; likes, dislikes and
  corrections 500 each; at most 50 corrections). Feedback fields (F1–F6) are optional until collected.
- **Unit deviation from the mapping:** `corrections[].t_start_s` becomes `t_start_ms` (integer ms; CONVENTIONS
  and I-4). Filled by code, never by an LLM.
- **Descriptions without an API (ADR-0023 zero cost):** `annotate` writes `describe/descriptions.todo.json`
  listing at most 4 keyframes; a Claude Code session reads only those images and fills the text;
  `apply-descriptions` merges it as `machine` labels with `provenance.describer` naming the session model.
- **Roles v0** are deterministic rules (`roles-v0`: position, speech overlap, scene length), always `machine`.
- **Corrections** come from the offline storyboard's JSON export; `import-corrections` sets the edited or
  confirmed labels to `human_verified` and keeps the machine value.

## Consequences
- Positive: every label is auditable for ADR-0022; partner and machine labels can be diffed per field.
- Negative: records are verbose (about 2x a flat record); a schema change after partner data exists needs a migration.
- Watch: if partners never touch transcripts, the segment labels stay machine-only and give EXP-012 nothing.
