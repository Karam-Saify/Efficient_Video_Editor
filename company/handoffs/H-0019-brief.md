# BRIEF H-0019 (risk register review and re-score, M0 0.8)
- **To:** assurance-lead · **Tier / Milestone:** T1 / M0 (0.8) · **Date:** 2026-11-22
1. **Objective (with why):** Bring the risk register up to date with what this session learned, so criterion 0.8 is met on evidence rather than on a template.
2. **Inputs:** `company/state/RISK_REGISTER.md` (15 risks); `company/reports/2026-11-22/README.md` (Threats); `company/experiments/EXP-006-results.md`, `EXP-008-results.md`; `company/gates/M0/hook-test.txt`; H-0003, H-0004 and H-0009 reviews.
3. **Constraints:** Founder-required new risks: (a) silent font fallback / undeclared fonts; (b) AI-only Arabic judging (single LLM judge); (c) hook gaps: shell writes bypass protection, false positives on quoted text. Add any others you see (e.g. no usable footage; third-party data and privacy for the Trend work; stale stage cache). Re-score every risk on the register's own scale, each with exactly one owner position and a mitigation with a check date or gate. Do not delete risks; close them with a reason. Edit only RISK_REGISTER.md and your LOG.md. No commit.
4. **Output:** updated `company/state/RISK_REGISTER.md`; return `company/handoffs/H-0019-return.md` (risks added, re-scored and closed; top 5 by score).
5. **Done when:** [ ] the 3 Founder-named risks added · [ ] all risks re-scored with owners · [ ] LOG entry
6. **Out of scope:** fixing any risk; the hook code (H-0020).
7. **Effort budget:** max 15 tool calls · max 2 retries
8. **Escalate if:** a risk warrants a HALT (data loss, rights breach).
9. **Termination condition:** register + return written; stop.
10. **Consulted positions:** the owners named in the register are informed via STATE at /close.
