# ADR-0008: Recipe-first intelligence: small model selects + fills a recipe; big model only on miss
- **Status:** Accepted · **Date:** 2026-11-23 · **Decider:** Founder (after 3 independent stakeholder strategy memos) · **Door:** two-way · **Review:** M1 gate
- **Process note:** Founder decision recorded directly; no T3 five-position vote was held. Positions may file dissent at the M1 gate.

**Decision:** A small model selects a recipe and fills its typed params. A big model is called only on a miss (no recipe fits, or validation fails after fill). Every miss is logged to `company/positions/01-product/RECIPE_BACKLOG.md`.
