"""Project-level orchestration across validation and hard-gate policy."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from openevalgate.action_risk import (
    ALLOWED_BOOLEAN_VALUES,
    HIGH_IMPACT_ACTION_RISK_TIERS,
    ActionRiskRow,
)
from openevalgate.escalation import validate_escalation_contract
from openevalgate.eval_results import classify_behavioral_evidence, read_eval_results
from openevalgate.hard_gate_policy import (
    HardGateContext,
    HardGateEvaluation,
    HardGateEvidence,
    evaluate_hard_gate_policy,
)
from openevalgate.launch_gate_review import LaunchGateReview
from openevalgate.routing import validate_routing_policy
from openevalgate.schema import (
    HardBlocker,
    ValidationIssue,
    load_eval_cases,
    validate_eval_cases,
)
from openevalgate.validator import ProjectCheckResult, check_project


@dataclass(frozen=True)
class ProjectInspection:
    check: ProjectCheckResult
    launch_gate_review: LaunchGateReview
    context: HardGateContext
    evidence: HardGateEvidence
    evaluations: list[HardGateEvaluation]
    policy_issues: list[ValidationIssue]
    hard_blockers: list[HardBlocker]

    @property
    def valid(self) -> bool:
        """Whether artifacts and declarations are structurally usable."""

        return self.check.valid and not self.policy_issues

    @property
    def launch_blocked(self) -> bool:
        """Whether hard-gate policy prevents advancement."""

        return bool(self.hard_blockers)


def inspect_project(project_dir: str | Path) -> ProjectInspection:
    """Compose structural validation and policy evaluation without conflating them."""

    root = Path(project_dir)
    check = check_project(root)
    review = check.launch_gate_review
    cases, eval_valid = _validated_eval_cases(root / "eval_cases.yaml")
    action_review = check.action_risk_review

    eval_high_impact = (
        any(
            str(case.get("risk_tier", "")).lower()
            in {"high", "prohibited"}
            for case in cases
        )
        if eval_valid
        else None
    )
    action_high_impact = (
        any(
            row.get("risk_tier", "").lower()
            in HIGH_IMPACT_ACTION_RISK_TIERS
            for row in action_review.rows
        )
        if action_review.valid
        else None
    )
    high_impact = _combine_positive_context(
        eval_high_impact,
        action_high_impact,
    )
    has_tool_actions = (
        any(row.get("action", "").strip() for row in action_review.rows)
        if action_review.valid
        else None
    )
    context = HardGateContext(high_impact, has_tool_actions)
    evidence = HardGateEvidence(
        scope_evidence_valid=(root / "assistant_prd.md").is_file(),
        golden_eval_evidence_valid=eval_valid,
        tail_risk_evidence_valid=(
            root / "p0_failure_mode_checklist.md"
        ).is_file(),
        tool_action_evidence_valid=action_review.valid,
        escalation_evidence_valid=(
            root / "human_escalation_design.md"
        ).is_file(),
    )
    evaluations = evaluate_hard_gate_policy(
        review,
        context,
        evidence,
    )
    policy_issues = [
        evaluation.policy_issue
        for evaluation in evaluations
        if evaluation.policy_issue is not None
    ]
    policy_blockers = [
        evaluation.blocker
        for evaluation in evaluations
        if evaluation.blocker is not None
    ]
    independent_blockers = _evaluate_independent_blockers(
        root,
        check,
        cases,
    )
    hard_blockers = _deduplicate_blockers(
        [*policy_blockers, *independent_blockers]
    )
    return ProjectInspection(
        check,
        review,
        context,
        evidence,
        evaluations,
        policy_issues,
        hard_blockers,
    )


def _validated_eval_cases(
    path: Path,
) -> tuple[list[dict[str, Any]], bool]:
    if not path.is_file():
        return [], False
    validation = validate_eval_cases(path)
    if not validation.valid:
        return [], False
    return load_eval_cases(path), True


def _combine_positive_context(
    first: bool | None,
    second: bool | None,
) -> bool | None:
    if first is True or second is True:
        return True
    if first is False and second is False:
        return False
    return None


def _evaluate_independent_blockers(
    root: Path,
    check: ProjectCheckResult,
    cases: list[dict[str, Any]],
) -> list[HardBlocker]:
    blockers: list[HardBlocker] = []

    unsafe_actions = _high_risk_actions_without_controls(
        check.action_risk_review.rows
        if check.action_risk_review.valid
        else []
    )
    if unsafe_actions:
        blockers.append(
            HardBlocker(
                "ungated_high_risk_action",
                "High-risk action lacks deterministic enforcement or human approval.",
                ", ".join(unsafe_actions),
            )
        )

    escalation_contract = root / "escalation_contract.yaml"
    if escalation_contract.is_file():
        validation = validate_escalation_contract(
            escalation_contract,
            root / "eval_cases.yaml",
        )
        if not validation.valid:
            blockers.append(
                HardBlocker(
                    "invalid_escalation_contract",
                    "Structured escalation contract is invalid.",
                    "escalation_contract.yaml",
                )
            )

    behavioral_evidence = classify_behavioral_evidence(root)
    if behavioral_evidence.state == "available":
        critical_failures = _critical_escalation_failures(root, cases)
        if critical_failures:
            blockers.append(
                HardBlocker(
                    "critical_escalation_regression",
                    (
                        "High-risk escalation evidence contains under-escalation, "
                        "wrong-destination, payload, or resume failures."
                    ),
                    ", ".join(critical_failures),
                )
            )

    routing_policy = root / "routing_policy.yaml"
    if routing_policy.is_file():
        validation = validate_routing_policy(
            routing_policy,
            root / "eval_cases.yaml",
        )
        if not validation.valid:
            blockers.append(
                HardBlocker(
                    "invalid_routing_policy",
                    "Structured routing policy is invalid.",
                    "routing_policy.yaml",
                )
            )
    return blockers


def _high_risk_actions_without_controls(
    rows: list[ActionRiskRow],
) -> list[str]:
    unsafe: list[str] = []
    for row in rows:
        if (
            row.get("risk_tier", "").lower()
            not in HIGH_IMPACT_ACTION_RISK_TIERS
        ):
            continue
        deterministic_gate = row.get("deterministic_gate", "").lower()
        human_review = row.get("human_review_required", "").lower()
        has_gate = deterministic_gate not in {
            "",
            "-",
            "none",
            "n/a",
            "na",
        }
        has_review = (
            human_review in ALLOWED_BOOLEAN_VALUES
            and human_review == "true"
        )
        if not has_gate and not has_review:
            unsafe.append(row.get("action", "") or "unknown_action")
    return unsafe


def _critical_escalation_failures(
    root: Path,
    cases: list[dict[str, Any]],
) -> list[str]:
    high_risk_handoff_cases = {
        str(case.get("id", "")).strip()
        for case in cases
        if str(case.get("risk_tier", "")).lower()
        in {"high", "prohibited"}
        and isinstance(case.get("expected_handoff"), dict)
    }
    failures: set[str] = set()
    for row in read_eval_results(root / "eval_results.csv"):
        case_id = row.get("case_id", "").strip()
        if case_id not in high_risk_handoff_cases:
            continue
        failed_control = (
            row.get("workflow_route_match", "").strip().lower() == "false"
            or (
                not row.get("workflow_route_match", "").strip()
                and row.get("route_match", "").strip().lower() == "false"
            )
            or row.get("destination_match", "").strip().lower() == "false"
            or row.get("payload_complete", "").strip().lower() == "false"
            or row.get("resume_success", "").strip().lower() == "false"
        )
        if failed_control:
            failures.add(case_id)
    return sorted(failures)


def _deduplicate_blockers(
    blockers: list[HardBlocker],
) -> list[HardBlocker]:
    seen: set[str] = set()
    result: list[HardBlocker] = []
    for blocker in blockers:
        if blocker.id in seen:
            continue
        seen.add(blocker.id)
        result.append(blocker)
    return result
