"""M0 exit criterion 0.1: feed synthetic PreToolUse payloads to .claude/hooks/protect.py.
Nothing protected is touched; the hook only judges the payload. Run from repo root:
    python3 company/gates/M0/hook_selftest.py > company/gates/M0/hook-test.txt
"""
import datetime, json, os, subprocess, sys

CASES = [
    ("Edit CONSTITUTION.md", "block", {"tool_name": "Edit", "tool_input": {"file_path": "company/CONSTITUTION.md"}}),
    ("Write into held-out set", "block", {"tool_name": "Write", "tool_input": {"file_path": "data/heldout/x.mp4"}}),
    ("Write .env", "block", {"tool_name": "Write", "tool_input": {"file_path": ".env"}}),
    ("Bash force-push", "block", {"tool_name": "Bash", "tool_input": {"command": "git push --force origin main"}}),
    ("Bash cat held-out media", "block", {"tool_name": "Bash", "tool_input": {"command": "ffprobe data/heldout/x.mp4"}}),
    ("Edit src/common.py", "allow", {"tool_name": "Edit", "tool_input": {"file_path": "src/common.py"}}),
    ("Bash git status", "allow", {"tool_name": "Bash", "tool_input": {"command": "git status"}}),
]

root = os.getcwd()
print(f"# Hook self-test {datetime.datetime.now(datetime.timezone.utc):%Y-%m-%dT%H:%M:%SZ}")
fails = 0
for name, want, payload in CASES:
    r = subprocess.run([sys.executable, ".claude/hooks/protect.py"], input=json.dumps(payload),
                       capture_output=True, text=True, env={**os.environ, "CLAUDE_PROJECT_DIR": root})
    got = "block" if r.returncode == 2 else "allow"
    ok = got == want
    fails += not ok
    print(f"{'PASS' if ok else 'FAIL'} | {name} | expect={want} got={got} exit={r.returncode} | {r.stderr.strip()}")
print(f"RESULT: {len(CASES) - fails}/{len(CASES)} passed")
sys.exit(1 if fails else 0)
