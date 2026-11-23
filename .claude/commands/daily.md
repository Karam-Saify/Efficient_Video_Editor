---
description: Daily pilot report (cost, plan usage, Founding Creator Data Program progress)
---
Write or update `company/reports/<YYYY-MM-DD>/README.md` with a section "Daily (pilot)". Keep it ≤ 40 lines. Facts only; mark estimates.
1. **Cash cost today** (target $0, ADR-0023): list any paid API call, paid tool or storage. Sources: `cache/*/usage.jsonl`, the `src/cost` ledger, and the Founder's word. If there is none, write "$0 (no paid calls found)".
2. **Plan usage:** subagent tokens per handoff (from task notifications), plus an Operator estimate. Give the total, and the share spent on pilot work versus other work.
3. **Pilot progress against the day-1–10 targets:** partners recruited /5, source videos with rights /20–30 (count DATA_RIGHTS rows with consent), jobs delivered /5 (2 versions each), choices and corrections logged (count `label_origin = human_verified` records and job feedback records).
4. **Consent status per partner:** evaluation / product development / training (default OFF).
5. **Done today, blockers, Founder asks** (numbered).
6. Commit with `docs(report): daily <date>`, trailer `Role: operator`, then push.
