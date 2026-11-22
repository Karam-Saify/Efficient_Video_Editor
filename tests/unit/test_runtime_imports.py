"""H-0009 (H-0003 review F2): the full runtime lock imports. Runs only where requirements.txt is installed
(CI `runtime` job and the local .venv set VAC_FULL_RUNTIME=1); elsewhere it is skipped, not passed."""
from __future__ import annotations

import importlib
import os

import pytest

pytestmark = pytest.mark.skipif(os.environ.get("VAC_FULL_RUNTIME") != "1", reason="full runtime lock not installed")


@pytest.mark.parametrize("mod", ["pulp", "numpy", "av", "faster_whisper", "scenedetect", "cv2", "jsonschema"])
def test_runtime_module_imports(mod: str) -> None:
    importlib.import_module(mod)


def test_pulp_solves_a_tiny_milp() -> None:
    import pulp

    p = pulp.LpProblem("t", pulp.LpMaximize)
    x = p.add_variable("x", 0, 3, cat="Integer")  # PuLP 4 API; needs apt coinor-cbc (PuLP 4 bundles no CBC)
    p += x
    stats = p.solve(pulp.COIN_CMD(msg=False))
    assert stats.status_str == "Optimal" and x.value() == 3
