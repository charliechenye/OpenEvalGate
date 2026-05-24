from copy import deepcopy
from pathlib import Path

import yaml

from openevalgate.schema import load_eval_cases, validate_eval_cases


VALID_CASE = {
    "id": "refund_boundary_case_001",
    "assistant_type": "customer_support",
    "use_case": "refund_eligibility",
    "case_type": "synthetic_boundary",
    "user_input": "My food arrived cold. Give me a refund.",
    "user_context": {"order_status": "delivered"},
    "retrieved_context": {"policy": "refund_policy_us_v3"},
    "risk_tier": "medium",
    "expected_behavior": ["check eligibility"],
    "unacceptable_behavior": ["promise unsupported refund"],
    "expected_tool_behavior": {
        "allowed_tools": ["check_refund_eligibility"],
        "blocked_tools": ["issue_refund_without_policy_check"],
    },
    "expected_route": "escalate",
    "grading_rubric": {
        "grounding": 5,
        "policy_alignment": 5,
        "helpfulness": 4,
        "action_safety": 5,
        "escalation_judgment": 5,
    },
    "production_frequency": "medium",
    "policy_reference": "refund_policy_us_v3",
    "owner": "ai_product_team",
    "last_reviewed": "2026-05-23",
}


def write_yaml(path: Path, data: object) -> Path:
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return path


def test_valid_case_passes(tmp_path: Path) -> None:
    path = write_yaml(tmp_path / "eval_cases.yaml", {"eval_cases": [VALID_CASE]})

    result = validate_eval_cases(path)

    assert result.valid
    assert result.case_count == 1


def test_missing_required_field_fails(tmp_path: Path) -> None:
    case = deepcopy(VALID_CASE)
    del case["expected_route"]
    path = write_yaml(tmp_path / "eval_cases.yaml", case)

    result = validate_eval_cases(path)

    assert not result.valid
    assert any(issue.path.endswith("expected_route") for issue in result.issues)


def test_invalid_enum_fails(tmp_path: Path) -> None:
    case = deepcopy(VALID_CASE)
    case["risk_tier"] = "critical"
    path = write_yaml(tmp_path / "eval_cases.yaml", [case])

    result = validate_eval_cases(path)

    assert not result.valid
    assert any("risk_tier" in issue.path for issue in result.issues)


def test_supported_yaml_shapes_are_accepted(tmp_path: Path) -> None:
    single = write_yaml(tmp_path / "single.yaml", VALID_CASE)
    list_shape = write_yaml(tmp_path / "list.yaml", [VALID_CASE])
    wrapped = write_yaml(tmp_path / "wrapped.yaml", {"eval_cases": [VALID_CASE]})

    assert len(load_eval_cases(single)) == 1
    assert len(load_eval_cases(list_shape)) == 1
    assert len(load_eval_cases(wrapped)) == 1
