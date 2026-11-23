#!/usr/bin/env python3
"""PreToolUse guard for the Company OS.
Blocks (exit 2, reason on stderr):
  - edits to company/CONSTITUTION.md (Founder edits by hand)
  - edits to ADRs whose Status is Accepted (supersede instead)
  - edits to experiments marked 'Lock: LOCKED' (create a new EXP instead)
  - any write under data/heldout/ except ACCESS_LOG.md (custody: Assurance at gates)
  - writing .env / secret files
  - destructive git / shell commands on Bash
Fails open (exit 0) on unexpected input so a broken hook never blocks all work."""
import json, os, re, sys

def block(msg):
    print(f"BLOCKED by company policy: {msg}", file=sys.stderr)
    sys.exit(2)

try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)

tool = data.get("tool_name", "")
ti = data.get("tool_input", {}) or {}
root = os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or os.getcwd()

def rel(p):
    try:
        return os.path.relpath(os.path.abspath(os.path.join(root, p)), root).replace("\\", "/")
    except Exception:
        return p

def read(path):
    try:
        with open(os.path.join(root, path), encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""

if tool in ("Edit", "Write", "MultiEdit", "NotebookEdit"):
    fp = ti.get("file_path") or ti.get("notebook_path") or ""
    r = rel(fp)
    exists = os.path.exists(os.path.join(root, r))
    if r == "company/CONSTITUTION.md":
        block("CONSTITUTION.md is Founder-only. Propose the change in an ADR; Kareem edits by hand.")
    if r.startswith("data/heldout/") and r != "data/heldout/ACCESS_LOG.md":
        block("data/heldout/ is sealed (Constitution I-6). Only Assurance, at a gate, via the access log.")
    if re.search(r"(^|/)\.env(\.|$)|credentials|secret", r, re.I):
        block("Writing secret/credential files is not allowed in the repo.")
    if exists and re.match(r"company/decisions/ADR-\d+", r):
        if re.search(r"\*\*Status:\*\*\s*Accepted", read(r)):
            block(f"{r} is Accepted (Constitution I-7). Write a new ADR that supersedes it.")
    if exists and re.match(r"company/experiments/EXP-\d+\.md$", r):
        if re.search(r"\*\*Lock:\*\*\s*LOCKED", read(r)):
            block(f"{r} is LOCKED (Constitution I-5). Results go in EXP-xxx-results.md; design changes need a new EXP id.")

if tool == "Bash":
    cmd = ti.get("command", "")
    patterns = [
        (r"git\s+push\s+.*(--force|-f\b)", "Force-push is forbidden. Use a revert commit."),
        (r"git\s+reset\s+--hard", "git reset --hard can destroy work. Stash or revert instead; if truly needed, the Founder runs it."),
        (r"git\s+clean\s+-[a-z]*f", "git clean -f deletes untracked files. Founder only."),
        (r"rm\s+-[a-z]*r[a-z]*\s+.*\b(company|data|schemas|src|\.git)\b", "Recursive delete of a core directory is forbidden."),
        (r"data/heldout/[^\s]*\.(mp4|mov|mkv|wav|mp3)", "Direct access to held-out media outside the gate procedure (I-6)."),
    ]
    for pat, msg in patterns:
        if re.search(pat, cmd):
            block(msg)
sys.exit(0)
