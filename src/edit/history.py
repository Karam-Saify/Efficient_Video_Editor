"""Version store for edit sessions (H-0025 G4): `cache/<video_id>/edit/history/v<N>.json`, one timeline per file.

`save(tl)` writes the next version N (v0 is the first); `undo()` deletes the head vN and returns vN-1, which is
then the head again. Files are written with sorted keys so the same edit gives byte-identical history files.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from src.edit.ops import OpError

_NAME = re.compile(r"^v(\d+)\.json$")


class History:
    def __init__(self, root: Path) -> None:
        self.root = root

    def versions(self) -> list[int]:
        if not self.root.is_dir():
            return []
        return sorted(int(m.group(1)) for p in self.root.iterdir() if (m := _NAME.match(p.name)))

    def path(self, n: int) -> Path:
        return self.root / f"v{n}.json"

    def save(self, tl: dict[str, Any]) -> int:
        vs = self.versions()
        n = vs[-1] + 1 if vs else 0
        self.root.mkdir(parents=True, exist_ok=True)
        self.path(n).write_text(json.dumps(tl, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return n

    def load(self, n: int) -> dict[str, Any]:
        return json.loads(self.path(n).read_text(encoding="utf-8"))

    def head(self) -> tuple[int, dict[str, Any]]:
        vs = self.versions()
        if not vs:
            raise OpError("E_OP_UNDO", f"no versions in {self.root}")
        return vs[-1], self.load(vs[-1])

    def undo(self) -> dict[str, Any]:
        vs = self.versions()
        if len(vs) < 2:
            raise OpError("E_OP_UNDO", "nothing to undo (only v0 or no version)")
        self.path(vs[-1]).unlink()
        return self.load(vs[-2])

    def clear(self) -> None:
        for n in self.versions():
            self.path(n).unlink()
