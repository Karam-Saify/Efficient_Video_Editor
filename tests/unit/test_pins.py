"""pyproject.toml is the source of truth; lock files must carry the same exact pins."""
from __future__ import annotations

import re
import tomllib
from pathlib import Path

import src

ROOT = Path(__file__).resolve().parents[2]
PY = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))


def _norm(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def _pins(lines: list[str]) -> dict[str, str]:
    out = {}
    for line in lines:
        line = line.split("#", 1)[0].strip()
        if line:
            name, sep, ver = line.partition("==")
            assert sep, f"not an exact pin: {line!r}"
            out[_norm(name)] = ver.strip()
    return out


def _lock(name: str) -> dict[str, str]:
    return _pins((ROOT / name).read_text(encoding="utf-8").splitlines())


def test_all_direct_deps_are_exact_pins() -> None:
    proj = PY["project"]
    groups = [proj["dependencies"], *proj["optional-dependencies"].values()]
    for g in groups:
        _pins(g)  # asserts '==' on each


def test_runtime_lock_matches_pyproject() -> None:
    extras = PY["project"]["optional-dependencies"]
    want = _pins(PY["project"]["dependencies"] + extras["milp"] + extras["media"])
    lock = _lock("requirements.txt")
    assert {k: lock.get(k) for k in want} == want


def test_dev_lock_matches_pyproject() -> None:
    want = _pins(PY["project"]["dependencies"] + PY["project"]["optional-dependencies"]["dev"])
    lock = _lock("requirements-dev.txt")
    assert {k: lock.get(k) for k in want} == want


def test_code_version_matches_pyproject() -> None:
    assert src.__version__ == PY["project"]["version"]


# H-0009 / ADR-0002: Python floor is 3.12 everywhere it is declared.
def test_python_floor_is_3_12() -> None:
    assert PY["project"]["requires-python"] == ">=3.12"
    assert PY["tool"]["ruff"]["target-version"] == "py312"
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert '"3.12"' in ci and '"3.14"' in ci and '"3.11"' not in ci


# H-0009 (H-0003 review F4): exactly one distribution provides cv2.
def test_one_opencv_distribution_in_runtime_lock() -> None:
    assert [k for k in _lock("requirements.txt") if k.startswith("opencv")] == ["opencv-python"]
