from collections import Counter
from pathlib import Path
from shutil import copytree

import pytest

from openevalgate.cli import main
from openevalgate.launch_gate_review import is_meaningful_mitigation
from openevalgate.project_inspection import inspect_project
from openevalgate.report import _non_eval_result_issues, generate_report
from openevalgate.schema import ValidationIssue, load_eval_cases
from openevalgate.scorer import WEIGHTS, score_gates, GateRow


ROOT = Path(__file__).resolve().parents[1]
CUSTOMER_SUPPORT = ROOT / "examples" / "customer_support_assistant"


def test_report_generation_returns_expected_sections(
    customer_support_report: str,
) -> None:
    report = customer_support_report

    assert "# Launch Readiness Report: Customer Support Refund Assistant" in report
    assert "## Executive Summary" in report
    assert "## Evidence Completeness Score" in report
    assert "## Observed Behavioral Quality" in report
    assert "## Critical-Control Status" in report
    assert "## Maximum Permitted Stage" in report
    assert "## Hard-Gate Evaluation" in report
    assert "## Hard Blockers" in report
    assert "## Trust Preservation Summary" in report
    assert "## Business Behavior Contract Summary" in report
    assert "## Tail-Risk / P0 Failure Mode Summary" in report
    assert "## Metric Stack Summary" in report
    assert "## Golden Eval Summary" in report
    assert "## Model Arena Summary" in report
    assert "## Routing / Capability Allocation Summary" in report
    assert "Overall Readiness Score" not in report


def test_high_evidence_completeness_can_still_be_not_ready(
    customer_support_report: str,
) -> None:
    report = customer_support_report

    assert "**Evidence completeness score:** 90/100" in report
    assert "**Evidence package band:** Substantially complete" in report
    assert "**Behavioral evidence status:** Evaluated — valid empirical rows are available." in report
    assert "**Critical-control status:** Fail" in report
    assert "**Maximum permitted stage:** Shadow evaluation with remediation" in report
    assert "**Final launch recommendation:** Not ready for controlled launch" in report
    assert "## Evidence Completeness Score\n90/100" in report
    assert "Overall Readiness Score" not in report


def test_scorer_emits_evidence_bands_not_deployment_recommendations() -> None:
    assert score_gates([GateRow("Scope gate", "pass", "", "", "")]).evidence_band == "Incomplete"


def test_project_issue_filter_uses_source_not_path_substring() -> None:
    issues = [
        ValidationIssue("unrelated/path", "bad results", source="eval_results"),
        ValidationIssue("looks-like-eval_results.csv", "project issue", source="project"),
    ]

    assert _non_eval_result_issues(issues) == [issues[1]]


def test_score_gates_uses_partial_half_credit() -> None:
    gates = [
        GateRow("Scope gate", "pass", "evidence", "None", "product"),
        GateRow("Golden eval gate", "partial", "evidence", "Add cases", "product"),
    ]

    result = score_gates(gates, boundary_coverage_status="fail")

    assert result.score == 10
    assert result.evidence_band == "Incomplete"


def test_routing_gate_shares_model_selection_weight() -> None:
    gates = [
        GateRow("Model selection gate", "pass", "evidence", "None", "ml"),
        GateRow(
            "Routing / capability allocation gate",
            "partial",
            "evidence",
            "Fix routing",
            "ml",
        ),
    ]

    result = score_gates(gates)

    assert sum(WEIGHTS.values()) == 100
    assert result.score == 4


def test_eval_summary_counts_case_types_and_risk_tiers() -> None:
    cases = load_eval_cases(CUSTOMER_SUPPORT / "eval_cases.yaml")
    case_types = Counter(case["case_type"] for case in cases)
    risk_tiers = Counter(case["risk_tier"] for case in cases)

    assert case_types["synthetic_boundary"] == 11
    assert case_types["historical_production"] == 2
    assert case_types["adversarial"] == 2
    assert case_types["fresh_drift_sample"] == 1
    assert case_types["regression"] == 1
    assert risk_tiers["low"] == 1
    assert risk_tiers["medium"] == 9
    assert risk_tiers["high"] == 5
    assert risk_tiers["prohibited"] == 2


