# ADR-0024: Retention limit for external personal data: 90 days maximum (amends DATA_POLICY item 4)
- **Status:** Proposed (Founder signs)
- **Date:** 2026-11-23 · **Tier:** T2 · **Door:** two-way (a shorter limit can be set at any time; a longer one needs a new ADR)
- **Decider:** Founder · **Recommender:** assurance-lead (H-0033 ruling 3, H-0034) · **Agree (veto holders):** assurance-lead · **Input:** product-lead (PROMPT_COLLECTION_FORM, EXP-011), ADR-0023

## Context
DATA_POLICY item 4 says edit diffs are "deleted on request with the user's media; retention limit to be set before any
external user (M-gate item)" and the policy says "extend only by ADR". Three collections are about to touch external
people: the prompt-collection form (H-0031), EXP-011 brand notes and clips, and the Founding Creator pilot (ADR-0023).
H-0033 approved 90 days as a maximum with conditions (a)–(e); this ADR records it so the policy actually changes.

## Options considered
| Option | Pros | Cons | Evidence |
|---|---|---|---|
| 30 days | Least exposure | Shorter than the 10-day pilot + follow-up (F6 published-version check) + EXP-011 analysis | ADR-0023 timeline |
| **90 days max, from collection, renewable only in writing** | Covers pilot, follow-up and analysis; simple to state in AR/EN | Human-verified labels from the pilot are deleted at day 90 unless the partner renews | H-0033 ruling 3 |
| Until deletion request | Keeps all labels | No limit: fails DATA_POLICY item 4's intent; hard to defend under Law 81/2018 | — |

## Decision
DATA_POLICY item 4 is amended to read:
> 4. Deleted on request with the user's media. **Retention limit: 90 days maximum from the date of collection** for all
> personal data from external people (form responses, waitlist emails, brand notes, partner clips and everything derived
> from them: transcripts, keyframes, annotations, edits, feedback). (a) The clock starts on the collection date of each
> item. (b) Deletion covers the hosting tool, every export, the Codespace (`quarantine/`, `cache/`, `out/`) and every local
> copy; each deletion is logged with its date (outside git; a no-personal-data line in DATA_RIGHTS). (c) After deletion
> only anonymised aggregate tallies may be kept; no excerpt, quote or "anonymised" free text is kept. (d) A partner may
> renew for another 90 days only by a written, dated reply to a day-80 reminder; silence means delete. (e) Deletion
> requests are honoured within 7 days through a channel that does not need email (form or WhatsApp/DM keyword + code).

## Consequences
- Positive: the consent texts (CONSENT_KIT CK-v0.1, PROMPT_COLLECTION_FORM, EXP-011) can state one true number.
- Negative: the ADR-0023 annotation corpus is not permanent. Keeping human-verified labels past 90 days needs the
  partner's renewal, recorded per partner. Product should plan the day-80 renewal ask.
- Harder: every artifact holding partner data needs a collection date (Engineering: `collected_on` in the annotation record).

## Reversal plan
Shortening the limit: edit by a new ADR, no data impact. Lengthening: a new ADR plus fresh consent from each person; data
already past 90 days cannot be restored (deletion is one-way by design).

## Dissent
None recorded. assurance-lead prediction: at day 80 at least one pilot partner will not answer the renewal ask, so their
labels will be deleted. Check at: pilot review 2026-12-03 + day-80 sweep.

## Review date / trigger
M-gate, or the first request to keep data longer, or a lawyer's review of Law 81/2018 (CONSENT_KIT §5).
