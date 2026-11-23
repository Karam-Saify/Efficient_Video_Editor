# Recovery Runbook
Use when: a session crashed, context was lost, the repo looks confusing, or you return after a break of more than a week.
Rule: **reconstruct before you change anything.**

1. **Freeze.** Do not edit files. If anything suggests data loss or a leaked secret, write `HALT:` in STATE.md and tell the Founder.
2. **Read state:** `company/state/STATE.md` → `company/state/ROADMAP.md` (current milestone) → `company/decisions/INDEX.md` (last 5).
3. **Read the repo's truth:**
   - `git status`: uncommitted changes? Run `git diff --stat` and identify which position's area they are in.
   - `git log --oneline -20` + trailers (`Role:`, `Tier:`): what was last done, by which position?
   - `git log @{u}..HEAD`: unpushed commits? Push them first if the tree is otherwise clean.
   - `git stash list`: forgotten stashes?
   - Open handoffs: briefs in `company/handoffs/` without a matching `-return.md` or `-review.md`.
4. **Write a reconstruction** (≤ 20 lines) in chat: what was in progress, what is uncommitted, what is unreviewed, what is unclear. Ask the Founder to confirm.
5. **Repair:**
   - Uncommitted work that matches an open brief → commit it on `t2/<brief-id>` and send to Assurance review. Never straight to `main`.
   - Uncommitted work with no brief → move it to a branch `recovery/<date>` and commit. Product decides whether to keep it.
   - Unreviewed T2 on `main` → open a retroactive Assurance review now.
6. **Update STATE.md**, commit `chore(recovery): <date>`, push.
7. If the cause was a process gap, open an incident (`/incident`) so the operating model learns.
