from collections import Counter
from pathlib import Path
from shutil import copytree

from openevalgate.report import generate_report
from openevalgate.schema import load_eval_cases
from openevalgate.scorer import WEIGHTS, readiness_recommendation, score_gates, GateRow


ROOT = Path(__file__).resolve().parents[1]
CUSTOMER_SUPPORT = ROOT / "examples" / "customer_support_assistant"


def test_report_generation_returns_expected_sections() -> None:
    report = generate_report(CUSTOMER_SUPPORT)

    assert "# Launch Readiness Report: Customer Support Refund Assistant" in report
    assert "## Executive Summary" in report
    assert "## Hard Blockers" in report
    assert "## Trust Preservation Summary" in report
    assert "## Business Behavior Contract Summary" in report
    assert "## Tail-Risk / P0 Failure Mode Summary" in report
    assert "## Metric Stack Summary" in report
    assert "## Golden Eval Summary" in report
    assert "## Eval Results Summary" in report
    assert "## Model Arena Summary" in report
    assert "## Routing / Capability Allocation Summary" in report


def test_recommendation_bands_match_thresholds() -> None:
    assert readiness_recommendation(85) == "Ready for controlled launch"
    assert readiness_recommendation(70) == "Conditional launch"
    assert readiness_recommendation(50) == "Shadow launch only"
    assert readiness_recommendation(49) == "Not ready"


def test_score_gates_uses_partial_half_credit() -> None:
    gates = [
        GateRow("Scope gate", "pass", "evidence", "None", "product"),
        GateRow("Golden eval gate", "partial", "evidence", "Add cases", "product"),
    ]

    result = score_gates(gates, boundary_coverage_status="fail")

    assert result.score == 10
    assert result.recommendation == "Not ready"


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


def test_report_eval_results_summary_includes_feedback_metrics() -> None:
    report = generate_report(CUSTOMER_SUPPORT)

    assert "Pass rate: 33%" in report
    assert "Route match rate: 50%" in report
    assert "Failed case IDs: refund_abuse_history_002, refund_boundary_case_001, routine_status_no_escalation_013, wrong_destination_fraud_012" in report
    assert "Workflow-route accuracy: 50%" in report
    assert "Contrast-family reliability: 33%" in report
    assert "Required-escalation recall: 67%" in report
    assert "Over-escalation rate: 67%" in report
    assert "Destination accuracy: 33%" in report
    assert "Context-preservation rate: 67%" in report


def test_high_risk_escalation_regression_is_hard_blocker() -> None:
    report = generate_report(CUSTOMER_SUPPORT)

    assert "critical_escalation_regression" in report
    assert "refund_abuse_history_002" in report
    assert "wrong_destination_fraud_012" in report
    assert "## Final Launch Recommendation" in report
    assert "Not ready" in report


def test_report_summarizes_structured_escalation_contract() -> None:
    report = generate_report(CUSTOMER_SUPPORT)

    assert "Structured escalation contract: valid." in report
    assert "Destinations: 6" in report
    assert "Handoff types: approval, async_case, conversation_handoff, specialist_routing" in report
    assert "Destination SLA coverage: 100%" in report
    assert "Checkpoint required: yes" in report
    assert "Eval handoff coverage: 9/9 required-handoff cases" in report


def test_report_summarizes_structured_routing_policy() -> None:
    report = generate_report(CUSTOMER_SUPPORT)

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
    assert "Not ready. Do not launch until hard blockers are resolved." in report


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
