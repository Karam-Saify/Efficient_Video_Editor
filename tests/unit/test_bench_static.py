"""H-0030 bench/ static checks: pinned CDN URLs, URLs documented, no dev media, caption parity with src/presets.

The bench itself runs in a browser (experiments/bench_smoke.mjs); these tests guard the properties that must hold
for every commit without a browser.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from src.presets import CAPTION_PRESETS

BENCH = Path(__file__).resolve().parents[2] / "bench"
CODE = sorted([*BENCH.glob("*.js"), BENCH / "index.html"])
README = (BENCH / "README.md").read_text(encoding="utf-8")
URL_RE = re.compile(r"https?://[^\s\"'`)<>]+")
SEMVER_AT = re.compile(r"@\d+\.\d+\.\d+(-[0-9A-Za-z.\-]+)?/")
SHA40 = re.compile(r"/resolve/[0-9a-f]{40}/")


def _urls() -> list[tuple[str, str]]:
    return [(p.name, u) for p in CODE for u in URL_RE.findall(p.read_text(encoding="utf-8"))]


def test_bench_is_static_files_only():
    allowed = {".html", ".js", ".md"}
    assert BENCH.is_dir()
    assert {p.suffix for p in BENCH.iterdir() if p.is_file()} <= allowed
    assert not [p for p in BENCH.iterdir() if p.is_dir()], "no subfolders (no build output, no bundled media)"


def test_code_has_external_urls():
    hosts = {re.sub(r"^https?://([^/]+)/.*", r"\1", u) for _, u in _urls()}
    assert {"cdn.jsdelivr.net", "huggingface.co"} <= hosts


@pytest.mark.parametrize("name,url", _urls())
def test_every_url_is_pinned(name, url):
    if "cdn.jsdelivr.net/npm/" in url:
        assert SEMVER_AT.search(url), f"{name}: unpinned npm URL {url}"
        assert "@latest" not in url
    elif "huggingface.co/datasets/" in url:
        assert SHA40.search(url), f"{name}: dataset file not pinned to a commit: {url}"
    else:
        pytest.fail(f"{name}: URL from an unexpected host: {url}")


def test_model_revisions_are_commit_hashes():
    libs = (BENCH / "libs.js").read_text(encoding="utf-8")
    revs = re.findall(r'revision: "([^"]*)"', libs)
    assert len(revs) == 2 and all(re.fullmatch(r"[0-9a-f]{40}", r) for r in revs)
    for rev in revs:
        assert rev in README


@pytest.mark.parametrize("name,url", _urls())
def test_every_url_is_in_readme(name, url):
    assert url in README, f"{name}: {url} missing from bench/README.md"


@pytest.mark.parametrize("path", CODE, ids=lambda p: p.name)
def test_no_dev_or_quarantine_media_referenced(path):
    text = path.read_text(encoding="utf-8").lower()
    for bad in ("quarantine", "samples/", "data/", "cache/", "download (", "tiktok", "file://"):
        assert bad not in text, f"{path.name} references {bad!r}"
    # a literal media file name (generated download names like `${id}.mp4` are fine)
    # pinned external URLs (e.g. the public speech sample) are checked by the URL tests instead
    local = URL_RE.sub("", text)
    assert not re.search(r"[\"'/][\w\- ()]+\.(mp4|mov|mkv|wav|mp3)[\"']", local), f"{path.name} names a media file"


def test_caption_geometry_matches_clean_preset():
    src = (BENCH / "export.js").read_text(encoding="utf-8")
    m = re.search(r"const CLEAN = \{ size: (\d+), outline: (\d+), margin_v: (\d+), color: \"(#\w+)\", "
                  r"outline_color: \"(#\w+)\" \}", src)
    assert m, "CLEAN constant not found in bench/export.js"
    clean = CAPTION_PRESETS["clean"]
    assert (int(m[1]), int(m[2]), int(m[3]), m[4], m[5]) == (
        clean["size"], clean["outline"], clean["margin_v"], clean["color"], clean["outline_color"])
    assert "'Noto Sans Arabic', 'Noto Sans'" in src


def test_results_schema_documented():
    for key in ("bench-results/1", "finished_at", "device_memory_gb", "hardware_concurrency", "webgpu_available",
                "backend", "model_load_ms", "rtf", "export_ms", "export_fps", "peak_memory_bytes", "attempts",
                "export_720", "audio_codec"):
        assert key in README, key
