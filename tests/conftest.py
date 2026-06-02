from __future__ import annotations

import re
import shutil
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRATCH_ROOT = ROOT / ".test-tmp"


@pytest.fixture
def tmp_path(request: pytest.FixtureRequest) -> Path:
    """Windows-safe replacement for pytest's tmp_path in locked temp setups."""
    SCRATCH_ROOT.mkdir(exist_ok=True)
    safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", request.node.name)
    path = SCRATCH_ROOT / safe_name
    if path.exists():
        shutil.rmtree(path, ignore_errors=True)
    path.mkdir()
    yield path
    shutil.rmtree(path, ignore_errors=True)
