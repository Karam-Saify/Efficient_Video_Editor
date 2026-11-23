# ADR-0016: Architecture: orchestrator, model_router, recipes, cost; describe/score/select get new roles
- **Status:** Accepted · **Date:** 2026-11-23 · **Decider:** Founder (CFO/CTO memo + competitor scan) · **Door:** two-way · **Review:** M1 gate
- **Process note:** Founder decision recorded directly; no position vote was held.

**Decision:** New packages: `src/orchestrator/`, `src/model_router/`, `src/recipes/`, `src/cost/` (`src/learning/` later). `src/describe`, `src/score` and `src/select` are unfrozen with new roles: cheap footage understanding, scoring, and adaptive evidence selection. Packages are created only when they have real code; a stub stays NOT_IMPLEMENTED (honest engine, H-0024).
