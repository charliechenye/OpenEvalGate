from copy import deepcopy
from pathlib import Path
from shutil import copytree

import yaml

from openevalgate.report import generate_report
from openevalgate.routing import summarize_routing_policy, validate_routing_policy
from openevalgate.validator import check_project


ROOT = Path(__file__).resolve().parents[1]
CUSTOMER_SUPPORT = ROOT / "examples" / "customer_support_assistant"

VALID_POLICY = {
    "schema_version": "1",
    "routing_policy": {
        "metadata": {
            "id": "support_routing",
            "version": "1.0.0",
            "owner": "platform",
            "last_reviewed": "2026-06-18",
        },
        "models": [
            {
                "id": "small",
                "provider": "provider",
                "model_version": "small-v1",
                "capability_tier": "small",
            },
            {
                "id": "strong",
                "provider": "provider",
                "model_version": "strong-v1",
                "capability_tier": "strong",
            },
        ],
        "workflows": [
            {
                "id": "answer",
                "name": "Answer specialist",
                "kind": "subagent",
                "owner": "product",
                "risk_tier": "medium",
                "scenarios": ["routine"],
                "mandatory_controls": ["grounding"],
                "fallback_workflow_id": "review",
                "eval_cases": [],
                "model_assignment": {
                    "mode": "adaptive",
                    "approved_models": ["small", "strong"],
                    "default_model": "small",
                    "reasoning_level": "medium",
                    "selection_rule": "Use strong for conflicting evidence.",
                },
            },
            {
                "id": "review",
                "name": "Human review",
                "kind": "human",
                "owner": "operations",
                "risk_tier": "high",
                "scenarios": ["exception"],
                "mandatory_controls": ["approval"],
                "fallback_workflow_id": "block",
                "eval_cases": [],
                "model_assignment": {
                    "mode": "none",
                    "approved_models": [],
                    "default_model": "",
                    "reasoning_level": "none",
                },
            },
            {
                "id": "block",
                "name": "Policy block",
                "kind": "deterministic",
                "owner": "risk",
                "risk_tier": "prohibited",
                "scenarios": ["prohibited"],
                "mandatory_controls": ["hard_block"],
                "fallback_workflow_id": "review",
                "eval_cases": [],
                "model_assignment": {
                    "mode": "none",
                    "approved_models": [],
                    "default_model": "",
                    "reasoning_level": "none",
                },
            },
        ],
        "observability": {
            "required_fields": [
                "workflow_id",
                "model_id",
                "routing_policy_version",
                "routing_reason",
            ]
        },
        "rollback": {
            "owner": "platform",
            "fallback_workflow_id": "review",
            "triggers": ["p0_failure"],
        },
        "recertification": {
            "cadence_days": 90,
            "required_reviewers": ["product", "engineering", "risk"],
        },
    }
}


def write_policy(path: Path, policy: dict) -> Path:
    path.write_text(yaml.safe_dump(policy, sort_keys=False), encoding="utf-8")
    return path


def test_valid_fixed_adaptive_and_no_model_assignments_pass(tmp_path: Path) -> None:
    result = validate_routing_policy(write_policy(tmp_path / "routing_policy.yaml", VALID_POLICY))

    assert result.valid
    assert result.model_count == 2
    assert result.workflow_count == 3

    fixed_policy = deepcopy(VALID_POLICY)
    fixed_assignment = fixed_policy["routing_policy"]["workflows"][0]["model_assignment"]
    fixed_assignment["mode"] = "fixed"
    fixed_assignment["approved_models"] = ["small"]
    fixed_assignment["default_model"] = "small"
    fixed_assignment.pop("selection_rule")

    fixed_result = validate_routing_policy(
        write_policy(tmp_path / "fixed_routing_policy.yaml", fixed_policy)
    )

    assert fixed_result.valid


