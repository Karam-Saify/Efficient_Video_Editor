"""H-0017 (H-0009 review N1): hostile `sources[].path` strings give a coded issue, never an exception.

Separate module so that, against the parent code, these tests fail by assertion/exception, not by an
ImportError at collection (H-0009 review N5).
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from tests.unit.test_validate import ROOT, base, codes

# Strings that `os`/`pathlib` refuse (ValueError: embedded null byte, UnicodeEncodeError for a lone
# surrogate) or that are control characters. All are representable in JSON, so an LLM or JSON tool can emit them.
MUST_REJECT = [
    "a\x00b",
    "\x00",
    "samples/clip.mp4\x00",
    "samples/\x00/x.mp4",
    "a\x01b",
    "a\nb.mp4",
    "a\rb.mp4",
    "a\tb.mp4",
    "a\x1fb",
    "a\x7fb",
    "a\ud800b",  # lone surrogate: not encodable with the filesystem encoding
    "\udfff",
]

# Odd but encodable strings: any coded outcome is fine, an exception is not.
ODD_BUT_ENCODABLE = [
    " ",
    ".",
    "..",
    "./",
    "~",
    "~/x.mp4",
    "a" * 5000,  # a single component longer than NAME_MAX
    "a/" * 3000,  # a path longer than PATH_MAX
    "samples/\u202eclip.mp4",  # RTL override
    "samples/مقطع.mp4",
    "samples/\u00a0.mp4",
    "\\\\server\\share\\x.mp4",
    "C:\\x.mp4",
    "file:///etc/passwd",
    "samples/clip.mp4/",
    "samples/clip.mp4/..",
]

KNOWN = {"E_SOURCE_PATH", "E_SOURCE_MISSING", "E_SOURCE_HASH", "E_RANGE", "E_OVERLAP", "E_DURATION",
         "E_CAPTION_BOUNDS", "E_SCHEMA"}


def _with_path(p: str) -> dict:
    tl = base()
    tl["sources"][0]["path"] = p
    return tl


def test_nul_byte_in_source_path_is_a_coded_error_not_a_crash() -> None:
    """Regression for N1: `(base_dir / raw).resolve()` raised ValueError('embedded null byte')."""
    assert codes(_with_path("a\x00b")) == ["E_SOURCE_PATH"]


@pytest.mark.parametrize("raw", MUST_REJECT, ids=repr)
def test_unusable_path_strings_give_e_source_path(raw: str) -> None:
    assert codes(_with_path(raw)) == ["E_SOURCE_PATH"]


@pytest.mark.parametrize("raw", ODD_BUT_ENCODABLE, ids=lambda s: repr(s)[:40])
def test_odd_path_strings_never_raise(raw: str) -> None:
    got = codes(_with_path(raw))
    assert got and set(got) <= KNOWN


def test_cli_nul_path_prints_one_line_and_exits_1(tmp_path: Path) -> None:
    f = tmp_path / "t.json"
    f.write_text(json.dumps(_with_path("a\x00b")), encoding="utf-8")  # json.dumps writes the NUL as \u0000
    r = subprocess.run([sys.executable, "-m", "src.validate", str(f)], cwd=ROOT, capture_output=True, text=True,
                       timeout=60)
    out = r.stdout + r.stderr
    assert r.returncode == 1 and "Traceback" not in out and "E_SOURCE_PATH" in out
