from pathlib import Path
from shutil import copytree

from openevalgate.eval_results import validate_eval_results
from openevalgate.validator import check_project


ROOT = Path(__file__).resolve().parents[1]
CUSTOMER_SUPPORT = ROOT / "examples" / "customer_support_assistant"


def test_valid_eval_results_pass() -> None:
    result = validate_eval_results(CUSTOMER_SUPPORT)

    assert result.valid
    assert result.row_count == 3


def test_invalid_eval_results_fail(tmp_path: Path) -> None:
    project = tmp_path / "project"
    copytree(CUSTOMER_SUPPORT, project)
    (project / "eval_results.csv").write_text(
        "\n".join(
            [
                "run_id,case_id,candidate,evaluator,actual_route,expected_route,route_match,passed,score,failure_category,failure_reason,observed_output_path,reviewed_by,reviewed_at,notes",
                "run_001,refund_boundary_case_001,gpt-4.1-mini,human_review,send,escalate,maybe,true,1.4,,,,ai_quality,2026-05-23,bad row",
            ]
        ),
        encoding="utf-8",
    )

    result = validate_eval_results(project)

    assert not result.valid
    assert any("actual_route" in issue.path for issue in result.issues)
    assert any("route_match" in issue.path for issue in result.issues)
    assert any("score" in issue.path for issue in result.issues)


def test_unknown_case_id_in_results_fails_project_check(tmp_path: Path) -> None:
    project = tmp_path / "project"
    copytree(CUSTOMER_SUPPORT, project)
    text = (project / "eval_results.csv").read_text(encoding="utf-8")
    text = text.replace("refund_boundary_case_001", "unknown_case_999", 1)
    (project / "eval_results.csv").write_text(text, encoding="utf-8")

    result = check_project(project)

    assert not result.valid
    assert any("Unknown eval case id" in issue.message for issue in result.issues)
