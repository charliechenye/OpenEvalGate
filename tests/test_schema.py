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
    if isinstance(data, list):
        data = {"schema_version": "1", "eval_cases": data}
    elif isinstance(data, dict) and "schema_version" not in data:
        data = {
            "schema_version": "1",
            "eval_cases": data.get("eval_cases", [data]),
        }
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


def test_only_the_schema_versioned_eval_case_envelope_is_accepted(tmp_path: Path) -> None:
    valid = write_yaml(tmp_path / "valid.yaml", [VALID_CASE])
    legacy = tmp_path / "legacy.yaml"
    legacy.write_text(yaml.safe_dump([VALID_CASE]), encoding="utf-8")

    assert len(load_eval_cases(valid)) == 1
    result = validate_eval_cases(legacy)
    assert not result.valid
    assert "schema_version" in result.issues[0].message or "document" in result.issues[0].message


def test_eval_case_extensions_are_isolated_and_unknown_envelope_fields_fail(tmp_path: Path) -> None:
    extended = {
        "schema_version": "1",
        "eval_cases": [VALID_CASE],
        "extensions": {"runner": {"name": "external"}},
    }
    assert validate_eval_cases(write_yaml(tmp_path / "extended.yaml", extended)).valid

    extended["unexpected"] = True
    result = validate_eval_cases(write_yaml(tmp_path / "unexpected.yaml", extended))
    assert not result.valid
    assert "unsupported field" in result.issues[0].message


def test_eval_case_schema_version_and_case_extensions_fail_closed(tmp_path: Path) -> None:
    invalid_version = {"schema_version": "2", "eval_cases": [VALID_CASE]}
    result = validate_eval_cases(write_yaml(tmp_path / "version.yaml", invalid_version))
    assert not result.valid
    assert "schema_version" in result.issues[0].message

    invalid_case = deepcopy(VALID_CASE)
    invalid_case["runner_metadata"] = {"provider": "external"}
    result = validate_eval_cases(write_yaml(tmp_path / "case.yaml", [invalid_case]))
    assert not result.valid
    assert any("Unsupported eval-case field" in issue.message for issue in result.issues)

    extended_case = deepcopy(VALID_CASE)
    extended_case["extensions"] = {"runner": {"provider": "external"}}
    assert validate_eval_cases(write_yaml(tmp_path / "extended-case.yaml", [extended_case])).valid


def test_valid_boundary_family_passes(tmp_path: Path) -> None:
    anchor = deepcopy(VALID_CASE)
    anchor["id"] = "refund_anchor"
    anchor["expected_workflow_route"] = "act"
    anchor["boundary"] = {
        "family_id": "refund_limit",
        "anchor_case_id": "refund_anchor",
        "controlling_fact": "requested_refund",
        "variation_type": "anchor",
        "before_value": 49.99,
        "after_value": 49.99,
    }
    anchor["expected_trajectory"] = {
        "required_events": ["issue_refund"],
        "prohibited_events": ["create_review_case"],
    }
    anchor["expected_end_state"] = {"assertions": ["refund_issued"]}

    variant = deepcopy(anchor)
    variant["id"] = "refund_above_limit"
    variant["expected_workflow_route"] = "approval"
    variant["boundary"] = {
        "family_id": "refund_limit",
        "anchor_case_id": "refund_anchor",
        "controlling_fact": "requested_refund",
        "variation_type": "threshold_neighbor",
        "before_value": 49.99,
        "after_value": 50.01,
    }

    path = write_yaml(tmp_path / "eval_cases.yaml", {"eval_cases": [anchor, variant]})

    result = validate_eval_cases(path)

    assert result.valid


def test_boundary_anchor_must_exist_and_be_anchor(tmp_path: Path) -> None:
    case = deepcopy(VALID_CASE)
    case["boundary"] = {
        "family_id": "refund_limit",
        "anchor_case_id": "missing_anchor",
        "controlling_fact": "requested_refund",
        "variation_type": "threshold_neighbor",
        "before_value": 49.99,
        "after_value": 50.01,
    }
    path = write_yaml(tmp_path / "eval_cases.yaml", [case])

    result = validate_eval_cases(path)

    assert not result.valid
    assert any("Unknown boundary anchor" in issue.message for issue in result.issues)


def test_invalid_optional_boundary_contract_fails(tmp_path: Path) -> None:
    case = deepcopy(VALID_CASE)
    case["expected_workflow_route"] = "execute"
    case["expected_trajectory"] = {"required_events": "issue_refund"}
    case["expected_end_state"] = {"assertions": "refund_issued"}
    path = write_yaml(tmp_path / "eval_cases.yaml", [case])

    result = validate_eval_cases(path)

    assert not result.valid
    assert any("expected_workflow_route" in issue.path for issue in result.issues)
    assert any("prohibited_events" in issue.path for issue in result.issues)
    assert any("expected_end_state.assertions" in issue.path for issue in result.issues)


def test_valid_expected_handoff_passes(tmp_path: Path) -> None:
    case = deepcopy(VALID_CASE)
    case["expected_workflow_route"] = "escalate"
    case["expected_handoff"] = {
        "trigger_id": "policy_ambiguity",
        "handoff_type": "specialist_routing",
        "destination": "policy_review",
        "required_payload_fields": ["user_goal", "policy_version"],
        "fallback": "senior_review",
        "resume_behavior": "Resume after the policy decision is recorded.",
    }
    path = write_yaml(tmp_path / "eval_cases.yaml", [case])

    result = validate_eval_cases(path)

    assert result.valid


def test_expected_handoff_requires_escalation_workflow_route(tmp_path: Path) -> None:
    case = deepcopy(VALID_CASE)
    case["expected_workflow_route"] = "answer"
    case["expected_handoff"] = {
        "trigger_id": "policy_ambiguity",
        "handoff_type": "specialist_routing",
        "destination": "policy_review",
        "required_payload_fields": [],
        "fallback": "senior_review",
        "resume_behavior": "Resume after review.",
    }
    path = write_yaml(tmp_path / "eval_cases.yaml", [case])

    result = validate_eval_cases(path)

    assert not result.valid
    assert any("Expected handoff requires" in issue.message for issue in result.issues)
