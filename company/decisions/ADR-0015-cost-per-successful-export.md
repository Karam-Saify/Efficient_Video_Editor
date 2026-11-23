# ADR-0015: Efficiency metrics: cost per successful export, and quality÷cost
- **Status:** Accepted · **Date:** 2026-11-23 · **Decider:** Founder (CFO/CTO memo + competitor scan) · **Door:** two-way · **Review:** M1 gate
- **Process note:** Founder decision recorded directly; no position vote was held.

**Decision:** Amends ADR-0011. The cost metric is **cost per SUCCESSFUL export**: total spend, including retries and failed or abandoned runs, ÷ successful exports. Ceiling $0.01, stretch $0.005. A second metric, **quality ÷ cost** (rubric score ÷ cost per successful export), is used to compare options. Both are added to `company/state/METRICS.md`.
