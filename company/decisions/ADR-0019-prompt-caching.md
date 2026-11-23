# ADR-0019: Prompt caching on all Claude API calls
- **Status:** Accepted · **Date:** 2026-11-23 · **Decider:** Founder (CFO/CTO memo + competitor scan) · **Door:** two-way · **Review:** M1 gate
- **Process note:** Founder decision recorded directly; no position vote was held.

**Decision:** Every Claude API call puts the stable prefix first (system, schema, recipe definitions, rubric) and the variable footage or user data last, using prompt caching. Cached and uncached input tokens are logged per call in `cache/<id>/usage.jsonl`.
