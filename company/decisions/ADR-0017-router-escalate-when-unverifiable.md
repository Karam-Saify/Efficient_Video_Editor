# ADR-0017: Router rule: deterministic → cache → small model → large model
- **Status:** Accepted · **Date:** 2026-11-23 · **Decider:** Founder (CFO/CTO memo + competitor scan) · **Door:** two-way · **Review:** M1 gate
- **Process note:** Founder decision recorded directly; no position vote was held.

**Decision:** Every decision is tried in order: deterministic code, then cache, then the small model, then the large model. Escalation to the next level happens only when validation or coverage checks fail ("escalate when unverifiable"). Refines ADR-0008.
