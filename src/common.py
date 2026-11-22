"""Shared helpers: paths, cache layout, media probing."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "cache"
SCHEMA_PATH = ROOT / "schemas" / "timeline.schema.json"


def video_id(path: Path) -> str:
    """Stable id from file size + first/last 4 MB. Cheap even for large files."""
    h = hashlib.sha1()
    size = path.stat().st_size
    h.update(str(size).encode())
    with path.open("rb") as f:
        h.update(f.read(4 << 20))
        if size > 8 << 20:
            f.seek(-(4 << 20), 2)
            h.update(f.read())
    return f"{path.stem[:24]}-{h.hexdigest()[:10]}"


def cache_dir(vid: str) -> Path:
    d = CACHE / vid
    d.mkdir(parents=True, exist_ok=True)
    return d


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def probe(path: Path) -> dict[str, Any]:
    """Duration, size, fps and audio presence via ffprobe."""
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(path)],
        check=True, capture_output=True, text=True,
    ).stdout
    info = json.loads(out)
    v = next((s for s in info["streams"] if s["codec_type"] == "video"), None)
    meta: dict[str, Any] = {
        "path": str(path),
        "duration": float(info["format"]["duration"]),
        "has_audio": any(s["codec_type"] == "audio" for s in info["streams"]),
    }
    if v:
        num, den = (int(x) for x in v.get("avg_frame_rate", "0/1").split("/"))
        meta.update(width=int(v["width"]), height=int(v["height"]), fps=round(num / den, 3) if den else 0)
    return meta
