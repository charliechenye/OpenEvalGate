from collections import Counter
from pathlib import Path

from openevalgate.report import generate_report
from openevalgate.schema import load_eval_cases
from openevalgate.scorer import readiness_recommendation, score_gates, GateRow


ROOT = Path(__file__).resolve().parents[1]
CUSTOMER_SUPPORT = ROOT / "examples" / "customer_support_assistant"


def test_report_generation_returns_expected_sections() -> None:
    report = generate_report(CUSTOMER_SUPPORT)

    assert "# Launch Readiness Report: Customer Support Refund Assistant" in report
    assert "## Passed Gates" in report
    assert "## Failed Or Weak Gates" in report
    assert "## Eval Set Summary" in report
    assert "## Eval Results Summary" in report
    assert "## Model Arena Summary" in report


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

    assert result.score == 14
    assert result.recommendation == "Not ready"


def test_eval_summary_counts_case_types_and_risk_tiers() -> None:
    cases = load_eval_cases(CUSTOMER_SUPPORT / "eval_cases.yaml")
    case_types = Counter(case["case_type"] for case in cases)
    risk_tiers = Counter(case["risk_tier"] for case in cases)

    assert case_types["synthetic_boundary"] == 1
    assert case_types["historical_production"] == 1
    assert case_types["adversarial"] == 1
    assert risk_tiers["medium"] == 2
    assert risk_tiers["high"] == 1


def test_report_eval_results_summary_includes_feedback_metrics() -> None:
    report = generate_report(CUSTOMER_SUPPORT)

    assert "Pass rate: 67%" in report
    assert "Route match rate: 67%" in report
    assert "Failed case IDs: refund_abuse_history_002" in report
