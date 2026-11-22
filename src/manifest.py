"""Stage cache contract: hash inputs + config, write `<out>/manifest.json`, skip on identical rerun.

Every stage CLI (`python -m src.<stage> --input <path> --out <dir>`) goes through `run_stage`.

Skip rule: a rerun is skipped (exit 0, no work) iff `<out>/manifest.json` exists, was written by the
same stage, has identical `input_hashes` and `config_hash`, and every recorded output file still has
its recorded sha256. `config` always contains the stage's `stage_version`, so bumping it forces a rerun.
`versions.python` / `versions.tools` are recorded for provenance but are not part of the skip key.

The manifest is written last and atomically; a stale manifest is deleted before work starts, so a
crash mid-stage can never leave a manifest that claims outputs it did not produce.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
from collections.abc import Callable, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from src import __version__
from src.common import ROOT

MANIFEST = "manifest.json"
_CHUNK = 1 << 20

# work(inputs, out_dir, config) -> status string recorded in the manifest ("ok", "stub", ...)
Work = Callable[[list[Path], Path, dict[str, Any]], str]


class StageError(RuntimeError):
    """A stage failed in a way the user must see; no manifest is written."""


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(_CHUNK):
            h.update(chunk)
    return h.hexdigest()


def _key(path: Path) -> str:
    """Repo-relative POSIX path when inside the repo, else absolute (stable across checkouts)."""
    p = path.resolve()
    try:
        return p.relative_to(ROOT).as_posix()
    except ValueError:
        return p.as_posix()


def hash_inputs(paths: Sequence[Path]) -> dict[str, str]:
    """sha256 per input file; a directory contributes every file under it."""
    out: dict[str, str] = {}
    for p in paths:
        if not p.exists():
            raise StageError(f"input not found: {p}")
        files = sorted(f for f in p.rglob("*") if f.is_file()) if p.is_dir() else [p]
        for f in files:
            out[_key(f)] = sha256_file(f)
    return dict(sorted(out.items()))


def config_hash(config: dict[str, Any]) -> str:
    canon = json.dumps(config, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()


def hash_outputs(out_dir: Path) -> dict[str, str]:
    return {
        f.relative_to(out_dir).as_posix(): sha256_file(f)
        for f in sorted(out_dir.rglob("*"))
        if f.is_file() and f.name != MANIFEST and not f.name.endswith(".tmp")
    }


def tool_version(cmd: str) -> str | None:
    """First line of `<cmd> -version`, or None if the tool is absent."""
    try:
        r = subprocess.run([cmd, "-version"], capture_output=True, text=True, check=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout.splitlines()[0].strip() if r.stdout else None


def versions(tools: Sequence[str] = ()) -> dict[str, Any]:
    return {
        "code": __version__,
        "python": platform.python_version(),
        "tools": {t: tool_version(t) for t in tools},
    }


def read_manifest(out_dir: Path) -> dict[str, Any] | None:
    p = out_dir / MANIFEST
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def is_fresh(out_dir: Path, stage: str, input_hashes: dict[str, str], cfg_hash: str) -> bool:
    m = read_manifest(out_dir)
    if not m or m.get("stage") != stage:
        return False
    if m.get("input_hashes") != input_hashes or m.get("config_hash") != cfg_hash:
        return False
    for rel, digest in (m.get("outputs") or {}).items():
        f = out_dir / rel
        if not f.is_file() or sha256_file(f) != digest:
            return False
    return True


def _write_atomic(path: Path, data: dict[str, Any]) -> None:
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def run_stage(
    stage: str,
    inputs: Sequence[Path],
    out_dir: Path,
    config: dict[str, Any],
    work: Work,
    tools: Sequence[str] = (),
) -> tuple[bool, dict[str, Any]]:
    """Run `work` unless a fresh manifest exists. Returns (ran, manifest)."""
    ins = hash_inputs(inputs)
    ch = config_hash(config)
    out_dir.mkdir(parents=True, exist_ok=True)
    if is_fresh(out_dir, stage, ins, ch):
        return False, read_manifest(out_dir) or {}
    (out_dir / MANIFEST).unlink(missing_ok=True)
    t0 = time.perf_counter()
    status = work([Path(p) for p in inputs], out_dir, config)
    manifest = {
        "stage": stage,
        "status": status,
        "created_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "duration_s": round(time.perf_counter() - t0, 3),
        "input_hashes": ins,
        "config": config,
        "config_hash": ch,
        "versions": versions(tools),
        "outputs": hash_outputs(out_dir),
    }
    _write_atomic(out_dir / MANIFEST, manifest)
    return True, manifest


def stub_work(inputs: list[Path], out_dir: Path, config: dict[str, Any]) -> str:
    """Placeholder for stages without logic yet: produces no outputs, manifest says status=stub."""
    return "stub"


def _parse_value(raw: str) -> Any:
    try:
        return json.loads(raw)
    except ValueError:
        return raw


def build_config(stage_version: str, defaults: dict[str, Any], sets: Sequence[str]) -> dict[str, Any]:
    cfg = dict(defaults)
    for kv in sets:
        k, sep, v = kv.partition("=")
        if not sep or not k:
            raise StageError(f"--set expects key=value, got {kv!r}")
        if k not in defaults:
            raise StageError(f"unknown config key {k!r} (known: {', '.join(sorted(defaults)) or 'none'})")
        cfg[k] = _parse_value(v)
    cfg["stage_version"] = stage_version
    return cfg


def cli(
    stage: str,
    argv: Sequence[str] | None = None,
    *,
    defaults: dict[str, Any] | None = None,
    work: Work = stub_work,
    stage_version: str = "0",
    tools: Sequence[str] = (),
) -> int:
    """Common CLI: `--input <path> [--input ...] --out <dir> [--set key=value ...]`. Returns exit code."""
    ap = argparse.ArgumentParser(prog=f"python -m src.{stage}", description=f"{stage} stage (cached)")
    ap.add_argument("--input", type=Path, action="append", required=True, help="input file or dir (repeatable)")
    ap.add_argument("--out", type=Path, required=True, help="output dir; manifest.json is written here")
    ap.add_argument("--set", action="append", default=[], metavar="KEY=VALUE", help="override a config key")
    a = ap.parse_args(argv)
    try:
        cfg = build_config(stage_version, defaults or {}, a.set)
        ran, m = run_stage(stage, a.input, a.out, cfg, work, tools)
    except StageError as e:
        print(f"{stage}: error: {e}", file=sys.stderr)
        return 1
    if ran:
        print(f"{stage}: done ({m['status']}) in {m['duration_s']}s -> {a.out / MANIFEST}")
    else:
        print(f"{stage}: skip (inputs and config unchanged; {a.out / MANIFEST})")
    return 0


def wants_stage_cli(argv: Sequence[str]) -> bool:
    """True when the new `--input/--out` interface is used (legacy positional CLIs stay intact)."""
    return any(x == "--input" or x.startswith("--input=") for x in argv)
