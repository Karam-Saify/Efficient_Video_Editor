# BRIEF H-0021 (PR/FAQ draft for the chat-editor MVP, M0 0.9)
- **To:** product-lead · **Tier / Milestone:** T1 (docs, ADR-0005 fast lane) / M0 (0.9) · **Date:** 2026-11-22
1. **Objective (with why):** Draft the target user and problem statement as a PR/FAQ for the **chat-editor MVP** (the Founder's term), so the coming MVP pivot has a written customer story to test against.
2. **Inputs:** `company/positions/01-product/PRFAQ.md` (stub), `PERSONAS.md`, `UNIT_ECONOMICS.md`, `COMPETITORS.md`, `PLAYBOOK.md`; root `CLAUDE.md` (vision; first market: Arabic Shorts); `company/state/ROADMAP.md`; `company/reports/2026-11-22/README.md`
3. **Constraints:** The Founder's MVP-pivot prompt is NOT available to you or the Operator. Read "chat-editor MVP" as: a user edits a Short by chatting with an assistant that changes `timeline.json` (the LLM decides, code enforces; the renderer runs locally). State this reading at the top, and list every assumption as an open question for the Founder. Use the Amazon PR/FAQ shape: press release (≤ 1 page), customer FAQ, internal FAQ (cost per Short, risks, what we will not build). No number may be presented as fact without a source; label guesses as hypotheses. Web research ≤ 5 sources. No commit.
4. **Output:** `company/positions/01-product/PRFAQ.md` (draft v0); return `company/handoffs/H-0021-return.md`.
5. **Done when:** [ ] target user v0 + problem statement · [ ] PR + customer FAQ + internal FAQ · [ ] open-questions list for the Founder · [ ] LOG entry
6. **Out of scope:** roadmap changes, the pivot itself, pricing decisions.
7. **Effort budget:** max 20 tool calls · max 2 retries
8. **Escalate if:** the roadmap contradicts a chat-editor MVP in a way that needs a T3 decision. Note it; don't resolve it.
9. **Termination condition:** draft + return written; stop.
10. **Consulted positions:** Creative and Research comment at the pivot T3; none now.
