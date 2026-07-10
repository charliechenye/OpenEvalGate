"""Structured human-escalation contract validation and summaries."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from openevalgate.schema import RISK_TIERS, ValidationIssue, load_eval_cases


HANDOFF_TYPES = {
    "conversation_handoff",
    "async_case",
    "approval",
    "specialist_routing",
}
BOUNDARY_PATHS = {"resolve", "clarify", "escalate", "approval", "refuse"}


@dataclass(frozen=True)
class EscalationContractValidationResult:
    valid: bool
    issues: list[ValidationIssue]
    trigger_count: int = 0
    destination_count: int = 0


@dataclass(frozen=True)
class EscalationContractSummary:
    present: bool
    valid: bool
    workflow_id: str | None
    trigger_count: int
    destination_count: int
    destinations: list[str]
    handoff_types: list[str]
    sla_coverage: float | None
    fallback_coverage: float | None
    checkpoint_required: bool | None
    idempotency_required: bool | None
    resume_behavior_defined: bool | None
    required_eval_slice_count: int


def load_escalation_contract(path: str | Path) -> dict[str, Any]:
    """Load the supported wrapped escalation-contract YAML shape."""

    with Path(path).open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict) or not isinstance(data.get("escalation_contract"), dict):
        raise ValueError("YAML must contain an escalation_contract object")
    return data["escalation_contract"]


def validate_escalation_contract(
    path: str | Path,
    eval_cases_path: str | Path | None = None,
) -> EscalationContractValidationResult:
    """Validate an optional project escalation contract and its eval references."""

    contract_path = Path(path)
    issues: list[ValidationIssue] = []
    try:
        contract = load_escalation_contract(contract_path)
    except Exception as exc:  # noqa: BLE001 - CLI validation should report parser errors.
        return EscalationContractValidationResult(
            False,
            [ValidationIssue(str(contract_path), str(exc))],
        )

    workflow = contract.get("workflow")
    if not isinstance(workflow, dict):
        issues.append(
            ValidationIssue("escalation_contract.workflow", "Required object is missing.")
        )
    else:
        for field in ("id", "name", "owner", "version", "risk_tier", "policy_version"):
            _require_non_empty_string(workflow, field, issues, "escalation_contract.workflow")
        if workflow.get("risk_tier") not in RISK_TIERS:
            issues.append(
                ValidationIssue(
                    "escalation_contract.workflow.risk_tier",
                    f"Must be one of: {', '.join(sorted(RISK_TIERS))}.",
                )
            )

    boundaries = contract.get("boundaries")
    if not isinstance(boundaries, dict):
        issues.append(
            ValidationIssue("escalation_contract.boundaries", "Required object is missing.")
        )
    else:
        for field in (
            "resolve_when",
            "clarify_when",
            "escalate_when",
            "approval_required_when",
            "refuse_or_block_when",
        ):
            _require_list(boundaries, field, issues, "escalation_contract.boundaries")

    destinations = _routing_destinations(contract, issues)
    destination_ids = _validate_destinations(destinations, issues)
    triggers = contract.get("triggers")
    trigger_ids = _validate_triggers(triggers, destination_ids, issues)

    handoff = contract.get("handoff")
    if not isinstance(handoff, dict):
        issues.append(ValidationIssue("escalation_contract.handoff", "Required object is missing."))
    else:
        _require_list(handoff, "required_fields", issues, "escalation_contract.handoff")
        if handoff.get("minimum_sufficient_context") is not True:
            issues.append(
                ValidationIssue(
                    "escalation_contract.handoff.minimum_sufficient_context",
                    "Must be true.",
                )
            )

    durable_state = contract.get("durable_state")
    if not isinstance(durable_state, dict):
        issues.append(
            ValidationIssue("escalation_contract.durable_state", "Required object is missing.")
        )
    else:
        for field in ("checkpoint_required", "idempotency_key_required"):
            if not isinstance(durable_state.get(field), bool):
                issues.append(
                    ValidationIssue(
                        f"escalation_contract.durable_state.{field}",
                        "Must be true or false.",
                    )
                )
        _require_non_empty_string(
            durable_state,
            "resume_behavior",
            issues,
            "escalation_contract.durable_state",
        )

    if _has_approval_path(triggers, boundaries):
        if (
            not isinstance(durable_state, dict)
            or durable_state.get("checkpoint_required") is not True
        ):
            issues.append(
                ValidationIssue(
                    "escalation_contract.durable_state.checkpoint_required",
                    "Approval paths require checkpoint_required: true.",
                )
            )
        if (
            not isinstance(durable_state, dict)
            or durable_state.get("idempotency_key_required") is not True
        ):
            issues.append(
                ValidationIssue(
                    "escalation_contract.durable_state.idempotency_key_required",
                    "Approval paths require idempotency_key_required: true.",
                )
            )

    evaluation = contract.get("evaluation")
    required_slices: list[Any] = []
    if not isinstance(evaluation, dict):
        issues.append(
            ValidationIssue("escalation_contract.evaluation", "Required object is missing.")
        )
    else:
        required_slices = evaluation.get("required_eval_slices", [])
        _require_list(evaluation, "required_eval_slices", issues, "escalation_contract.evaluation")

    recertification = contract.get("recertification")
    if not isinstance(recertification, dict):
        issues.append(
            ValidationIssue("escalation_contract.recertification", "Required object is missing.")
        )
    else:
        cadence = recertification.get("cadence_days")
        if not isinstance(cadence, int) or cadence <= 0:
            issues.append(
                ValidationIssue(
                    "escalation_contract.recertification.cadence_days",
                    "Must be a positive integer.",
                )
            )
        _require_list(
            recertification,
            "required_reviewers",
            issues,
            "escalation_contract.recertification",
        )

    if eval_cases_path is not None and Path(eval_cases_path).is_file():
        cases = load_eval_cases(eval_cases_path)
        case_ids = {str(case.get("id", "")).strip() for case in cases}
        for index, case_id in enumerate(required_slices):
            if not isinstance(case_id, str) or not case_id.strip():
                issues.append(
                    ValidationIssue(
                        f"escalation_contract.evaluation.required_eval_slices[{index}]",
                        "Must be a non-empty eval case id.",
                    )
                )
            elif case_id not in case_ids:
                issues.append(
                    ValidationIssue(
                        f"escalation_contract.evaluation.required_eval_slices[{index}]",
                        f"Unknown eval case id: {case_id}.",
                    )
                )
        issues.extend(_validate_case_handoff_references(cases, triggers, destinations))

    return EscalationContractValidationResult(
        not issues,
        issues,
        len(trigger_ids),
        len(destination_ids),
    )


def summarize_escalation_contract(path: str | Path) -> EscalationContractSummary:
    """Summarize contract coverage for the generated launch report."""

    contract_path = Path(path)
    if not contract_path.is_file():
        return EscalationContractSummary(
            False, False, None, 0, 0, [], [], None, None, None, None, None, 0
        )

    validation = validate_escalation_contract(contract_path)
    try:
        contract = load_escalation_contract(contract_path)
    except Exception:  # noqa: BLE001 - invalid contract still gets a report summary.
        return EscalationContractSummary(
            True, False, None, 0, 0, [], [], None, None, None, None, None, 0
        )

    workflow = contract.get("workflow", {})
    destinations = _routing_destinations(contract, [])
    destination_ids = [
        str(destination.get("id", "")).strip()
        for destination in destinations
        if isinstance(destination, dict) and str(destination.get("id", "")).strip()
    ]
    durable_state = contract.get("durable_state", {})
    evaluation = contract.get("evaluation", {})
    return EscalationContractSummary(
        present=True,
        valid=validation.valid,
        workflow_id=str(workflow.get("id", "")).strip() or None
        if isinstance(workflow, dict)
        else None,
        trigger_count=validation.trigger_count,
        destination_count=validation.destination_count,
        destinations=destination_ids,
        handoff_types=sorted(
            {
                str(destination.get("handoff_type", "")).strip()
                for destination in destinations
                if isinstance(destination, dict)
                and str(destination.get("handoff_type", "")).strip()
            }
        ),
        sla_coverage=_coverage(destinations, "sla_minutes"),
        fallback_coverage=_coverage(destinations, "fallback"),
        checkpoint_required=durable_state.get("checkpoint_required")
        if isinstance(durable_state, dict)
        else None,
        idempotency_required=durable_state.get("idempotency_key_required")
        if isinstance(durable_state, dict)
        else None,
        resume_behavior_defined=(
            bool(str(durable_state.get("resume_behavior", "")).strip())
            if isinstance(durable_state, dict)
            else None
        ),
        required_eval_slice_count=(
            len(evaluation.get("required_eval_slices", []))
            if isinstance(evaluation, dict)
            and isinstance(evaluation.get("required_eval_slices"), list)
            else 0
        ),
    )


def _routing_destinations(
    contract: dict[str, Any],
    issues: list[ValidationIssue],
) -> list[Any]:
    routing = contract.get("routing")
    if not isinstance(routing, dict):
        issues.append(ValidationIssue("escalation_contract.routing", "Required object is missing."))
        return []
    destinations = routing.get("destinations")
    if not isinstance(destinations, list):
        issues.append(
            ValidationIssue(
                "escalation_contract.routing.destinations",
                "Must be a list.",
            )
        )
        return []
    return destinations


def _validate_destinations(
    destinations: list[Any],
    issues: list[ValidationIssue],
) -> set[str]:
    destination_ids: set[str] = set()
    for index, destination in enumerate(destinations):
        path = f"escalation_contract.routing.destinations[{index}]"
        if not isinstance(destination, dict):
            issues.append(ValidationIssue(path, "Destination must be an object."))
            continue
        destination_id = destination.get("id")
        if not isinstance(destination_id, str) or not destination_id.strip():
            issues.append(ValidationIssue(f"{path}.id", "Must be a non-empty string."))
        elif destination_id in destination_ids:
            issues.append(
                ValidationIssue(f"{path}.id", f"Duplicate destination id: {destination_id}.")
            )
        else:
            destination_ids.add(destination_id)
        handoff_type = destination.get("handoff_type")
        if handoff_type not in HANDOFF_TYPES:
            issues.append(
                ValidationIssue(
                    f"{path}.handoff_type",
                    f"Must be one of: {', '.join(sorted(HANDOFF_TYPES))}.",
                )
            )
        sla = destination.get("sla_minutes")
        if not isinstance(sla, int) or sla <= 0:
            issues.append(ValidationIssue(f"{path}.sla_minutes", "Must be a positive integer."))
        _require_non_empty_string(destination, "fallback", issues, path)
        _require_non_empty_string(destination, "owner", issues, path)
    return destination_ids


def _validate_triggers(
    triggers: Any,
    destination_ids: set[str],
    issues: list[ValidationIssue],
) -> set[str]:
    if not isinstance(triggers, list):
        issues.append(ValidationIssue("escalation_contract.triggers", "Must be a list."))
        return set()
    trigger_ids: set[str] = set()
    for index, trigger in enumerate(triggers):
        path = f"escalation_contract.triggers[{index}]"
        if not isinstance(trigger, dict):
            issues.append(ValidationIssue(path, "Trigger must be an object."))
            continue
        trigger_id = trigger.get("id")
        if not isinstance(trigger_id, str) or not trigger_id.strip():
            issues.append(ValidationIssue(f"{path}.id", "Must be a non-empty string."))
        elif trigger_id in trigger_ids:
            issues.append(ValidationIssue(f"{path}.id", f"Duplicate trigger id: {trigger_id}."))
        else:
            trigger_ids.add(trigger_id)
        _require_non_empty_string(trigger, "condition", issues, path)
        boundary_path = trigger.get("path")
        if boundary_path not in BOUNDARY_PATHS:
            issues.append(
                ValidationIssue(
                    f"{path}.path",
                    f"Must be one of: {', '.join(sorted(BOUNDARY_PATHS))}.",
                )
            )
        destination = trigger.get("destination")
        if boundary_path in {"escalate", "approval"}:
            if not isinstance(destination, str) or not destination.strip():
                issues.append(
                    ValidationIssue(
                        f"{path}.destination",
                        "Escalation and approval triggers require a destination.",
                    )
                )
            elif destination not in destination_ids:
                issues.append(
                    ValidationIssue(
                        f"{path}.destination",
                        f"Unknown destination id: {destination}.",
                    )
                )
    return trigger_ids


def _validate_case_handoff_references(
    cases: list[dict[str, Any]],
    triggers: Any,
    destinations: list[Any],
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    trigger_map = (
        {
            str(trigger.get("id", "")).strip(): trigger
            for trigger in triggers
            if isinstance(trigger, dict) and str(trigger.get("id", "")).strip()
        }
        if isinstance(triggers, list)
        else {}
    )
    destination_map = {
        str(destination.get("id", "")).strip(): destination
        for destination in destinations
        if isinstance(destination, dict) and str(destination.get("id", "")).strip()
    }
    for index, case in enumerate(cases):
        handoff = case.get("expected_handoff")
        if not isinstance(handoff, dict):
            continue
        trigger_id = handoff.get("trigger_id")
        destination = handoff.get("destination")
        if trigger_id not in trigger_map:
            issues.append(
                ValidationIssue(
                    f"case[{index}].expected_handoff.trigger_id",
                    f"Unknown escalation trigger id: {trigger_id}.",
                )
            )
        if destination not in destination_map:
            issues.append(
                ValidationIssue(
                    f"case[{index}].expected_handoff.destination",
                    f"Unknown escalation destination id: {destination}.",
                )
            )
        trigger = trigger_map.get(trigger_id)
        if trigger is not None and trigger.get("destination") != destination:
            issues.append(
                ValidationIssue(
                    f"case[{index}].expected_handoff.destination",
                    f"Trigger {trigger_id} routes to {trigger.get('destination')}, not {destination}.",
                )
            )
        destination_contract = destination_map.get(destination)
        if destination_contract is not None and destination_contract.get(
            "handoff_type"
        ) != handoff.get("handoff_type"):
            issues.append(
                ValidationIssue(
                    f"case[{index}].expected_handoff.handoff_type",
                    (
                        f"Destination {destination} uses handoff_type "
                        f"{destination_contract.get('handoff_type')}."
                    ),
                )
            )
    return issues


def _has_approval_path(triggers: Any, boundaries: Any) -> bool:
    if isinstance(triggers, list) and any(
        isinstance(trigger, dict) and trigger.get("path") == "approval" for trigger in triggers
    ):
        return True
    return (
        isinstance(boundaries, dict)
        and isinstance(boundaries.get("approval_required_when"), list)
        and bool(boundaries["approval_required_when"])
    )


def _require_non_empty_string(
    value: dict[str, Any],
    field: str,
    issues: list[ValidationIssue],
    path: str,
) -> None:
    if not isinstance(value.get(field), str) or not value[field].strip():
        issues.append(ValidationIssue(f"{path}.{field}", "Must be a non-empty string."))


def _require_list(
    value: dict[str, Any],
    field: str,
    issues: list[ValidationIssue],
    path: str,
) -> None:
    if not isinstance(value.get(field), list):
        issues.append(ValidationIssue(f"{path}.{field}", "Must be a list."))


def _coverage(destinations: list[Any], field: str) -> float | None:
    valid_destinations = [item for item in destinations if isinstance(item, dict)]
    if not valid_destinations:
        return None
    if field == "sla_minutes":
        covered = sum(
            1
            for destination in valid_destinations
            if isinstance(destination.get(field), int) and destination[field] > 0
        )
    else:
        covered = sum(
            1
            for destination in valid_destinations
            if isinstance(destination.get(field), str) and destination[field].strip()
        )
    return covered / len(valid_destinations)
