"""Structured workflow and subagent capability-allocation policy support."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import yaml

from openevalgate.schema import RISK_TIERS, ValidationIssue, load_eval_cases


WORKFLOW_KINDS = {"subagent", "deterministic", "human"}
ASSIGNMENT_MODES = {"fixed", "adaptive", "none"}
CAPABILITY_TIERS = {"small", "balanced", "strong", "frontier", "specialized"}
REASONING_LEVELS = {"none", "low", "medium", "high"}
REQUIRED_OBSERVABILITY_FIELDS = {
    "workflow_id",
    "routing_policy_version",
    "routing_reason",
}


@dataclass(frozen=True)
class RoutingPolicyValidationResult:
    valid: bool
    issues: list[ValidationIssue]
    model_count: int = 0
    workflow_count: int = 0


@dataclass(frozen=True)
class RoutingPolicySummary:
    present: bool
    valid: bool
    policy_id: str | None
    version: str | None
    model_count: int
    workflow_count: int
    subagent_count: int
    deterministic_count: int
    human_count: int
    fixed_count: int
    adaptive_count: int
    no_model_count: int
    fallback_coverage: float | None
    eval_coverage: float | None
    high_risk_control_coverage: float | None
    rollback_defined: bool | None


def load_routing_policy(path: str | Path) -> dict[str, Any]:
    """Load the supported wrapped routing-policy YAML shape."""

    with Path(path).open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict) or not isinstance(data.get("routing_policy"), dict):
        raise ValueError("YAML must contain a routing_policy object")
    return data["routing_policy"]


def validate_routing_policy(
    path: str | Path,
    eval_cases_path: str | Path | None = None,
) -> RoutingPolicyValidationResult:
    """Validate an optional routing policy and its eval-case references."""

    policy_path = Path(path)
    issues: list[ValidationIssue] = []
    try:
        policy = load_routing_policy(policy_path)
    except Exception as exc:  # noqa: BLE001 - CLI validation should report parser errors.
        return RoutingPolicyValidationResult(
            False,
            [ValidationIssue(str(policy_path), str(exc))],
        )

    metadata = policy.get("metadata")
    if not isinstance(metadata, dict):
        issues.append(ValidationIssue("routing_policy.metadata", "Required object is missing."))
    else:
        for field in ("id", "version", "owner", "last_reviewed"):
            _require_non_empty_string(metadata, field, issues, "routing_policy.metadata")
        reviewed = metadata.get("last_reviewed")
        if isinstance(reviewed, date):
            pass
        elif isinstance(reviewed, str):
            try:
                date.fromisoformat(reviewed)
            except ValueError:
                issues.append(
                    ValidationIssue(
                        "routing_policy.metadata.last_reviewed",
                        "Must use YYYY-MM-DD format.",
                    )
                )

    models = policy.get("models")
    model_ids = _validate_models(models, issues)
    workflows = policy.get("workflows")
    workflow_ids = _validate_workflows(workflows, model_ids, issues)

    observability = policy.get("observability")
    if not isinstance(observability, dict):
        issues.append(ValidationIssue("routing_policy.observability", "Required object is missing."))
    else:
        required_fields = observability.get("required_fields")
        _require_list(observability, "required_fields", issues, "routing_policy.observability")
        if isinstance(required_fields, list):
            normalized = {
                str(field).strip()
                for field in required_fields
                if isinstance(field, str) and field.strip()
            }
            for field in sorted(REQUIRED_OBSERVABILITY_FIELDS - normalized):
                issues.append(
                    ValidationIssue(
                        "routing_policy.observability.required_fields",
                        f"Must include {field}.",
                    )
                )
            if any(
                isinstance(workflow, dict)
                and workflow.get("kind") == "subagent"
                for workflow in workflows or []
            ) and "model_id" not in normalized:
                issues.append(
                    ValidationIssue(
                        "routing_policy.observability.required_fields",
                        "Subagent policies must include model_id.",
                    )
                )

    rollback = policy.get("rollback")
    if not isinstance(rollback, dict):
        issues.append(ValidationIssue("routing_policy.rollback", "Required object is missing."))
    else:
        _require_non_empty_string(rollback, "owner", issues, "routing_policy.rollback")
        fallback_id = rollback.get("fallback_workflow_id")
        if not isinstance(fallback_id, str) or not fallback_id.strip():
            issues.append(
                ValidationIssue(
                    "routing_policy.rollback.fallback_workflow_id",
                    "Must be a non-empty string.",
                )
            )
        elif fallback_id not in workflow_ids:
            issues.append(
                ValidationIssue(
                    "routing_policy.rollback.fallback_workflow_id",
                    f"Unknown workflow id: {fallback_id}.",
                )
            )
        _require_list(rollback, "triggers", issues, "routing_policy.rollback")

    recertification = policy.get("recertification")
    if not isinstance(recertification, dict):
        issues.append(ValidationIssue("routing_policy.recertification", "Required object is missing."))
    else:
        cadence = recertification.get("cadence_days")
        if not isinstance(cadence, int) or cadence <= 0:
            issues.append(
                ValidationIssue(
                    "routing_policy.recertification.cadence_days",
                    "Must be a positive integer.",
                )
            )
        _require_list(
            recertification,
            "required_reviewers",
            issues,
            "routing_policy.recertification",
        )

    if eval_cases_path is not None and Path(eval_cases_path).is_file():
        cases = load_eval_cases(eval_cases_path)
        case_ids = {
            str(case.get("id", "")).strip()
            for case in cases
            if str(case.get("id", "")).strip()
        }
        referenced_cases: dict[str, str] = {}
        for index, workflow in enumerate(workflows or []):
            if not isinstance(workflow, dict):
                continue
            workflow_id = str(workflow.get("id", "")).strip()
            eval_cases = workflow.get("eval_cases", [])
            if not isinstance(eval_cases, list):
                continue
            for case_index, case_id in enumerate(eval_cases):
                path_prefix = f"routing_policy.workflows[{index}].eval_cases[{case_index}]"
                if not isinstance(case_id, str) or not case_id.strip():
                    issues.append(ValidationIssue(path_prefix, "Must be a non-empty eval case id."))
                elif case_id not in case_ids:
                    issues.append(ValidationIssue(path_prefix, f"Unknown eval case id: {case_id}."))
                elif case_id in referenced_cases:
                    issues.append(
                        ValidationIssue(
                            path_prefix,
                            f"Eval case {case_id} is already assigned to workflow {referenced_cases[case_id]}.",
                        )
                    )
                else:
                    referenced_cases[case_id] = workflow_id

    return RoutingPolicyValidationResult(
        not issues,
        issues,
        len(model_ids),
        len(workflow_ids),
    )


def summarize_routing_policy(path: str | Path) -> RoutingPolicySummary:
    """Summarize workflow and model-assignment coverage for launch reports."""

    policy_path = Path(path)
    if not policy_path.is_file():
        return RoutingPolicySummary(
            False, False, None, None, 0, 0, 0, 0, 0, 0, 0, 0, None, None, None, None
        )

    validation = validate_routing_policy(policy_path)
    try:
        policy = load_routing_policy(policy_path)
    except Exception:  # noqa: BLE001 - invalid policy still gets a report summary.
        return RoutingPolicySummary(
            True, False, None, None, 0, 0, 0, 0, 0, 0, 0, 0, None, None, None, None
        )

    metadata = policy.get("metadata", {})
    workflows = [
        workflow for workflow in policy.get("workflows", []) if isinstance(workflow, dict)
    ]
    assignments = [
        workflow.get("model_assignment", {})
        for workflow in workflows
        if isinstance(workflow.get("model_assignment"), dict)
    ]
    high_risk = [
        workflow
        for workflow in workflows
        if workflow.get("risk_tier") in {"high", "prohibited"}
    ]
    rollback = policy.get("rollback")
    return RoutingPolicySummary(
        present=True,
        valid=validation.valid,
        policy_id=str(metadata.get("id", "")).strip() or None,
        version=str(metadata.get("version", "")).strip() or None,
        model_count=len(
            [model for model in policy.get("models", []) if isinstance(model, dict)]
        ),
        workflow_count=len(workflows),
        subagent_count=sum(1 for workflow in workflows if workflow.get("kind") == "subagent"),
        deterministic_count=sum(
            1 for workflow in workflows if workflow.get("kind") == "deterministic"
        ),
        human_count=sum(1 for workflow in workflows if workflow.get("kind") == "human"),
        fixed_count=sum(1 for assignment in assignments if assignment.get("mode") == "fixed"),
        adaptive_count=sum(
            1 for assignment in assignments if assignment.get("mode") == "adaptive"
        ),
        no_model_count=sum(1 for assignment in assignments if assignment.get("mode") == "none"),
        fallback_coverage=_workflow_coverage(workflows, "fallback_workflow_id"),
        eval_coverage=_workflow_list_coverage(workflows, "eval_cases"),
        high_risk_control_coverage=_workflow_list_coverage(high_risk, "mandatory_controls"),
        rollback_defined=(
            isinstance(rollback, dict)
            and bool(str(rollback.get("owner", "")).strip())
            and bool(str(rollback.get("fallback_workflow_id", "")).strip())
            and isinstance(rollback.get("triggers"), list)
            and bool(rollback["triggers"])
        ),
    )


def routing_expectations(
    path: str | Path,
) -> tuple[str | None, dict[str, dict[str, Any]], dict[str, str]]:
    """Return policy version, workflows by id, and eval-case workflow assignments."""

    policy = load_routing_policy(path)
    metadata = policy.get("metadata", {})
    workflows = {
        str(workflow.get("id", "")).strip(): workflow
        for workflow in policy.get("workflows", [])
        if isinstance(workflow, dict) and str(workflow.get("id", "")).strip()
    }
    case_workflows: dict[str, str] = {}
    for workflow_id, workflow in workflows.items():
        for case_id in workflow.get("eval_cases", []):
            if isinstance(case_id, str) and case_id.strip():
                case_workflows[case_id.strip()] = workflow_id
    version = str(metadata.get("version", "")).strip() or None
    return version, workflows, case_workflows


def _validate_models(models: Any, issues: list[ValidationIssue]) -> set[str]:
    if not isinstance(models, list):
        issues.append(ValidationIssue("routing_policy.models", "Must be a list."))
        return set()
    model_ids: set[str] = set()
    for index, model in enumerate(models):
        path = f"routing_policy.models[{index}]"
        if not isinstance(model, dict):
            issues.append(ValidationIssue(path, "Model must be an object."))
            continue
        for field in ("id", "provider", "model_version"):
            _require_non_empty_string(model, field, issues, path)
        model_id = model.get("id")
        if isinstance(model_id, str) and model_id.strip():
            if model_id in model_ids:
                issues.append(ValidationIssue(f"{path}.id", f"Duplicate model id: {model_id}."))
            else:
                model_ids.add(model_id)
        if model.get("capability_tier") not in CAPABILITY_TIERS:
            issues.append(
                ValidationIssue(
                    f"{path}.capability_tier",
                    f"Must be one of: {', '.join(sorted(CAPABILITY_TIERS))}.",
                )
            )
    return model_ids


def _validate_workflows(
    workflows: Any,
    model_ids: set[str],
    issues: list[ValidationIssue],
) -> set[str]:
    if not isinstance(workflows, list):
        issues.append(ValidationIssue("routing_policy.workflows", "Must be a list."))
        return set()

    workflow_ids: set[str] = set()
    for index, workflow in enumerate(workflows):
        path = f"routing_policy.workflows[{index}]"
        if not isinstance(workflow, dict):
            issues.append(ValidationIssue(path, "Workflow must be an object."))
            continue
        for field in ("id", "name", "owner"):
            _require_non_empty_string(workflow, field, issues, path)
        workflow_id = workflow.get("id")
        if isinstance(workflow_id, str) and workflow_id.strip():
            if workflow_id in workflow_ids:
                issues.append(
                    ValidationIssue(f"{path}.id", f"Duplicate workflow id: {workflow_id}.")
                )
            else:
                workflow_ids.add(workflow_id)
        kind = workflow.get("kind")
        if kind not in WORKFLOW_KINDS:
            issues.append(
                ValidationIssue(
                    f"{path}.kind",
                    f"Must be one of: {', '.join(sorted(WORKFLOW_KINDS))}.",
                )
            )
        risk_tier = workflow.get("risk_tier")
        if risk_tier not in RISK_TIERS:
            issues.append(
                ValidationIssue(
                    f"{path}.risk_tier",
                    f"Must be one of: {', '.join(sorted(RISK_TIERS))}.",
                )
            )
        for field in ("scenarios", "mandatory_controls", "eval_cases"):
            _require_list(workflow, field, issues, path)
        if risk_tier in {"high", "prohibited"}:
            controls = workflow.get("mandatory_controls")
            if not isinstance(controls, list) or not controls:
                issues.append(
                    ValidationIssue(
                        f"{path}.mandatory_controls",
                        "High-risk and prohibited workflows require at least one control.",
                    )
                )
        assignment = workflow.get("model_assignment")
        _validate_assignment(assignment, kind, model_ids, issues, f"{path}.model_assignment")

    for index, workflow in enumerate(workflows):
        if not isinstance(workflow, dict):
            continue
        fallback = workflow.get("fallback_workflow_id")
        if not isinstance(fallback, str) or not fallback.strip():
            issues.append(
                ValidationIssue(
                    f"routing_policy.workflows[{index}].fallback_workflow_id",
                    "Must be a non-empty string.",
                )
            )
        elif fallback not in workflow_ids:
            issues.append(
                ValidationIssue(
                    f"routing_policy.workflows[{index}].fallback_workflow_id",
                    f"Unknown workflow id: {fallback}.",
                )
            )
        elif fallback == workflow.get("id"):
            issues.append(
                ValidationIssue(
                    f"routing_policy.workflows[{index}].fallback_workflow_id",
                    "Fallback workflow must differ from the workflow.",
                )
            )
    return workflow_ids


def _validate_assignment(
    assignment: Any,
    kind: Any,
    model_ids: set[str],
    issues: list[ValidationIssue],
    path: str,
) -> None:
    if not isinstance(assignment, dict):
        issues.append(ValidationIssue(path, "Required object is missing."))
        return
    mode = assignment.get("mode")
    if mode not in ASSIGNMENT_MODES:
        issues.append(
            ValidationIssue(
                f"{path}.mode",
                f"Must be one of: {', '.join(sorted(ASSIGNMENT_MODES))}.",
            )
        )
        return
    if kind == "subagent" and mode not in {"fixed", "adaptive"}:
        issues.append(ValidationIssue(f"{path}.mode", "Subagents require fixed or adaptive mode."))
    if kind in {"deterministic", "human"} and mode != "none":
        issues.append(
            ValidationIssue(
                f"{path}.mode",
                "Deterministic and human workflows require none mode.",
            )
        )

    approved = assignment.get("approved_models")
    if mode in {"fixed", "adaptive"}:
        if not isinstance(approved, list) or not approved:
            issues.append(ValidationIssue(f"{path}.approved_models", "Must be a non-empty list."))
            approved_ids: list[str] = []
        else:
            approved_ids = [
                model_id.strip()
                for model_id in approved
                if isinstance(model_id, str) and model_id.strip()
            ]
            for model_id in approved_ids:
                if model_id not in model_ids:
                    issues.append(
                        ValidationIssue(
                            f"{path}.approved_models",
                            f"Unknown model id: {model_id}.",
                        )
                    )
        default_model = assignment.get("default_model")
        if not isinstance(default_model, str) or not default_model.strip():
            issues.append(ValidationIssue(f"{path}.default_model", "Must be a non-empty string."))
        elif default_model not in approved_ids:
            issues.append(
                ValidationIssue(
                    f"{path}.default_model",
                    "Must reference one of approved_models.",
                )
            )
        if assignment.get("reasoning_level") not in REASONING_LEVELS - {"none"}:
            issues.append(
                ValidationIssue(
                    f"{path}.reasoning_level",
                    "Must be one of: high, low, medium.",
                )
            )
        if mode == "fixed" and len(set(approved_ids)) != 1:
            issues.append(
                ValidationIssue(
                    f"{path}.approved_models",
                    "Fixed mode requires exactly one approved model.",
                )
            )
        if mode == "adaptive":
            if len(set(approved_ids)) < 2:
                issues.append(
                    ValidationIssue(
                        f"{path}.approved_models",
                        "Adaptive mode requires at least two approved models.",
                    )
                )
            _require_non_empty_string(assignment, "selection_rule", issues, path)
    elif mode == "none":
        if assignment.get("reasoning_level") != "none":
            issues.append(ValidationIssue(f"{path}.reasoning_level", "None mode requires none."))
        if approved not in (None, []):
            issues.append(
                ValidationIssue(
                    f"{path}.approved_models",
                    "None mode cannot approve models.",
                )
            )
        if assignment.get("default_model") not in (None, ""):
            issues.append(
                ValidationIssue(
                    f"{path}.default_model",
                    "None mode cannot define a default model.",
                )
            )


def _require_non_empty_string(
    data: dict[str, Any],
    field: str,
    issues: list[ValidationIssue],
    path: str,
) -> None:
    if not isinstance(data.get(field), str) or not data[field].strip():
        issues.append(ValidationIssue(f"{path}.{field}", "Must be a non-empty string."))


def _require_list(
    data: dict[str, Any],
    field: str,
    issues: list[ValidationIssue],
    path: str,
) -> None:
    if not isinstance(data.get(field), list):
        issues.append(ValidationIssue(f"{path}.{field}", "Must be a list."))


def _workflow_coverage(workflows: list[dict[str, Any]], field: str) -> float | None:
    if not workflows:
        return None
    covered = sum(1 for workflow in workflows if str(workflow.get(field, "")).strip())
    return covered / len(workflows)


def _workflow_list_coverage(workflows: list[dict[str, Any]], field: str) -> float | None:
    if not workflows:
        return None
    covered = sum(
        1
        for workflow in workflows
        if isinstance(workflow.get(field), list) and bool(workflow[field])
    )
    return covered / len(workflows)
