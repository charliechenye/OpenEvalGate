from pathlib import Path
from shutil import copytree

from openevalgate.validator import check_project


ROOT = Path(__file__).resolve().parents[1]
CUSTOMER_SUPPORT = ROOT / "examples" / "customer_support_assistant"


def test_complete_example_project_passes() -> None:
    result = check_project(CUSTOMER_SUPPORT)

    assert result.valid
    assert result.missing_required == []
    assert "model_arena_scorecard.csv" in result.present_optional
    assert "action_risk_matrix.csv" in result.present_optional


def test_missing_required_launch_file_fails(tmp_path: Path) -> None:
    project = tmp_path / "project"
    copytree(CUSTOMER_SUPPORT, project)
    (project / "launch_gate_review.md").unlink()

    result = check_project(project)

    assert not result.valid
    assert "launch_gate_review.md" in result.missing_required


def test_optional_files_do_not_fail_project_check(tmp_path: Path) -> None:
    project = tmp_path / "project"
    copytree(CUSTOMER_SUPPORT, project)
    (project / "model_arena_scorecard.csv").unlink()
    (project / "action_risk_matrix.csv").unlink()

    result = check_project(project)

    assert result.valid
    assert result.present_optional == []
