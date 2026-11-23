# BRIEF H-0020 (close hook gaps)
- **To:** engineering-lead · **Tier / Milestone:** T2 / M0 · **Date:** 2026-11-22
1. **Objective (with why):** Make `.claude/hooks/protect.py` block shell writes to protected paths and stop false positives on text. Today `echo x >> company/CONSTITUTION.md` gets through, while a commit message or heredoc that merely *mentions* a destructive git command is blocked. That has happened twice this session, including on a brief file being written.
2. **Inputs:** `.claude/hooks/protect.py`, `.claude/settings.json`, `company/gates/M0/hook-test.txt`, `company/gates/M0/hook_selftest.py`, `company/CONSTITUTION.md` (read only; I-5, I-6, I-7)
3. **Constraints:**
   - **Protected paths:** `company/CONSTITUTION.md`; ADRs whose Status is Accepted; experiments with `**Lock:** LOCKED`; `data/heldout/` (except `ACCESS_LOG.md`); `quarantine/` (new: block writes AND reads or extraction such as `unzip`, `cat`, `cp` from it, per the Founder order "do not open, extract or use"; `ls` stays allowed); `.env`/secret files as today.
   - **Bash: block writes** to protected paths via redirects (`>`, `>>`, `1>`, `&>`), `tee`/`tee -a`, `sed -i`/`perl -i`, `cp`/`mv`/`install`/`ln`/`rsync` destinations, `truncate`, `dd of=`; best-effort for `python -c`/heredoc scripts that name a protected path as a write target (document the limits).
   - **Reduce false positives:** tokenise with `shlex` (fall back to regex if parsing fails) and match destructive commands only in command position (start, or after `&&`, `||`, `;`, `|`). Ignore quoted message arguments (`git commit -m ...`) and heredoc *bodies* (text after `<<'EOF'` up to the terminator). Keep the existing destructive-git blocks.
   - **Fail-open stays** for malformed hook input, but a parse failure on a command that mentions a protected path must fail **closed** (block, with a reason).
   - Tests: `tests/unit/test_protect_hook.py` feeding JSON to the hook via subprocess. At least 15 must-block cases (each protected path class × redirect/tee/sed -i/cp/mv) and at least 10 must-allow cases (commit messages and heredoc bodies that mention the commands, `ls quarantine/`, `cat` of normal files, `git status`, `git add` of a locked EXP, reading the Constitution). Update `company/gates/M0/hook_selftest.py` if it exists.
   - **Careful:** a bug in this hook can block every tool call. Keep the file syntactically valid at all times (write to a temp file, test it, then move it into place). Run the full suite before finishing. Don't touch protected files. No commit.
4. **Output:** updated hook + tests; return `company/handoffs/H-0020-return.md` with the case table, ruff + pytest output, and the known limits (what still can't be caught).
5. **Done when:** [ ] all must-block and must-allow cases pass · [ ] full suite green · [ ] limits documented in the hook docstring · [ ] LOG entry
6. **Out of scope:** settings.json permission changes; new protected classes beyond the list.
7. **Effort budget:** max 40 tool calls · max 2 retries
8. **Escalate if:** blocking a class would also block routine Operator work (reading and `git add` must stay allowed).
9. **Termination condition:** return written; stop.
10. **Consulted positions:** Assurance reviews (T2: `.claude/hooks/` is never fast lane, ADR-0005).
