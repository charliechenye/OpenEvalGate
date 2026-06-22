from pathlib import Path
from shutil import copytree

import yaml

from openevalgate.validator import check_project


ROOT = Path(__file__).resolve().parents[1]
CUSTOMER_SUPPORT = ROOT / "examples" / "customer_support_assistant"


def test_complete_example_project_passes() -> None:
    result = check_project(CUSTOMER_SUPPORT)

    assert result.valid
    assert result.missing_required == []
    assert "model_arena_scorecard.csv" in result.present_optional
    assert "eval_results.csv" in result.present_optional
    assert "domain_owner_feedback_loop.md" in result.present_optional
    assert "escalation_contract.yaml" in result.present_optional
    assert "routing_policy.yaml" in result.present_optional


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
    (project / "eval_results.csv").unlink()
    (project / "domain_owner_feedback_loop.md").unlink()
    (project / "agent_behavior_change_request.md").unlink()
    (project / "p0_failure_mode_checklist.md").unlink()
    (project / "tail_risk_eval_cases.yaml").unlink()
    (project / "purpose_built_assistant_scope.md").unlink()
    (project / "escalation_contract.yaml").unlink()
    (project / "routing_policy.yaml").unlink()
    (project / "review_policy.yaml").unlink()

    result = check_project(project)

    assert result.valid
    assert result.present_optional == []


def test_invalid_optional_escalation_contract_fails_project_check(tmp_path: Path) -> None:
    project = tmp_path / "project"
    copytree(CUSTOMER_SUPPORT, project)
    contract_path = project / "escalation_contract.yaml"
    contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
    contract["escalation_contract"]["routing"]["destinations"][0]["fallback"] = ""
    contract_path.write_text(yaml.safe_dump(contract, sort_keys=False), encoding="utf-8")

    result = check_project(project)

    assert not result.valid
    assert any("fallback" in issue.path for issue in result.issues)
