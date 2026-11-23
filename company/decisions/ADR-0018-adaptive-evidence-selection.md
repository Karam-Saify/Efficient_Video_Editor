# ADR-0018: Adaptive evidence selection (training-free)
- **Status:** Accepted · **Date:** 2026-11-23 · **Decider:** Founder (CFO/CTO memo + competitor scan) · **Door:** two-way · **Review:** M1 gate
- **Process note:** Founder decision recorded directly; no position vote was held.

**Decision:** A `FrameBudgetAllocator` sets the number of frames per video from scene count, motion, visual diversity, duration and task, and stops when coverage saturates. Results are cached by content hash + analysis version. Inspired by AKS (CVPR 2025) and CSES (2026); research-lead verifies both citations before the design is locked. CLAUDE.md rule 1 still applies: only a few keyframes go to the LLM.
