"""Pure hard-gate policy semantics.

This module consumes normalized declarations and evidence facts. It does not
parse Markdown or read project files.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from openevalgate.launch_gate_review import (
    GateRow,
    LaunchGateReview,
    is_meaningful_evidence,
)
from openevalgate.schema import HardBlocker, ValidationIssue


Applicability = Literal["always", "high_impact", "tool_actions"]


@dataclass(frozen=True)
class HardGateRule:
    gate: str
    blocker_id: str
    applicability: Applicability
    artifact_field: str | None
    artifact_label: str


@dataclass(frozen=True)
class HardGateContext:
    high_impact: bool | None
    has_tool_actions: bool | None


@dataclass(frozen=True)
class HardGateEvidence:
    scope_evidence_valid: bool
    golden_eval_evidence_valid: bool
    tail_risk_evidence_valid: bool
    tool_action_evidence_valid: bool
    escalation_evidence_valid: bool


@dataclass(frozen=True)
class HardGateEvaluation:
    gate: str
    applicable: bool | None
    required_status: str
    actual_status: str
    outcome: str
    reason: str
    blocker: HardBlocker | None = None
    policy_issue: ValidationIssue | None = None


HARD_GATE_RULES = (
    HardGateRule(
        "scope gate",
        "missing_scope",
        "always",
        "scope_evidence_valid",
        "assistant_prd.md",
    ),
    HardGateRule(
        "golden eval gate",
        "missing_golden_eval",
        "always",
        "golden_eval_evidence_valid",
        "eval_cases.yaml",
    ),
    HardGateRule(
        "tail-risk / p0 failure mode gate",
        "missing_tail_risk_review",
        "high_impact",
        "tail_risk_evidence_valid",
        "p0_failure_mode_checklist.md",
    ),
    HardGateRule(
        "tool/action safety gate",
        "missing_tool_action_safety",
        "tool_actions",
        "tool_action_evidence_valid",
        "action_risk_matrix.csv",
    ),
    HardGateRule(
        "human escalation gate",
        "missing_escalation_path",
        "high_impact",
        "escalation_evidence_valid",
        "human_escalation_design.md",
    ),
    HardGateRule(
        "observability gate",
        "missing_monitoring",
        "always",
        None,
        "launch-gate evidence cell",
    ),
    HardGateRule(
        "rollback gate",
        "missing_rollback",
        "always",
        None,
        "launch-gate evidence cell",
    ),
    HardGateRule(
        "owner signoff gate",
        "missing_owner_signoff",
        "always",
        None,
        "launch-gate evidence cell",
    ),
)


def evaluate_hard_gate_policy(
    review: LaunchGateReview,
    context: HardGateContext,
    evidence: HardGateEvidence,
) -> list[HardGateEvaluation]:
    """Evaluate the centralized hard gates in deterministic policy order."""

    return [
        _evaluate_rule(rule, review, context, evidence)
        for rule in HARD_GATE_RULES
    ]


def _evaluate_rule(
    rule: HardGateRule,
    review: LaunchGateReview,
    context: HardGateContext,
    evidence: HardGateEvidence,
) -> HardGateEvaluation:
    rows = [row for row in review.rows if row.canonical_gate == rule.gate]
    applicable = _resolve_applicability(rule, context)

    if rule.gate in review.invalid_canonical_gates:
        return _blocked_evaluation(
            rule,
            applicable,
            "invalid: duplicate rows",
            "Invalid",
            (
                f"{_gate_label(rule)} has duplicate declarations and "
                "cannot be evaluated deterministically."
            ),
        )

    row = rows[0] if rows else None
    if row is not None and row.normalized_status not in {
        "pass",
        "partial",
        "fail",
        "not_applicable",
    }:
        return _blocked_evaluation(
            rule,
            applicable,
            f"invalid: {row.status.strip()}",
            "Invalid",
            (
                f"{_gate_label(rule)} declares unsupported status "
                f"`{row.status.strip()}`."
            ),
        )

    actual_status = row.normalized_status if row is not None else "missing"

    if applicable is None:
        return _blocked_evaluation(
            rule,
            None,
            actual_status,
            "Blocked",
            (
                f"{_gate_label(rule)} applicability could not be "
                "established from valid project evidence."
            ),
        )

    if applicable is False:
        if actual_status in {"partial", "fail"}:
            return _blocked_evaluation(
                rule,
                False,
                actual_status,
                "Blocked",
                (
                    f"{_gate_label(rule)} is not required for this project, "
                    f"but actual status is `{actual_status}`; an explicitly "
                    "incomplete declaration remains blocking."
                ),
            )
        return HardGateEvaluation(
            gate=rule.gate,
            applicable=False,
            required_status=_required_status(rule),
            actual_status=actual_status,
            outcome="Not applicable",
            reason="The project context establishes that this conditional gate is not applicable.",
        )

    if actual_status == "not_applicable":
        issue = ValidationIssue(
            f"launch_gate_review.{rule.gate}.status",
            "not_applicable is prohibited for an applicable hard gate.",
            source="hard_gate_policy",
        )
        reasons = [
            (
                f"{_gate_requirement(rule)}; actual status is "
                "`not_applicable`."
            )
        ]
        if (
            rule.artifact_field is not None
            and not getattr(evidence, rule.artifact_field)
        ):
            reasons.append(
                f"Required evidence is missing or invalid: {rule.artifact_label}."
            )
        return _blocked_evaluation(
            rule,
            True,
            actual_status,
            "Blocked",
            " ".join(reasons),
            policy_issue=issue,
        )

    if actual_status != "pass":
        if actual_status == "missing":
            status_reason = f"{_gate_requirement(rule)}; the gate is missing."
        else:
            status_reason = (
                f"{_gate_requirement(rule)}; actual status is "
                f"`{actual_status}`."
            )
        reasons = [status_reason]
        if (
            rule.artifact_field is not None
            and not getattr(evidence, rule.artifact_field)
        ):
            reasons.append(
                f"Required evidence is missing or invalid: {rule.artifact_label}."
            )
        return _blocked_evaluation(
            rule,
            True,
            actual_status,
            "Blocked",
            " ".join(reasons),
        )

    assert row is not None
    reasons: list[str] = []
    if not is_meaningful_evidence(row.evidence):
        reasons.append(
            (
                f"{_gate_label(rule)} is declared `pass` but does not "
                "contain meaningful evidence."
            )
        )
    if (
        rule.artifact_field is not None
        and not getattr(evidence, rule.artifact_field)
    ):
        reasons.append(
            f"Required evidence is missing or invalid: {rule.artifact_label}."
        )
    if reasons:
        return _blocked_evaluation(
            rule,
            True,
            actual_status,
            "Blocked",
            " ".join(reasons),
        )

    return HardGateEvaluation(
        gate=rule.gate,
        applicable=True,
        required_status=_required_status(rule),
        actual_status=actual_status,
        outcome="Satisfied",
        reason="The declaration and required evidence satisfy this hard gate.",
    )


def _resolve_applicability(
    rule: HardGateRule,
    context: HardGateContext,
) -> bool | None:
    if rule.applicability == "always":
        return True
    if rule.applicability == "high_impact":
        return context.high_impact
    return context.has_tool_actions


def _blocked_evaluation(
    rule: HardGateRule,
    applicable: bool | None,
    actual_status: str,
    outcome: str,
    reason: str,
    *,
    policy_issue: ValidationIssue | None = None,
) -> HardGateEvaluation:
    return HardGateEvaluation(
        gate=rule.gate,
        applicable=applicable,
        required_status=_required_status(rule),
        actual_status=actual_status,
        outcome=outcome,
        reason=reason,
        blocker=HardBlocker(rule.blocker_id, reason, rule.artifact_label),
        policy_issue=policy_issue,
    )


def _required_status(rule: HardGateRule) -> str:
    return (
        "pass"
        if rule.applicability == "always"
        else "pass when applicable"
    )


def _gate_requirement(rule: HardGateRule) -> str:
    requirement = f"{_gate_label(rule)} requires `pass`"
    if rule.applicability == "high_impact":
        return requirement + " for high-impact projects"
    if rule.applicability == "tool_actions":
        return requirement + " when tool actions are present"
    return requirement


def _gate_label(rule: HardGateRule) -> str:
    label = rule.gate[0].upper() + rule.gate[1:]
    return label.replace("p0", "P0")
