"""H-0020: .claude/hooks/protect.py blocks shell writes to protected paths, allows text that only
mentions commands. Hermetic: each case runs against a throw-away project tree (tmp_path) via
CLAUDE_PROJECT_DIR, feeding the PreToolUse JSON payload on stdin. PROTECT_HOOK overrides the hook
path (used to test a candidate copy before installing it)."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
HOOK = Path(os.environ.get("PROTECT_HOOK") or ROOT / ".claude" / "hooks" / "protect.py")

C = "company/CONSTITUTION.md"
ADR = "company/decisions/ADR-0001-accepted.md"
ADR_P = "company/decisions/ADR-0009-proposed.md"
EXP = "company/experiments/EXP-001.md"
EXP_U = "company/experiments/EXP-002.md"
HELD = "data/heldout/clip.json"
Q = "quarantine/samples.zip"


@pytest.fixture(scope="module")
def project(tmp_path_factory) -> Path:
    p = tmp_path_factory.mktemp("proj")
    files = {
        C: "# Constitution\n",
        ADR: "# ADR-0001\n**Status:** Accepted\n",
        ADR_P: "# ADR-0009\n**Status:** Proposed\n",
        EXP: "# EXP-001\n**Lock:** LOCKED\n",
        EXP_U: "# EXP-002\n**Lock:** DRAFT\n",
        "data/heldout/ACCESS_LOG.md": "log\n",
        HELD: "{}\n",
        Q: "PK\x03\x04",
        "company/handoffs/.keep": "",
        "README.md": "hello\n",
        "src/a.py": "x = 1\n",
    }
    for rel, text in files.items():
        f = p / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(text, encoding="utf-8")
    return p


def run(project: Path, payload) -> subprocess.CompletedProcess:
    data = payload if isinstance(payload, str) else json.dumps({**payload, "cwd": str(project)})
    env = {**os.environ, "CLAUDE_PROJECT_DIR": str(project)}
    return subprocess.run([sys.executable, str(HOOK)], input=data, capture_output=True, text=True,
                          env=env, cwd=project, timeout=30)


def bash(cmd: str) -> dict:
    return {"tool_name": "Bash", "tool_input": {"command": cmd}}


def tool(name: str, path: str) -> dict:
    return {"tool_name": name, "tool_input": {"file_path": path}}


MUST_BLOCK = [
    # Constitution x write vectors
    ("const-append", bash(f"echo x >> {C}")),
    ("const-redirect-1>", bash(f"echo x 1> {C}")),
    ("const-redirect-&>", bash(f"make &> {C}")),
    ("const-tee-a", bash(f"echo x | tee -a {C}")),
    ("const-sed-i", bash(f"sed -i 's/a/b/' {C}")),
    ("const-cp-dest", bash(f"cp README.md {C}")),
    ("const-mv-dest", bash(f"mv README.md {C}")),
    ("const-truncate", bash(f"truncate -s 0 {C}")),
    ("const-dd-of", bash(f"dd if=/dev/zero of={C} count=1")),
    ("const-after-cd", bash("cd company && echo x > CONSTITUTION.md")),
    ("const-envvar", bash("echo x >> $CLAUDE_PROJECT_DIR/company/CONSTITUTION.md")),
    ("const-heredoc-redirect", bash(f"cat > {C} <<'EOF'\nnew text\nEOF")),
    ("const-bash-c", bash(f"bash -c 'echo x >> {C}'")),
    ("const-python-c", bash(f"python3 -c \"open('{C}', 'a').write('x')\"")),
    ("const-python-heredoc", bash(f"python3 - <<'EOF'\nfrom pathlib import Path\nPath('{C}').write_text('x')\nEOF")),
    ("const-cp-into-dir", bash("cp /tmp/CONSTITUTION.md company/")),
    ("const-edit-tool", tool("Edit", C)),
    # Accepted ADR
    ("adr-redirect", bash(f"echo x >> {ADR}")),
    ("adr-tee", bash(f"tee {ADR} < README.md")),
    ("adr-sed-i", bash(f"sed -i.bak 's/Accepted/Proposed/' {ADR}")),
    ("adr-cp", bash(f"cp README.md {ADR}")),
    ("adr-mv-source", bash(f"mv {ADR} /tmp/old.md")),
    ("adr-rm", bash(f"rm {ADR}")),
    ("adr-write-tool", tool("Write", ADR)),
    # Locked EXP
    ("exp-redirect", bash(f"printf 'x' > {EXP}")),
    ("exp-tee", bash(f"echo x | tee {EXP}")),
    ("exp-sed-i", bash(f"sed -E -i 's/LOCKED/DRAFT/' {EXP}")),
    ("exp-perl-i", bash(f"perl -pi -e 's/LOCKED/DRAFT/' {EXP}")),
    ("exp-cp", bash(f"cp {EXP_U} {EXP}")),
    ("exp-mv-dest", bash(f"mv {EXP_U} {EXP}")),
    ("exp-glob", bash("sed -i 's/x/y/' company/experiments/EXP-*.md")),
    # held-out
    ("held-redirect", bash(f"echo x > {HELD}")),
    ("held-tee", bash(f"echo x | tee -a {HELD}")),
    ("held-sed-i", bash(f"sed -i 's/a/b/' {HELD}")),
    ("held-cp-into-dir", bash("cp README.md data/heldout/")),
    ("held-mv", bash(f"mv README.md {HELD}")),
    ("held-rsync", bash("rsync -a src/ data/heldout/new/")),
    ("held-media-probe", bash("ffprobe data/heldout/x.mp4")),
    ("held-write-tool", tool("Write", "data/heldout/x.mp4")),
    # quarantine: no open / extract / use
    ("quar-unzip", bash(f"unzip {Q} -d /tmp/x")),
    ("quar-cat", bash(f"cat {Q}")),
    ("quar-cp-from", bash(f"cp {Q} /tmp/")),
    ("quar-input-redirect", bash(f"python3 -m zipfile -l < {Q}")),
    ("quar-python", bash("python3 -c \"import zipfile; zipfile.ZipFile('quarantine/samples.zip').extractall()\"")),
    ("quar-write", bash("echo x > quarantine/note.txt")),
    ("quar-git-add", bash("git add quarantine/")),
    ("quar-glob", bash("cat quarantine/*")),
    ("quar-write-tool", tool("Write", "quarantine/x.txt")),
    ("quar-find-exec", bash("find quarantine -name '*.zip' -exec unzip {} \\;")),
    # secrets
    ("env-redirect", bash("echo KEY=1 > .env")),
    ("env-write-tool", tool("Write", ".env")),
    # destructive git / shell, in command position
    ("git-force-push", bash("git push --force origin main")),
    ("git-force-push-f", bash("git push -f origin main")),
    ("git-force-push-plus", bash("git push origin +main")),
    ("git-reset-hard-after-and", bash("git status && git reset --hard HEAD~1")),
    ("git-reset-hard-after-semicolon", bash("ls; git reset --hard")),
    ("git-clean-fd", bash("git clean -fd")),
    ("rm-rf-src", bash("rm -rf src")),
    ("rm-rf-dot", bash("rm -rf .")),
    ("mv-dir-with-adr", bash("mv company/decisions /tmp/decisions")),
    ("git-reset-in-subshell", bash("echo $(git reset --hard)")),
    # fail closed: unparseable + mentions protected path
    ("parse-fail-protected", bash(f"echo 'unterminated >> {C}")),
]

MUST_ALLOW = [
    ("commit-msg-mentions-reset", bash("git commit -m \"docs: never run git reset --hard or git push --force\"")),
    ("commit-msg-mentions-write", bash(f"git commit -m 'hook: block echo x >> {C}; rm -rf src'")),
    ("commit-heredoc-body", bash("git commit -F - <<'EOF'\nfix: git reset --hard and git clean -fd are blocked\n"
                                 f"echo x >> {C}\nEOF")),
    ("brief-heredoc-body", bash("cat > company/handoffs/H-9999-brief.md <<'EOF'\n# Brief\n"
                                f"Today `echo x >> {C}` gets through; git push --force too.\nrm -rf src\n"
                                "cat quarantine/samples.zip\nEOF")),
    ("brief-heredoc-dash", bash("cat > company/handoffs/x.md <<-EOF\n\tgit reset --hard\n\tEOF\necho done")),
    ("ls-quarantine", bash("ls quarantine/")),
    ("ls-la-quarantine", bash("ls -la quarantine")),
    ("cat-normal-file", bash("cat README.md")),
    ("read-constitution", bash(f"cat {C}")),
    ("grep-constitution", bash(f"grep -n 'I-6' {C} | head -5")),
    ("git-status", bash("git status")),
    ("git-add-locked-exp", bash(f"git add {EXP} company/experiments/EXP-002.md")),
    ("git-status-quarantine", bash("git status --short quarantine/")),
    ("append-unlocked-exp", bash(f"echo x >> {EXP_U}")),
    ("sed-i-proposed-adr", bash(f"sed -i 's/a/b/' {ADR_P}")),
    ("cp-constitution-out", bash(f"cp {C} /tmp/constitution-copy.md")),
    ("append-access-log", bash("echo entry >> data/heldout/ACCESS_LOG.md")),
    ("python-read-constitution", bash(f"python3 -c \"print(open('{C}').read())\"")),
    ("echo-mentions-commands", bash("echo \"git push --force is blocked; rm -rf src too\"")),
    ("grep-for-command-text", bash("grep -rn 'git reset --hard' company/ | head")),
    ("pytest-2>&1", bash("python3 -m pytest -q 2>&1 | tail -5")),
    ("rm-rf-scratch", bash("rm -rf out/tmp /tmp/scratch")),
    ("comment-mentions-reset", bash("ls  # then git reset --hard")),
    ("parse-fail-no-protected", bash("echo 'unterminated")),
    ("edit-src", tool("Edit", "src/a.py")),
    ("edit-handoff", tool("Write", "company/handoffs/H-9999-return.md")),
    ("malformed-json", "{not json"),
    ("non-dict-tool-input", {"tool_name": "Bash", "tool_input": "oops"}),
]


@pytest.mark.parametrize("name,payload", MUST_BLOCK, ids=[c[0] for c in MUST_BLOCK])
def test_must_block(project, name, payload):
    r = run(project, payload)
    assert r.returncode == 2, f"{name}: expected block, got exit {r.returncode} {r.stderr!r}"
    assert "BLOCKED by company policy" in r.stderr


@pytest.mark.parametrize("name,payload", MUST_ALLOW, ids=[c[0] for c in MUST_ALLOW])
def test_must_allow(project, name, payload):
    r = run(project, payload)
    assert r.returncode == 0, f"{name}: expected allow, got exit {r.returncode} {r.stderr!r}"


def test_case_counts():
    assert len(MUST_BLOCK) >= 15 and len(MUST_ALLOW) >= 10


def test_hook_never_touches_files(project):
    before = {p: p.read_bytes() for p in project.rglob("*") if p.is_file()}
    for _, payload in MUST_BLOCK + MUST_ALLOW:
        run(project, payload)
    after = {p: p.read_bytes() for p in project.rglob("*") if p.is_file()}
    assert before == after
