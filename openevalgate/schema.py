"""Golden eval case schema validation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum
from pathlib import Path
from typing import Any

import yaml


CASE_TYPES = {
    "historical_production",
    "synthetic_boundary",
    "fresh_drift_sample",
    "adversarial",
    "regression",
}

RISK_TIERS = {"low", "medium", "high", "prohibited"}
EXPECTED_ROUTES = {"show", "revise", "escalate", "block"}
WORKFLOW_ROUTES = {"answer", "clarify", "act", "approval", "escalate", "refuse"}
BOUNDARY_VARIATION_TYPES = {
    "anchor",
    "threshold_neighbor",
    "missing_fact",
    "conflicting_evidence",
    "authority_state",
    "semantic_invariance",
}
HANDOFF_TYPES = {
    "conversation_handoff",
    "async_case",
    "approval",
    "specialist_routing",
}


class RiskTier(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    PROHIBITED = "prohibited"


class ExpectedRoute(str, Enum):
    SHOW = "show"
    REVISE = "revise"
    ESCALATE = "escalate"
    BLOCK = "block"


class WorkflowRoute(str, Enum):
    ANSWER = "answer"
    CLARIFY = "clarify"
    ACT = "act"
    APPROVAL = "approval"
    ESCALATE = "escalate"
    REFUSE = "refuse"


class LaunchGateStatus(str, Enum):
    PASS = "pass"
    PARTIAL = "partial"
    FAIL = "fail"
    NOT_APPLICABLE = "not_applicable"


class ReadinessCategory(str, Enum):
    SCOPE_READINESS = "scope_readiness"
    TRUST_PRESERVATION_READINESS = "trust_preservation_readiness"
    BUSINESS_BEHAVIOR_CONTRACT_READINESS = "business_behavior_contract_readiness"
    GOLDEN_EVAL_READINESS = "golden_eval_readiness"
    TAIL_RISK_P0_FAILURE_READINESS = "tail_risk_p0_failure_readiness"
    MODEL_SELECTION_ARENA_READINESS = "model_selection_arena_readiness"
    GROUNDING_READINESS = "grounding_readiness"
    SOP_POLICY_COMPILATION_READINESS = "sop_policy_compilation_readiness"
    TOOL_ACTION_SAFETY_READINESS = "tool_action_safety_readiness"
    AUTOMATION_BOUNDARY_READINESS = "automation_boundary_readiness"
    HUMAN_ESCALATION_READINESS = "human_escalation_readiness"
    INPUT_OUTPUT_PERIMETER_READINESS = "input_output_perimeter_readiness"
    DOMAIN_OWNER_FEEDBACK_LOOP_READINESS = "domain_owner_feedback_loop_readiness"
    OBSERVABILITY_READINESS = "observability_readiness"
    COST_LATENCY_READINESS = "cost_latency_readiness"
    JOURNEY_BUSINESS_METRICS_READINESS = "journey_business_metrics_readiness"

REQUIRED_FIELDS = [
    "id",
    "assistant_type",
    "use_case",
    "case_type",
    "user_input",
    "user_context",
    "retrieved_context",
    "risk_tier",
    "expected_behavior",
    "unacceptable_behavior",
    "expected_tool_behavior",
    "expected_route",
    "grading_rubric",
    "production_frequency",
    "policy_reference",
    "owner",
    "last_reviewed",
]


@dataclass(frozen=True)
class ValidationIssue:
    """A schema or project validation issue."""

    path: str
    message: str


@dataclass(frozen=True)
class ValidationResult:
    """Validation result with issues and normalized case count."""

    valid: bool
    issues: list[ValidationIssue]
    case_count: int = 0


@dataclass(frozen=True)
class GoldenEvalCase:
    id: str
    assistant_type: str
    use_case: str
    case_type: str
    risk_tier: RiskTier
    expected_route: ExpectedRoute


@dataclass(frozen=True)
class HardBlocker:
    id: str
    reason: str
    evidence: str


@dataclass(frozen=True)
class LaunchReadinessReport:
    system_name: str
    assistant_type: str
    score: int
    recommendation: str
    hard_blockers: list[HardBlocker]


@dataclass(frozen=True)
class LaunchAssessment:
    """Independent evidence, behavior, control, and launch determinations."""

    evidence_completeness_score: int
    evidence_band: str
    evidence_package_sufficient: bool
    behavioral_evidence_state: str
    critical_control_status: str
    maximum_permitted_stage: str
    recommendation: str
    recommended_next_action: str
    hard_blockers: list[HardBlocker]


@dataclass(frozen=True)
class BusinessBehaviorContract:
    system_name: str
    business_owner: str
    policy_owner: str
    operations_owner: str


@dataclass(frozen=True)
class DomainOwnerFeedback:
    domain_area: str
    domain_owner: str
    risk_tier: RiskTier
    status: str


@dataclass(frozen=True)
class P0FailureMode:
    failure_mode_id: str
    risk_tier: RiskTier
    prevented_by: str
    escalated_by: str
    blocked_by: str


@dataclass(frozen=True)
class AutomationBoundaryRule:
    risk_level: RiskTier
    confidence_level: str
    action_route: str
    required_controls: str


@dataclass(frozen=True)
class ChatbotMetricStack:
    efficiency_metrics: list[str]
    quality_metrics: list[str]
    journey_metrics: list[str]
    business_trust_metrics: list[str]


def load_eval_cases(path: str | Path) -> list[dict[str, Any]]:
    """Load eval cases from a supported YAML shape."""

    with Path(path).open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)

    if data is None:
        return []
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "eval_cases" in data:
        cases = data["eval_cases"]
        if isinstance(cases, list):
            return cases
        raise ValueError("eval_cases must be a list")
    if isinstance(data, dict):
        return [data]
    raise ValueError("YAML must be an eval case, a list, or an object with eval_cases")


def validate_eval_cases(path: str | Path) -> ValidationResult:
    """Validate a golden eval YAML file."""

    issues: list[ValidationIssue] = []
    try:
        cases = load_eval_cases(path)
    except Exception as exc:  # noqa: BLE001 - CLI should report parser errors cleanly.
        return ValidationResult(False, [ValidationIssue(str(path), str(exc))], 0)

    if not cases:
        issues.append(ValidationIssue(str(path), "No eval cases found."))
        return ValidationResult(False, issues, 0)

    for index, case in enumerate(cases):
        case_path = f"case[{index}]"
        if not isinstance(case, dict):
            issues.append(ValidationIssue(case_path, "Eval case must be an object."))
            continue
        issues.extend(_validate_case(case, case_path))

    issues.extend(_validate_case_relationships(cases))
    return ValidationResult(not issues, issues, len(cases))


def _validate_case(case: dict[str, Any], case_path: str) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    for field in REQUIRED_FIELDS:
        if field not in case:
            issues.append(ValidationIssue(f"{case_path}.{field}", "Required field is missing."))

    if "case_type" in case and case["case_type"] not in CASE_TYPES:
        issues.append(
            ValidationIssue(
                f"{case_path}.case_type",
                f"Must be one of: {', '.join(sorted(CASE_TYPES))}.",
            )
        )

    if "risk_tier" in case and case["risk_tier"] not in RISK_TIERS:
        issues.append(
            ValidationIssue(
                f"{case_path}.risk_tier",
                f"Must be one of: {', '.join(sorted(RISK_TIERS))}.",
            )
        )

    if "expected_route" in case and case["expected_route"] not in EXPECTED_ROUTES:
        issues.append(
            ValidationIssue(
                f"{case_path}.expected_route",
                f"Must be one of: {', '.join(sorted(EXPECTED_ROUTES))}.",
            )
        )

    if "expected_workflow_route" in case and case["expected_workflow_route"] not in WORKFLOW_ROUTES:
        issues.append(
            ValidationIssue(
                f"{case_path}.expected_workflow_route",
                f"Must be one of: {', '.join(sorted(WORKFLOW_ROUTES))}.",
            )
        )

    _require_type(case, "expected_behavior", list, issues, case_path)
    _require_type(case, "unacceptable_behavior", list, issues, case_path)
    _require_type(case, "user_context", dict, issues, case_path)
    _require_type(case, "retrieved_context", dict, issues, case_path)
    _require_type(case, "expected_tool_behavior", dict, issues, case_path)
    _require_type(case, "grading_rubric", dict, issues, case_path)
    _require_type(case, "boundary", dict, issues, case_path)
    _require_type(case, "expected_trajectory", dict, issues, case_path)
    _require_type(case, "expected_end_state", dict, issues, case_path)
    _require_type(case, "expected_handoff", dict, issues, case_path)

    tool_behavior = case.get("expected_tool_behavior")
    if isinstance(tool_behavior, dict):
        for key in ("allowed_tools", "blocked_tools"):
            if key in tool_behavior and not isinstance(tool_behavior[key], list):
                issues.append(ValidationIssue(f"{case_path}.expected_tool_behavior.{key}", "Must be a list."))

    rubric = case.get("grading_rubric")
    if isinstance(rubric, dict):
        for name, value in rubric.items():
            if not isinstance(value, int) or not 1 <= value <= 5:
                issues.append(ValidationIssue(f"{case_path}.grading_rubric.{name}", "Must be an integer from 1 to 5."))

    boundary = case.get("boundary")
    if isinstance(boundary, dict):
        required_boundary_fields = (
            "family_id",
            "anchor_case_id",
            "controlling_fact",
            "variation_type",
            "before_value",
            "after_value",
        )
        for field in required_boundary_fields:
            if field not in boundary:
                issues.append(ValidationIssue(f"{case_path}.boundary.{field}", "Required boundary field is missing."))
        for field in ("family_id", "anchor_case_id", "controlling_fact"):
            if field in boundary and (not isinstance(boundary[field], str) or not boundary[field].strip()):
                issues.append(ValidationIssue(f"{case_path}.boundary.{field}", "Must be a non-empty string."))
        variation_type = boundary.get("variation_type")
        if variation_type is not None and variation_type not in BOUNDARY_VARIATION_TYPES:
            issues.append(
                ValidationIssue(
                    f"{case_path}.boundary.variation_type",
                    f"Must be one of: {', '.join(sorted(BOUNDARY_VARIATION_TYPES))}.",
                )
            )

    trajectory = case.get("expected_trajectory")
    if isinstance(trajectory, dict):
        for field in ("required_events", "prohibited_events"):
            if field not in trajectory:
                issues.append(ValidationIssue(f"{case_path}.expected_trajectory.{field}", "Required trajectory field is missing."))
            elif not isinstance(trajectory[field], list):
                issues.append(ValidationIssue(f"{case_path}.expected_trajectory.{field}", "Must be a list."))

    end_state = case.get("expected_end_state")
    if isinstance(end_state, dict):
        if "assertions" not in end_state:
            issues.append(ValidationIssue(f"{case_path}.expected_end_state.assertions", "Required end-state field is missing."))
        elif not isinstance(end_state["assertions"], list):
            issues.append(ValidationIssue(f"{case_path}.expected_end_state.assertions", "Must be a list."))

    handoff = case.get("expected_handoff")
    if isinstance(handoff, dict):
        workflow_route = case.get("expected_workflow_route")
        if workflow_route not in {"approval", "escalate"}:
            issues.append(
                ValidationIssue(
                    f"{case_path}.expected_handoff",
                    "Expected handoff requires expected_workflow_route: approval or escalate.",
                )
            )
        for field in ("trigger_id", "destination", "fallback", "resume_behavior"):
            if not isinstance(handoff.get(field), str) or not handoff[field].strip():
                issues.append(
                    ValidationIssue(
                        f"{case_path}.expected_handoff.{field}",
                        "Must be a non-empty string.",
                    )
                )
        handoff_type = handoff.get("handoff_type")
        if handoff_type not in HANDOFF_TYPES:
            issues.append(
                ValidationIssue(
                    f"{case_path}.expected_handoff.handoff_type",
                    f"Must be one of: {', '.join(sorted(HANDOFF_TYPES))}.",
                )
            )
        if not isinstance(handoff.get("required_payload_fields"), list):
            issues.append(
                ValidationIssue(
                    f"{case_path}.expected_handoff.required_payload_fields",
                    "Must be a list.",
                )
            )

    if "last_reviewed" in case:
        reviewed = case["last_reviewed"]
        if isinstance(reviewed, date):
            pass
        elif isinstance(reviewed, str):
            try:
                date.fromisoformat(reviewed)
            except ValueError:
                issues.append(ValidationIssue(f"{case_path}.last_reviewed", "Must use YYYY-MM-DD format."))
        else:
            issues.append(ValidationIssue(f"{case_path}.last_reviewed", "Must use YYYY-MM-DD format."))

    return issues


def _validate_case_relationships(cases: list[dict[str, Any]]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    case_by_id: dict[str, tuple[int, dict[str, Any]]] = {}

    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            continue
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id.strip():
            continue
        if case_id in case_by_id:
            issues.append(ValidationIssue(f"case[{index}].id", f"Duplicate eval case id: {case_id}."))
        else:
            case_by_id[case_id] = (index, case)

    for index, case in enumerate(cases):
        if not isinstance(case, dict) or not isinstance(case.get("boundary"), dict):
            continue
        boundary = case["boundary"]
        case_id = case.get("id")
        anchor_case_id = boundary.get("anchor_case_id")
        family_id = boundary.get("family_id")
        if not isinstance(anchor_case_id, str) or not anchor_case_id.strip():
            continue
        anchor_entry = case_by_id.get(anchor_case_id)
        if anchor_entry is None:
            issues.append(
                ValidationIssue(
                    f"case[{index}].boundary.anchor_case_id",
                    f"Unknown boundary anchor case id: {anchor_case_id}.",
                )
            )
            continue
        _, anchor_case = anchor_entry
        anchor_boundary = anchor_case.get("boundary")
        if not isinstance(anchor_boundary, dict):
            issues.append(
                ValidationIssue(
                    f"case[{index}].boundary.anchor_case_id",
                    f"Boundary anchor {anchor_case_id} must also define boundary metadata.",
                )
            )
            continue
        if family_id and anchor_boundary.get("family_id") != family_id:
            issues.append(
                ValidationIssue(
                    f"case[{index}].boundary.family_id",
                    f"Boundary anchor {anchor_case_id} belongs to a different family.",
                )
            )
        if anchor_boundary.get("variation_type") != "anchor":
            issues.append(
                ValidationIssue(
                    f"case[{index}].boundary.anchor_case_id",
                    f"Boundary anchor {anchor_case_id} must use variation_type: anchor.",
                )
            )
        if boundary.get("variation_type") == "anchor" and anchor_case_id != case_id:
            issues.append(
                ValidationIssue(
                    f"case[{index}].boundary.anchor_case_id",
                    "An anchor case must reference its own case id.",
                )
            )

    return issues


def _require_type(
    case: dict[str, Any],
    field: str,
    expected_type: type,
    issues: list[ValidationIssue],
    case_path: str,
) -> None:
    if field in case and not isinstance(case[field], expected_type):
        issues.append(ValidationIssue(f"{case_path}.{field}", f"Must be a {expected_type.__name__}."))
