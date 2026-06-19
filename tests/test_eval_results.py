import csv
from pathlib import Path
from shutil import copytree

import yaml

from openevalgate.eval_results import summarize_eval_results, validate_eval_results
from openevalgate.report import generate_report
from openevalgate.validator import check_project


ROOT = Path(__file__).resolve().parents[1]
CUSTOMER_SUPPORT = ROOT / "examples" / "customer_support_assistant"


def test_valid_eval_results_pass() -> None:
    result = validate_eval_results(CUSTOMER_SUPPORT)

    assert result.valid
    assert result.row_count == 6


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


def test_enriched_eval_results_validate_and_calculate_boundary_metrics(tmp_path: Path) -> None:
    project = tmp_path / "project"
    copytree(CUSTOMER_SUPPORT, project)
    cases = yaml.safe_load((project / "eval_cases.yaml").read_text(encoding="utf-8"))["eval_cases"]
    anchor = cases[0]
    variant = cases[1]
    anchor["boundary"] = {
        "family_id": "refund_family",
        "anchor_case_id": anchor["id"],
        "controlling_fact": "wording",
        "variation_type": "anchor",
        "before_value": "base",
        "after_value": "base",
    }
    variant["boundary"] = {
        "family_id": "refund_family",
        "anchor_case_id": anchor["id"],
        "controlling_fact": "wording",
        "variation_type": "semantic_invariance",
        "before_value": "base",
        "after_value": "paraphrase",
    }
    (project / "eval_cases.yaml").write_text(
        yaml.safe_dump({"eval_cases": [anchor, variant]}, sort_keys=False),
        encoding="utf-8",
    )

    headers = [
        "run_id", "case_id", "candidate", "evaluator", "actual_route", "expected_route",
        "route_match", "passed", "score", "failure_category", "failure_reason",
        "observed_output_path", "reviewed_by", "reviewed_at", "notes", "trial_id",
        "actual_workflow_route", "workflow_route_match", "trajectory_pass",
        "end_state_pass", "prohibited_action_occurred",
    ]
    rows = [
        ["run_002", anchor["id"], "candidate", "harness", "escalate", "escalate", "true", "true", "1", "", "", "", "qa", "2026-06-18", "", "trial_1", "act", "true", "true", "true", "false"],
        ["run_002", variant["id"], "candidate", "harness", "escalate", "escalate", "true", "true", "1", "", "", "", "qa", "2026-06-18", "", "trial_1", "act", "true", "true", "true", "false"],
        ["run_002", anchor["id"], "candidate", "harness", "escalate", "escalate", "true", "true", "1", "", "", "", "qa", "2026-06-18", "", "trial_2", "act", "true", "true", "true", "false"],
        ["run_002", variant["id"], "candidate", "harness", "show", "escalate", "false", "false", "0", "route", "unstable", "", "qa", "2026-06-18", "", "trial_2", "answer", "false", "false", "false", "true"],
    ]
    with (project / "eval_results.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)
        writer.writerows(rows)

    validation = validate_eval_results(project)
    summary = summarize_eval_results(project)

    assert validation.valid
    assert summary is not None
    assert summary.workflow_route_accuracy == 0.75
    assert summary.prohibited_action_rate == 0.25
    assert summary.boundary_family_count == 1
    assert summary.complete_boundary_family_count == 1
    assert summary.contrast_family_reliability == 0.0
    assert summary.semantic_stability == 0.5
    assert summary.repeated_case_count == 2
    assert summary.repeated_run_reliability == 0.5
    report = generate_report(project)
    assert "Workflow-route accuracy: 75%" in report
    assert "Prohibited-action rate: 25%" in report
    assert "Contrast-family reliability: 0%" in report
    assert "Semantic stability: 50%" in report
    assert "Repeated-run reliability: 50%" in report


def test_escalation_metrics_are_calculated_from_enriched_results() -> None:
    summary = summarize_eval_results(CUSTOMER_SUPPORT)

    assert summary is not None
    assert summary.required_escalation_recall == 2 / 3
    assert summary.over_escalation_rate == 2 / 3
    assert summary.destination_accuracy == 1 / 3
    assert summary.context_preservation_rate == 2 / 3
    assert summary.fallback_success_rate == 1.0
    assert summary.resume_success_rate == 1 / 3
    assert summary.late_escalation_rate == 1 / 3


def test_invalid_enriched_result_values_fail(tmp_path: Path) -> None:
    project = tmp_path / "project"
    copytree(CUSTOMER_SUPPORT, project)
    path = project / "eval_results.csv"
    path.write_text(
        "\n".join(
            [
                "run_id,case_id,candidate,evaluator,actual_route,expected_route,route_match,passed,score,failure_category,failure_reason,observed_output_path,reviewed_by,reviewed_at,notes,trial_id,actual_workflow_route,workflow_route_match,trajectory_pass,end_state_pass,prohibited_action_occurred,destination_match,payload_complete",
                "run_1,refund_boundary_case_001,candidate,harness,escalate,escalate,true,true,1,,,,qa,2026-06-18,,trial_1,execute,maybe,true,true,false,maybe,nope",
            ]
        ),
        encoding="utf-8",
    )

    result = validate_eval_results(project)

    assert not result.valid
    assert any("actual_workflow_route" in issue.path for issue in result.issues)
    assert any("workflow_route_match" in issue.path for issue in result.issues)
    assert any("destination_match" in issue.path for issue in result.issues)
    assert any("payload_complete" in issue.path for issue in result.issues)