def test_report_eval_results_summary_includes_feedback_metrics(
    customer_support_report: str,
) -> None:
    report = customer_support_report

    assert "Eval pass rate: 33%" in report
    assert "Admission-route match rate: 50%" in report
    assert "Failed case IDs: refund_abuse_history_002, refund_boundary_case_001, routine_status_no_escalation_013, wrong_destination_fraud_012" in report
    assert "Workflow-route accuracy: 50%" in report
    assert "Contrast-family reliability: 33%" in report
    assert "Required-escalation recall: 67%" in report
    assert "Over-escalation rate: 67%" in report
    assert "Destination accuracy: 33%" in report
    assert "Context-preservation rate: 67%" in report


def test_missing_eval_results_are_not_evaluated_and_cap_launch_recommendation(tmp_path: Path) -> None:
    project = tmp_path / "project"
    copytree(CUSTOMER_SUPPORT, project)
    (project / "eval_results.csv").unlink()

    report = generate_report(project)

    assert "**Behavioral evidence status:** Not evaluated — no results provided." in report
    assert "**Critical-control status:** Fail" in report
    assert "**Final launch recommendation:** Not ready for shadow evaluation" in report
    assert "**Maximum permitted stage:** Documentation remediation" in report
    assert "`missing_monitoring`" in report
    assert "Ready for bounded controlled launch" not in report


def test_empty_eval_results_are_distinguished_from_missing_results(tmp_path: Path) -> None:
    project = tmp_path / "project"
    copytree(CUSTOMER_SUPPORT, project)
    header = (project / "eval_results.csv").read_text(encoding="utf-8").splitlines()[0]
    (project / "eval_results.csv").write_text(header + "\n", encoding="utf-8")

    report = generate_report(project)

    assert "**Behavioral evidence status:** Not evaluated — results file contains no rows." in report
    assert "**Critical-control status:** Fail" in report
    assert "**Final launch recommendation:** Not ready for shadow evaluation" in report
    assert "**Maximum permitted stage:** Documentation remediation" in report


