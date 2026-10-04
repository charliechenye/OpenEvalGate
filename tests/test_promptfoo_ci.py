from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from scripts import export_promptfoo_v1 as producer
from scripts import run_promptfoo_demo as demo

HELPER = demo.ROOT / "scripts/review_evidence_ci.sh"


def _review(project: Path, artifacts: Path, *statuses: str) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["PATH"] = str(Path(sys.executable).parent) + os.pathsep + environment["PATH"]
    environment["GITHUB_STEP_SUMMARY"] = str(artifacts.parent / "summary.md")
    return subprocess.run(
        ["bash", str(HELPER), str(project), str(artifacts), *statuses],
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.parametrize("blocked", [False, True])
def test_ci_propagates_blocked_report_through_tee_and_keeps_diagnostics(
    tmp_path: Path, blocked: bool
) -> None:
    project = tmp_path / "review"
    demo.prepare_project(project, blocked=blocked)
    assert producer.main(demo.export_command(project)[2:]) == 0
    artifacts = tmp_path / "artifacts"
    result = _review(project, artifacts)
    assert result.returncode == int(blocked)
    report = json.loads((artifacts / "report.json").read_text())
    assert report["status"] == ("blocked" if blocked else "pass")
    assert f"card_exit={int(blocked)}" in (artifacts / "review-status.txt").read_text()
    assert "tee_exit=0" in (artifacts / "review-status.txt").read_text()
    assert (
        (tmp_path / "summary.md").read_text().endswith((artifacts / "decision-card.md").read_text())
    )


def test_ci_retains_invalid_evidence_diagnostics(tmp_path: Path) -> None:
    project = tmp_path / "review"
    demo.prepare_project(project)
    assert producer.main(demo.export_command(project)[2:]) == 0
    with (project / "eval_results.csv").open("a") as stream:
        stream.write("invalid,row\n")
    artifacts = tmp_path / "artifacts"
    assert _review(project, artifacts).returncode == 1
    assert json.loads((artifacts / "check.json").read_text())["status"] == "invalid"
    assert json.loads((artifacts / "report.json").read_text())["status"] == "blocked"


@pytest.mark.parametrize("statuses", [("100", "0"), ("0", "1"), ("1", "1")])
def test_ci_never_accepts_upstream_or_export_failure(
    tmp_path: Path, statuses: tuple[str, str]
) -> None:
    artifacts = tmp_path / "artifacts"
    artifacts.mkdir()
    (artifacts / "eval.log").write_text("synthetic upstream diagnostic\n")
    assert _review(tmp_path / "absent", artifacts, *statuses).returncode == 1
    assert not (artifacts / "report.json").exists()
    assert "skipped_due_to_upstream_failure" in (artifacts / "review-status.txt").read_text()
    assert (artifacts / "eval.log").read_text() == "synthetic upstream diagnostic\n"


@pytest.mark.parametrize("value", ["", "-1", "256", "01", "bad"])
def test_ci_rejects_invalid_upstream_exit_code(tmp_path: Path, value: str) -> None:
    assert _review(tmp_path / "absent", tmp_path / "artifacts", value).returncode == 2


def test_ci_fails_when_tee_cannot_save_card(tmp_path: Path) -> None:
    project = tmp_path / "review"
    demo.prepare_project(project)
    assert producer.main(demo.export_command(project)[2:]) == 0
    artifacts = tmp_path / "artifacts"
    artifacts.mkdir()
    (artifacts / "decision-card.md").mkdir()
    assert _review(project, artifacts).returncode == 1
    status = (artifacts / "review-status.txt").read_text()
    assert "card_exit=0" in status
    assert "tee_exit=1" in status
