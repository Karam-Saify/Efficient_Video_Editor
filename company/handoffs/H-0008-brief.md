# BRIEF H-0008 (fallback font rights record)
- **To:** assurance-lead
- **Tier / Milestone:** T1 / M0
- **Date:** 2026-11-22
<!-- Dispatched inline by the Operator; filed here afterwards so the handoff record is complete. -->

1. **Objective (with why):** Record rights for NotoSans-Regular.ttf, which libass used as the fallback font for Latin glyphs in the EXP-006 render. No record means no use (I-9).
2. **Inputs (exact paths):** `render/frames_check/render.log`; `/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf`; `/usr/share/doc/fonts-noto-core/copyright`; `company/positions/05-assurance/DATA_RIGHTS.md`
3. **Constraints:** Primary sources on this machine only; do not touch H-0004 files; no commit.
4. **Output:** row RR-011 in DATA_RIGHTS.md; `company/handoffs/H-0008-return.md`
5. **Done when:** [ ] RR-011 has version, sha256, package, license, commercial use, date, EXP-006 usage note · [ ] LOG line appended
6. **Out of scope:** Deciding the renderer's font stack.
7. **Effort budget:** max 10 tool calls · max 2 retries
8. **Escalate if:** License can't be confirmed (mark pending).
9. **Termination condition:** Row + return written; stop.
10. **Consulted positions:** Engineering/Creative informed via the return (font-stack question).
