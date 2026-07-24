from copy import deepcopy
from pathlib import Path

import yaml

from openevalgate.escalation import validate_escalation_contract


VALID_CONTRACT = {
    "schema_version": "1",
    "escalation_contract": {
        "workflow": {
            "id": "refund_request",
            "name": "Refund request",
            "owner": "support_ops",
            "version": "1.0.0",
            "risk_tier": "high",
            "policy_version": "refund_policy_v1",
        },
        "boundaries": {
            "resolve_when": ["routine request"],
            "clarify_when": ["missing order"],
            "escalate_when": ["fraud signal"],
            "approval_required_when": ["high-value refund"],
            "refuse_or_block_when": ["policy bypass"],
        },
        "triggers": [
            {
                "id": "high_value_refund",
                "condition": "refund_amount > 100",
                "path": "approval",
                "destination": "refund_review",
            }
        ],
        "handoff": {
            "minimum_sufficient_context": True,
            "required_fields": ["user_goal", "policy_version"],
        },
        "routing": {
            "destinations": [
                {
                    "id": "refund_review",
                    "handoff_type": "approval",
                    "sla_minutes": 30,
                    "fallback": "hold_and_notify",
                    "owner": "support_policy",
                }
            ]
        },
        "durable_state": {
            "checkpoint_required": True,
            "idempotency_key_required": True,
            "resume_behavior": "Revalidate and execute once.",
        },
        "evaluation": {"required_eval_slices": []},
        "recertification": {
            "cadence_days": 90,
            "required_reviewers": ["product", "operations"],
        },
    }
}


def write_contract(path: Path, contract: dict) -> Path:
    path.write_text(yaml.safe_dump(contract, sort_keys=False), encoding="utf-8")
    return path


def test_valid_escalation_contract_passes(tmp_path: Path) -> None:
    result = validate_escalation_contract(
        write_contract(tmp_path / "escalation_contract.yaml", VALID_CONTRACT)
    )

    assert result.valid
    assert result.trigger_count == 1
    assert result.destination_count == 1


def test_escalation_contract_v1_envelope_and_extensions_fail_closed(tmp_path: Path) -> None:
    contract = deepcopy(VALID_CONTRACT)
    contract["escalation_contract"]["extensions"] = {"vendor": {"queue": "internal"}}
    assert validate_escalation_contract(write_contract(tmp_path / "extended.yaml", contract)).valid

    contract["escalation_contract"]["vendor_metadata"] = {"queue": "internal"}
    result = validate_escalation_contract(write_contract(tmp_path / "unknown.yaml", contract))
    assert not result.valid
    assert any("Unsupported escalation-contract field" in issue.message for issue in result.issues)

    contract = deepcopy(VALID_CONTRACT)
    contract["schema_version"] = "2"
    result = validate_escalation_contract(write_contract(tmp_path / "wrong-version.yaml", contract))
    assert not result.valid
    assert "schema_version" in result.issues[0].message


def test_duplicate_and_unknown_ids_fail(tmp_path: Path) -> None:
    contract = deepcopy(VALID_CONTRACT)
    destination = deepcopy(contract["escalation_contract"]["routing"]["destinations"][0])
    contract["escalation_contract"]["routing"]["destinations"].append(destination)
    trigger = deepcopy(contract["escalation_contract"]["triggers"][0])
    trigger["destination"] = "missing_queue"
    contract["escalation_contract"]["triggers"].append(trigger)

    result = validate_escalation_contract(
        write_contract(tmp_path / "escalation_contract.yaml", contract)
    )

    assert not result.valid
    assert any("Duplicate destination id" in issue.message for issue in result.issues)
    assert any("Duplicate trigger id" in issue.message for issue in result.issues)
    assert any("Unknown destination id" in issue.message for issue in result.issues)


def test_destination_requires_sla_and_fallback(tmp_path: Path) -> None:
    contract = deepcopy(VALID_CONTRACT)
    destination = contract["escalation_contract"]["routing"]["destinations"][0]
    destination["sla_minutes"] = 0
    destination["fallback"] = ""

    result = validate_escalation_contract(
        write_contract(tmp_path / "escalation_contract.yaml", contract)
    )

    assert not result.valid
    assert any("sla_minutes" in issue.path for issue in result.issues)
    assert any("fallback" in issue.path for issue in result.issues)


def test_approval_requires_checkpoint_and_idempotency(tmp_path: Path) -> None:
    contract = deepcopy(VALID_CONTRACT)
    durable_state = contract["escalation_contract"]["durable_state"]
    durable_state["checkpoint_required"] = False
    durable_state["idempotency_key_required"] = False

    result = validate_escalation_contract(
        write_contract(tmp_path / "escalation_contract.yaml", contract)
    )

    assert not result.valid
    assert any("Approval paths require checkpoint" in issue.message for issue in result.issues)
    assert any("Approval paths require idempotency" in issue.message for issue in result.issues)


def test_eval_handoff_must_match_trigger_and_destination_type(tmp_path: Path) -> None:
    contract_path = write_contract(tmp_path / "escalation_contract.yaml", VALID_CONTRACT)
    eval_path = tmp_path / "eval_cases.yaml"
    eval_path.write_text(
        yaml.safe_dump(
                {
                    "schema_version": "1",
                    "eval_cases": [
                    {
                        "id": "refund_case",
                        "expected_handoff": {
                            "trigger_id": "high_value_refund",
                            "handoff_type": "specialist_routing",
                            "destination": "wrong_destination",
                        },
                    }
                ]
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    result = validate_escalation_contract(contract_path, eval_path)

    assert not result.valid
    assert any("Unknown escalation destination" in issue.message for issue in result.issues)
    assert any("routes to refund_review" in issue.message for issue in result.issues)