def test_empirical_results_without_hard_blockers_remain_shadow_only(tmp_path: Path) -> None:
    project = tmp_path / "project"
    copytree(CUSTOMER_SUPPORT, project)
    low_risk_case = next(
        case
        for case in load_eval_cases(project / "eval_cases.yaml")
        if case["risk_tier"] == "low"
    )
    (project / "eval_results.csv").write_text(
        "\n".join(
            [
                (
                    "run_id,case_id,candidate,evaluator,actual_route,expected_route,"
                    "route_match,passed,score,failure_category,failure_reason,"
                    "observed_output_path,reviewed_by,reviewed_at,notes"
                ),
                (
                    f"run_pass,{low_risk_case['id']},candidate,human_review,"
                    f"{low_risk_case['expected_route']},{low_risk_case['expected_route']},"
                    "true,true,1,,,,qa,2026-06-19,passing control fixture"
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    gate_review = project / "launch_gate_review.md"
    gate_review.write_text(
        gate_review.read_text(encoding="utf-8").replace(
            "| Observability gate | partial |",
            "| Observability gate | pass |",
        ),
        encoding="utf-8",
    )

    report = generate_report(project)

    assert "**Evidence completeness score:** 90/100" in report
    assert "**Behavioral evidence status:** Evaluated — valid empirical rows are available." in report
    assert "**Critical-control status:** No known blockers detected" in report
    assert "**Maximum permitted stage:** Shadow evaluation" in report
    assert "**Final launch recommendation:** Controlled-launch readiness not yet determined" in report
    assert "Verify required-slice coverage and behavioral thresholds before controlled launch." in report
    assert "Ready for bounded controlled launch" not in report
    assert "Critical-control status: Pass" not in report


def test_malformed_eval_results_are_invalid_not_missing(tmp_path: Path) -> None:
    project = tmp_path / "project"
    copytree(CUSTOMER_SUPPORT, project)
    (project / "eval_results.csv").write_text(
        "run_id,case_id\nrun_1,refund_boundary_case_001\n",
        encoding="utf-8",
    )

    report = generate_report(project)

    assert "**Behavioral evidence status:** Invalid — results could not be validated." in report
    assert "**Final launch recommendation:** Not ready" in report
    assert "**Maximum permitted stage:** Documentation remediation" in report
    assert "Validation issues:" in report


def test_invalid_results_and_incomplete_control_package_show_all_actions(
    tmp_path: Path,
) -> None:
    project = tmp_path / "project"
    copytree(CUSTOMER_SUPPORT, project)
    (project / "business_behavior_contract.md").unlink()
    (project / "eval_results.csv").write_text(
        "run_id,case_id\nrun_1,refund_boundary_case_001\n",
        encoding="utf-8",
    )

    report = generate_report(project)

    assert "Repair and revalidate eval_results.csv." in report
    assert "Complete missing or invalid control-evidence requirements." in report


def test_missing_results_do_not_hide_known_blockers(tmp_path: Path) -> None:
    project = tmp_path / "project"
    copytree(CUSTOMER_SUPPORT, project)
    (project / "eval_results.csv").unlink()
    text = (project / "launch_gate_review.md").read_text(encoding="utf-8")
    text = text.replace(
        "| Rollback gate | pass |",
        "| Rollback gate | fail |",
    )
    (project / "launch_gate_review.md").write_text(text, encoding="utf-8")

    report = generate_report(project)

    assert "**Behavioral evidence status:** Not evaluated — no results provided." in report
    assert "**Critical-control status:** Fail" in report
    assert "**Maximum permitted stage:** Documentation remediation" in report
    assert "**Final launch recommendation:** Not ready for shadow evaluation" in report
    assert "`missing_rollback`" in report


@pytest.mark.parametrize(
    "example_name",
    ["customer_support_assistant", "presales_assistant", "education_assistant"],
)
def test_generated_example_reports_are_reproducible(example_name: str) -> None:
    project = ROOT / "examples" / example_name
    report = generate_report(project)

    assert (project / "generated_launch_report.md").read_text(
        encoding="utf-8"
    ) == report
    assert "Ready for bounded controlled launch" not in report
    assert "Critical-control status: Pass" not in report
    assert "**Pass**" not in report
    assert ".;" not in report


@pytest.mark.parametrize(
    ("example_name", "expected_score", "rollback_status"),
    [
        ("customer_support_assistant", 90, "pass"),
        ("presales_assistant", 37, "partial"),
        ("education_assistant", 34, "partial"),
    ],
)
def test_canonical_scores_and_rollback_sections_are_consistent(
    example_name: str,
    expected_score: int,
    rollback_status: str,
    request: pytest.FixtureRequest,
) -> None:
    project = ROOT / "examples" / example_name
    inspection = inspect_project(project)
    score = score_gates(inspection.launch_gate_review)
    report = request.getfixturevalue(
        {
            "customer_support_assistant": "customer_support_report",
            "presales_assistant": "presales_report",
            "education_assistant": "education_report",
        }[example_name]
    )

    assert score.score == expected_score
    assert (
        f"| rollback gate | Yes | pass | {rollback_status} |"
        in report
    )
    assert f"- Rollback gate: {rollback_status}" in report


def test_non_scored_hard_gate_mitigations_remain_in_example_reports(
    presales_report: str,
    education_report: str,
) -> None:
    assert "- Rollback gate: Define launch stop criteria." in presales_report
    assert "- Owner signoff gate: Complete final review." in presales_report
    assert "- Rollback gate: Define stop criteria." in education_report
    assert (
        "- Owner signoff gate: Complete signoff after arena and drift plan."
        in education_report
    )


@pytest.mark.parametrize(
    "example_name",
    ["customer_support_assistant", "presales_assistant", "education_assistant"],
)
def test_every_weak_standard_gate_has_a_required_mitigation_line(
    example_name: str,
    request: pytest.FixtureRequest,
) -> None:
    project = ROOT / "examples" / example_name
    inspection = inspect_project(project)
    result = score_gates(inspection.launch_gate_review)
    report = request.getfixturevalue(
        {
            "customer_support_assistant": "customer_support_report",
            "presales_assistant": "presales_report",
            "education_assistant": "education_report",
        }[example_name]
    )

    for gate in result.weak_gates:
        mitigation = (
            gate.mitigation
            if is_meaningful_mitigation(gate.mitigation)
            else "mitigation not provided."
        )
        assert f"- {gate.gate}: {mitigation}" in report


def test_weak_gate_without_meaningful_mitigation_uses_fallback(
    tmp_path: Path,
) -> None:
    project = tmp_path / "project"
    copytree(CUSTOMER_SUPPORT, project)
    path = project / "launch_gate_review.md"
    path.write_text(
        path.read_text(encoding="utf-8").replace(
            (
                "| Rollback gate | pass | Product and engineering owners "
                "can pause rollout. | None | engineering |"
            ),
            (
                "| Rollback gate | partial | Product and engineering owners "
                "can pause rollout. | N/A | engineering |"
            ),
        ),
        encoding="utf-8",
    )

    report = generate_report(project)

    assert "- Rollback gate: mitigation not provided." in report


def test_legacy_manual_report_copies_are_removed() -> None:
    for example_name in (
        "customer_support_assistant",
        "presales_assistant",
        "education_assistant",
    ):
        assert not (ROOT / "examples" / example_name / "launch_report.md").exists()


def test_cli_commands_retain_success_exit_behavior(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["validate", str(CUSTOMER_SUPPORT / "eval_cases.yaml")]) == 0
    assert main(["check", str(CUSTOMER_SUPPORT)]) == 0
    assert main(["report", str(CUSTOMER_SUPPORT)]) == 0
    capsys.readouterr()


def test_check_and_report_do_not_conflict_on_invalid_results(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    project = tmp_path / "project"
    copytree(CUSTOMER_SUPPORT, project)
    (project / "eval_results.csv").write_text(
        "run_id,case_id\nrun_1,refund_boundary_case_001\n",
        encoding="utf-8",
    )

    assert main(["check", str(project)]) == 1
    check_output = capsys.readouterr().out
    report = generate_report(project)

    assert "Artifact validation failed. This is not a launch recommendation." in check_output
    assert "Invalid — results could not be validated." in report
    assert "**Final launch recommendation:** Not ready" in report


def test_high_risk_escalation_regression_is_hard_blocker(
    customer_support_report: str,
) -> None:
    report = customer_support_report

    assert "critical_escalation_regression" in report
    assert "refund_abuse_history_002" in report
    assert "wrong_destination_fraud_012" in report
    assert "## Final Launch Recommendation" in report
    assert "Not ready" in report


def test_report_summarizes_structured_escalation_contract(
    customer_support_report: str,
) -> None:
    report = customer_support_report

    assert "Structured escalation contract: valid." in report
    assert "Destinations: 6" in report
    assert "Handoff types: approval, async_case, conversation_handoff, specialist_routing" in report
    assert "Destination SLA coverage: 100%" in report
    assert "Checkpoint required: yes" in report
    assert "Eval handoff coverage: 9/9 required-handoff cases" in report


def test_report_summarizes_structured_routing_policy(
    customer_support_report: str,
) -> None:
    report = customer_support_report

    assert "Structured routing policy: valid." in report
    assert "Policy: customer_support_capability_allocation" in report
    assert "Workflow kinds: subagent=3, deterministic=1, human=2" in report
    assert "Assignment modes: fixed=2, adaptive=1, none=3" in report
    assert "Workflow fallback coverage: 100%" in report
    assert "High-risk control coverage: 100%" in report


def test_missing_files_report_shows_gaps_and_not_ready(tmp_path: Path) -> None:
    project = tmp_path / "project"
    copytree(CUSTOMER_SUPPORT, project)
    (project / "eval_cases.yaml").unlink()
    (project / "human_escalation_design.md").unlink()
    (project / "launch_gate_review.md").write_text(
        "\n".join(
            [
                "# Launch Gate Review",
                "",
                "| Gate | Status | Evidence | Required mitigation | Owner |",
                "| --- | --- | --- | --- | --- |",
                "| Scope gate | pass | Scope defined. | None | product |",
                "| Rollback gate | fail | No rollback. | Add rollback. | engineering |",
                "| Owner signoff gate | fail | No signoff. | Add signoff. | product |",
                "| Observability gate | fail | No monitoring. | Add monitoring. | platform |",
            ]
        ),
        encoding="utf-8",
    )

    report = generate_report(project)

    assert "missing_golden_eval" in report
    assert "missing_escalation_path" in report
    assert "missing_rollback" in report
    assert "missing_owner_signoff" in report
    assert "missing_monitoring" in report
    assert "Not ready to advance beyond documentation remediation" in report


def test_high_risk_action_without_controls_is_hard_blocker(tmp_path: Path) -> None:
    project = tmp_path / "project"
    copytree(CUSTOMER_SUPPORT, project)
    (project / "action_risk_matrix.csv").write_text(
        "\n".join(
            [
                "action,risk_tier,possible_harm,preconditions,deterministic_gate,human_review_required,owner",
                "issue_refund,high,Financial loss,Eligibility missing,,false,support_ops",
            ]
        ),
        encoding="utf-8",
    )

    report = generate_report(project)

    assert "ungated_high_risk_action" in report
    assert "Not ready" in report


def test_report_renders_duplicate_gate_as_invalid(tmp_path: Path) -> None:
    project = tmp_path / "project"
    copytree(CUSTOMER_SUPPORT, project)
    path = project / "launch_gate_review.md"
    path.write_text(
        path.read_text(encoding="utf-8")
        + "| Rollback gate | pass | duplicate evidence | None | owner |\n",
        encoding="utf-8",
    )

    report = generate_report(project)

    assert (
        "| rollback gate | Yes | pass | invalid: duplicate rows | Invalid |"
        in report
    )
    assert "- Rollback gate: invalid: duplicate rows" in report
    assert "`missing_rollback`" in report


def test_report_renders_unsupported_gate_status_as_invalid(
    tmp_path: Path,
) -> None:
    project = tmp_path / "project"
    copytree(CUSTOMER_SUPPORT, project)
    path = project / "launch_gate_review.md"
    path.write_text(
        path.read_text(encoding="utf-8").replace(
            "| Rollback gate | pass |",
            "| Rollback gate | warning |",
        ),
        encoding="utf-8",
    )

    report = generate_report(project)

    assert (
        "| rollback gate | Yes | pass | invalid: warning | Invalid |"
        in report
    )
    assert "- Rollback gate: invalid: warning" in report


def test_report_renders_truly_missing_rollback_consistently(
    tmp_path: Path,
) -> None:
    project = tmp_path / "project"
    copytree(CUSTOMER_SUPPORT, project)
    path = project / "launch_gate_review.md"
    lines = [
        line
        for line in path.read_text(encoding="utf-8").splitlines()
        if not line.startswith("| Rollback gate |")
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    report = generate_report(project)

    assert "| rollback gate | Yes | pass | missing | Blocked |" in report
    assert "- Rollback gate: missing" in report


def test_invalid_duplicate_risk_header_summary_uses_unknown_counts(
    tmp_path: Path,
) -> None:
    project = tmp_path / "project"
    copytree(CUSTOMER_SUPPORT, project)
    (project / "action_risk_matrix.csv").write_text(
        "\n".join(
            [
                (
                    "action,risk_tier,risk_tier,deterministic_gate,"
                    "human_review_required"
                ),
                "refund,low,high,,false",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    report = generate_report(project)
    inspection = inspect_project(project)
    section = report.split("## Tool/Action Safety Summary\n", 1)[1].split(
        "\n\n## Input/Output Perimeter Summary",
        1,
    )[0]

    assert (
        "Action-risk matrix: invalid; the following counts are diagnostic "
        "only and were not used for policy decisions."
    ) in section
    assert "- Rows: 1" in section
    assert "- Risk tiers: unknown=1" in section
    assert "High/prohibited actions" not in section
    assert not inspection.check.action_risk_review.valid
    assert inspection.context.has_tool_actions is None
    assert (
        "risk_tier"
        not in inspection.check.action_risk_review.rows[0].raw_values
    )


def test_invalid_unrelated_duplicate_header_preserves_unique_tier_counts(
    tmp_path: Path,
) -> None:
    project = tmp_path / "project"
    copytree(CUSTOMER_SUPPORT, project)
    (project / "action_risk_matrix.csv").write_text(
        "\n".join(
            [
                (
                    "action,risk_tier,extra,extra,deterministic_gate,"
                    "human_review_required"
                ),
                "refund,high,a,b,,false",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    report = generate_report(project)
    inspection = inspect_project(project)
    section = report.split("## Tool/Action Safety Summary\n", 1)[1].split(
        "\n\n## Input/Output Perimeter Summary",
        1,
    )[0]

    assert "- Risk tiers: high=1" in section
    assert "High/prohibited actions" not in section
    assert "ungated_high_risk_action" not in report
    assert not inspection.check.action_risk_review.valid
    assert inspection.context.has_tool_actions is None


def test_missing_and_valid_action_risk_summaries_keep_existing_behavior(
    tmp_path: Path,
    customer_support_report: str,
) -> None:
    valid_section = customer_support_report.split(
        "## Tool/Action Safety Summary\n",
        1,
    )[1].split("\n\n## Input/Output Perimeter Summary", 1)[0]
    assert "- Rows: 7" in valid_section
    assert "High/prohibited actions:" in valid_section

    project = tmp_path / "project"
    copytree(CUSTOMER_SUPPORT, project)
    (project / "action_risk_matrix.csv").unlink()
    missing_report = generate_report(project)
    assert (
        "## Tool/Action Safety Summary\nNo action risk matrix found."
        in missing_report
    )