def test_routing_policy_v1_envelope_and_extensions_fail_closed(tmp_path: Path) -> None:
    policy = deepcopy(VALID_POLICY)
    policy["routing_policy"]["extensions"] = {"vendor": {"trace_schema": "v1"}}
    assert validate_routing_policy(write_policy(tmp_path / "extended.yaml", policy)).valid

    policy["routing_policy"]["vendor_metadata"] = {"trace_schema": "v1"}
    result = validate_routing_policy(write_policy(tmp_path / "unknown.yaml", policy))
    assert not result.valid
    assert any("Unsupported routing-policy field" in issue.message for issue in result.issues)

    policy = deepcopy(VALID_POLICY)
    policy["schema_version"] = "2"
    result = validate_routing_policy(write_policy(tmp_path / "wrong-version.yaml", policy))
    assert not result.valid
    assert "schema_version" in result.issues[0].message


def test_invalid_ids_fallbacks_and_eval_references_fail(tmp_path: Path) -> None:
    policy = deepcopy(VALID_POLICY)
    duplicate = deepcopy(policy["routing_policy"]["workflows"][0])
    duplicate["fallback_workflow_id"] = "missing"
    duplicate["eval_cases"] = ["missing_case"]
    policy["routing_policy"]["workflows"].append(duplicate)
    eval_path = tmp_path / "eval_cases.yaml"
    eval_path.write_text(
        yaml.safe_dump({"schema_version": "1", "eval_cases": [{"id": "known_case"}]}),
        encoding="utf-8",
    )

    result = validate_routing_policy(
        write_policy(tmp_path / "routing_policy.yaml", policy),
        eval_path,
    )

    assert not result.valid
    assert any("Duplicate workflow id" in issue.message for issue in result.issues)
    assert any("Unknown workflow id" in issue.message for issue in result.issues)
    assert any("Unknown eval case id" in issue.message for issue in result.issues)


def test_assignment_modes_and_high_risk_controls_are_enforced(tmp_path: Path) -> None:
    policy = deepcopy(VALID_POLICY)
    answer = policy["routing_policy"]["workflows"][0]
    answer["model_assignment"]["approved_models"] = ["small", "missing"]
    review = policy["routing_policy"]["workflows"][1]
    review["model_assignment"] = {
        "mode": "fixed",
        "approved_models": ["small"],
        "default_model": "small",
        "reasoning_level": "low",
    }
    review["mandatory_controls"] = []

    result = validate_routing_policy(write_policy(tmp_path / "routing_policy.yaml", policy))

    assert not result.valid
    assert any("Unknown model id" in issue.message for issue in result.issues)
    assert any(
        "Deterministic and human workflows require none" in issue.message for issue in result.issues
    )
    assert any("require at least one control" in issue.message for issue in result.issues)


def test_missing_policy_remains_optional(tmp_path: Path) -> None:
    project = tmp_path / "project"
    copytree(CUSTOMER_SUPPORT, project)
    (project / "routing_policy.yaml").unlink()

    result = check_project(project)

    assert result.valid
    assert "routing_policy.yaml" not in result.present_optional


def test_invalid_optional_policy_fails_check_and_blocks_report(tmp_path: Path) -> None:
    project = tmp_path / "project"
    copytree(CUSTOMER_SUPPORT, project)
    policy = yaml.safe_load((project / "routing_policy.yaml").read_text(encoding="utf-8"))
    policy["routing_policy"]["workflows"][0]["fallback_workflow_id"] = "missing"
    write_policy(project / "routing_policy.yaml", policy)

    result = check_project(project)
    report = generate_report(project)

    assert not result.valid
    assert "invalid_routing_policy" in report
    assert "Structured routing policy is invalid." in report


def test_summary_counts_workflow_and_assignment_types() -> None:
    summary = summarize_routing_policy(CUSTOMER_SUPPORT / "routing_policy.yaml")

    assert summary.valid
    assert summary.subagent_count == 3
    assert summary.deterministic_count == 1
    assert summary.human_count == 2
    assert summary.fixed_count == 2
    assert summary.adaptive_count == 1
    assert summary.no_model_count == 3
