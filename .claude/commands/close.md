---
description: Close the session safely (update state, log, commit, push)
---
Session close protocol (Constitution I-8):
1. Update `company/state/STATE.md`: date, session number, Now/Next/Blockers/Open decisions/Key numbers. Keep it ≤ 60 lines.
2. Make sure every position that worked this session appended to its `LOG.md`.
3. `git add -A && git status` → show the Founder what will be committed; never commit media, `.env`, or `cache/`.
4. Commit `chore(state): session close <YYYY-MM-DD>` with trailer `Role: operator`, then `git push`.
5. Confirm "pushed: <commit hash>". If the push fails, say so clearly. The session is NOT closed until pushed.
