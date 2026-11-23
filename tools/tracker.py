"""Tracker: company/state/TRACKER.md is the single source of truth for work items.

    python tools/tracker.py           regenerate the stats block in TRACKER.md
    python tools/tracker.py --check   exit 1 if the tracker is invalid or the stats block is stale

Rules enforced by --check:
  * every row has an ID, a Status from STATUSES, and an Owner;
  * IDs are unique;
  * a Done row must have evidence (not empty, not "-"/"—"); a Done row without evidence fails;
  * every `backticked/path` in an Evidence cell that looks like a repo path must exist
    (git-ignored locations such as out/, cache/, quarantine/ are allowed to be absent);
  * the stats block matches what the rows say (run without --check to regenerate).
Stdlib only, so CI can run it before installing anything.
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRACKER = ROOT / "company" / "state" / "TRACKER.md"
STATUSES = ("Todo", "Doing", "Blocked", "Done", "Dropped")
HEADER = ["ID", "Item", "Owner", "Status", "Evidence", "Updated"]
STATS_START, STATS_END = "<!-- stats:start -->", "<!-- stats:end -->"
EMPTY = {"", "-", "—", "–", "n/a", "tbd"}
IGNORED_ROOTS = ("out/", "cache/", "quarantine/", "data/golden/", "data/heldout/")
PATH_RE = re.compile(r"`([^`\s]+)`")


def parse_rows(text: str) -> tuple[list[dict[str, str]], list[str]]:
    """Return (rows, errors). Rows come from every markdown table whose header is HEADER."""
    rows, errors = [], []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        cells = _cells(lines[i])
        if cells == HEADER:
            i += 2  # skip header + separator
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                c = _cells(lines[i])
                if len(c) != len(HEADER):
                    errors.append(f"line {i + 1}: expected {len(HEADER)} cells, got {len(c)}")
                else:
                    rows.append({**dict(zip(HEADER, c, strict=True)), "_line": str(i + 1)})
                i += 1
            continue
        i += 1
    return rows, errors


def _cells(line: str) -> list[str]:
    s = line.strip()
    if not (s.startswith("|") and s.endswith("|")):
        return []
    return [c.strip() for c in s[1:-1].split("|")]


def _looks_like_path(tok: str) -> bool:
    return "/" in tok and not tok.startswith(("http", "-")) and " " not in tok and not tok.startswith("python")


def check_rows(rows: list[dict[str, str]], root: Path = ROOT) -> list[str]:
    errors, seen = [], set()
    for r in rows:
        where = f"line {r['_line']} ({r['ID'] or '?'})"
        if not r["ID"]:
            errors.append(f"{where}: missing ID")
        elif r["ID"] in seen:
            errors.append(f"{where}: duplicate ID")
        seen.add(r["ID"])
        if r["Status"] not in STATUSES:
            errors.append(f"{where}: status {r['Status']!r} not in {STATUSES}")
        if not r["Owner"]:
            errors.append(f"{where}: missing Owner")
        ev = r["Evidence"]
        if r["Status"] == "Done" and ev.strip().lower() in EMPTY:
            errors.append(f"{where}: Done without evidence")
        for tok in PATH_RE.findall(ev):
            tok = tok.rstrip(".,;:")
            if not _looks_like_path(tok) or tok.startswith(IGNORED_ROOTS):
                continue
            p = tok.split("#")[0].split(":")[0]
            if "*" in p or "<" in p:
                continue
            if not (root / p).exists():
                errors.append(f"{where}: evidence path does not exist: {p}")
    return errors


def stats_block(rows: list[dict[str, str]]) -> str:
    c = Counter(r["Status"] for r in rows)
    total = len(rows)
    done = c.get("Done", 0)
    pct = round(100 * done / total) if total else 0
    parts = " · ".join(f"{s} {c.get(s, 0)}" for s in STATUSES)
    owners = Counter(r["Owner"] for r in rows if r["Status"] in ("Todo", "Doing", "Blocked"))
    open_by = ", ".join(f"{o} {n}" for o, n in sorted(owners.items())) or "none"
    return (f"{STATS_START}\n**{total} items · {done} done ({pct} %)** · {parts}  \n"
            f"Open by owner: {open_by}\n{STATS_END}")


def render(text: str, rows: list[dict[str, str]]) -> str:
    block = stats_block(rows)
    if STATS_START in text and STATS_END in text:
        pre, rest = text.split(STATS_START, 1)
        _, post = rest.split(STATS_END, 1)
        return pre + block + post
    return block + "\n\n" + text


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="validate only; exit 1 on any problem")
    ap.add_argument("--file", type=Path, default=TRACKER)
    a = ap.parse_args(argv)
    text = a.file.read_text(encoding="utf-8")
    rows, errors = parse_rows(text)
    if not rows:
        errors.append("no tracker rows found (table header must be: | " + " | ".join(HEADER) + " |)")
    errors += check_rows(rows)
    new = render(text, rows)
    if a.check:
        if new != text:
            errors.append("stats block is stale: run `python tools/tracker.py`")
        for e in errors:
            print(f"TRACKER: {e}", file=sys.stderr)
        print(f"tracker: {len(rows)} rows, {len(errors)} problem(s)")
        return 1 if errors else 0
    for e in errors:
        print(f"TRACKER: {e}", file=sys.stderr)
    if new != text:
        a.file.write_text(new, encoding="utf-8")
    print(stats_block(rows).splitlines()[1])
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
