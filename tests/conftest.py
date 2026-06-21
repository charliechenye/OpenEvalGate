from __future__ import annotations

import hashlib
import os
import re
import shutil
from pathlib import Path

import pytest

from openevalgate.report import generate_report


ROOT = Path(__file__).resolve().parents[1]
SCRATCH_ROOT = ROOT / ".test-tmp"
READABLE_NODE_ID_LIMIT = 96


@pytest.hookimpl(trylast=True)
def pytest_configure(config: pytest.Config) -> None:
    """Keep pytest and xdist out of locked Windows temp directories."""

    if config.option.basetemp is not None:
        return
    internal_root = SCRATCH_ROOT / f"pytest-internal-{os.getpid()}"
    if internal_root.exists():
        shutil.rmtree(internal_root, ignore_errors=True)
    internal_root.mkdir(parents=True, exist_ok=True)
    config._tmp_path_factory._basetemp = internal_root.resolve()
    config._openevalgate_internal_root = internal_root


@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session: pytest.Session) -> None:
    internal_root = getattr(
        session.config,
        "_openevalgate_internal_root",
        None,
    )
    if internal_root is not None:
        shutil.rmtree(internal_root, ignore_errors=True)


def _worker_id(config: pytest.Config) -> str:
    worker_input = getattr(config, "workerinput", None)
    if isinstance(worker_input, dict):
        return str(worker_input.get("workerid", "master"))
    return "master"


def _safe_test_directory_name(node_id: str) -> str:
    readable = re.sub(r"[^A-Za-z0-9_.-]+", "_", node_id).strip("._-")
    readable = readable[:READABLE_NODE_ID_LIMIT] or "test"
    digest = hashlib.sha256(node_id.encode("utf-8")).hexdigest()[:12]
    return f"{readable}_{digest}"


@pytest.fixture(scope="session")
def _worker_scratch_root(request: pytest.FixtureRequest) -> Path:
    """Create one isolated scratch root per xdist worker."""

    SCRATCH_ROOT.mkdir(exist_ok=True)
    worker_root = SCRATCH_ROOT / _worker_id(request.config)
    if worker_root.exists():
        shutil.rmtree(worker_root, ignore_errors=True)
    worker_root.mkdir()
    yield worker_root
    shutil.rmtree(worker_root, ignore_errors=True)


@pytest.fixture
def tmp_path(
    request: pytest.FixtureRequest,
    _worker_scratch_root: Path,
) -> Path:
    """Windows-safe replacement for pytest's tmp_path in locked temp setups."""

    path = _worker_scratch_root / _safe_test_directory_name(
        request.node.nodeid
    )
    if path.exists():
        shutil.rmtree(path, ignore_errors=True)
    path.mkdir()
    yield path
    shutil.rmtree(path, ignore_errors=True)


@pytest.fixture(scope="session")
def customer_support_report() -> str:
    return generate_report(ROOT / "examples" / "customer_support_assistant")


@pytest.fixture(scope="session")
def presales_report() -> str:
    return generate_report(ROOT / "examples" / "presales_assistant")


@pytest.fixture(scope="session")
def education_report() -> str:
    return generate_report(ROOT / "examples" / "education_assistant")
