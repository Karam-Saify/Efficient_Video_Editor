# BRIEF H-0031 (Week 1 · D)
- **To:** product-lead · **Tier / Milestone:** T1 (fast lane: docs/copy) / M1 · **Date:** 2026-11-23

1. **Objective (with why):** Prepare three demand instruments: a 50-prompt collection form, a Brand Brain test protocol and fake-door copy. We need real creator language and willingness signals before building Brand Brain, auto-posting or extra variants (ADR-0007 Creative Director, ADR-0008 recipe-first).
2. **Inputs:** `company/decisions/ADR-0007..0013`; `company/positions/01-product/{PRFAQ,PERSONAS,UNIT_ECONOMICS}.md`; `company/positions/05-assurance/DATA_POLICY.md`; `company/templates/EXPERIMENT.md` (§0 decision brief, ADR-0012).
3. **Constraints:**
   - Everything is copy-ready in Arabic (Lebanese-friendly MSA) **and** English, and code-switch friendly (ADR-0010).
   - **Personal data:** the form and the protocol include plain consent text, a stated purpose, retention and deletion (DATA_POLICY; ADR-0013 treats edit diffs and prompts as sensitive). No collection starts until the Founder picks the tool (Google Forms / Tally / other): you write the content, not the hosting.
   - The fake-door copy must be honest: on click it says "coming soon, join the waitlist", with no fake functionality or payment capture. Measure clicks/joins only.
   - Brand Brain protocol: 3 businesses × 5 posts, blind A/B (brand-tuned vs generic), with the ADR-0012 decision brief at the top (recommendation, reasoning, first experiment, numeric success threshold, "if it fails, then"). Write it in the format of `company/templates/EXPERIMENT.md`.
4. **Output:**
   - `company/positions/01-product/PROMPT_COLLECTION_FORM.md`: questions, field types, the target of 50 prompts, quotas by niche and language, consent block.
   - `company/experiments/EXP-011-brand-brain.md`: DRAFT, not locked; research-lead signs later.
   - `company/positions/01-product/FAKE_DOOR_COPY.md`: 3 doors (Brand Brain, auto-posting, extra variants), each with button label, modal copy, waitlist confirmation and the metric + threshold.
   - Return at `company/handoffs/H-0031-return.md`.
5. **Done when:**
   - [ ] All three files exist, with ar + en copy.
   - [ ] EXP-011 §0 has a numeric success threshold and an "if it fails, then".
   - [ ] Each fake door has a numeric go/no-go threshold.
6. **Out of scope:** hosting forms, contacting businesses, pricing changes, new governance docs.
7. **Effort budget:** max 20 tool calls.
8. **Escalate if:** a protocol step needs real user data before the Founder approves the tool and consent.
9. **Termination condition:** files written and committed (`Role: product-lead`, `Tier: T1`), but not pushed.
10. **Consulted:** research-lead (EXP-011 lock, later); assurance-lead (consent text, at the daily review).

## Addendum (Operator, Founder memo 2: supersedes where it conflicts)
- The fake doors are now: **Brand Brain**, **auto-posting** and **per-video pricing**. For the pricing door, use AdKraft's ~$3/video only as a *reference point*; we do not copy it. "Extra variants" becomes an optional 4th door.
- Add an **AdKraft** entry to `company/positions/01-product/COMPETITORS.md`: what it does, its pricing model, the ~$3/video figure with a cited primary source (pricing page URL + fetch date), and our differentiator. If you can't verify the figure from a primary source, write "unverified (Founder-reported)".
- The Brand Brain protocol (EXP-011) stays in scope.
- **Commit cadence (Founder):** commit each finished unit, with tests passing, about every 5 min of work. Do not push; the Operator pushes.
