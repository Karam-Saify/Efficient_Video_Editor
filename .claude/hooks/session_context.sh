#!/usr/bin/env bash
# SessionStart: print company state into Claude's context (FM-1.4 loss of history).
cd "${CLAUDE_PROJECT_DIR:-.}" || exit 0
echo "=== COMPANY STATE (company/state/STATE.md) ==="
if [ -f company/state/STATE.md ]; then head -60 company/state/STATE.md; fi
if grep -q '^HALT:' company/state/STATE.md 2>/dev/null; then
  echo ""; echo "!!! A HALT IS ACTIVE. Do no work except what the Founder asks to resolve it. !!!"
fi
echo ""; echo "=== GIT ==="
git status --short 2>/dev/null | head -20
echo "unpushed commits: $(git log --oneline @{u}..HEAD 2>/dev/null | wc -l | tr -d ' ')"
git log --oneline -5 2>/dev/null
echo ""; echo "Reminder: you are the Operator. Classify every request (T0-T3/E) per company/OPERATING_MODEL.md before acting."
exit 0
