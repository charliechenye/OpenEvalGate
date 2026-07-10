"""Evidence-completeness scoring and hard-blocker evaluation."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, replace

from openevalgate.assessment import evidence_completeness_band
from openevalgate.launch_gate_review import (
    ALLOWED_GATE_STATUSES,
    GateRow,
    LaunchGateReview,
    canonicalize_gate_name,
    normalize_gate_name,
)

# Backward-compatible alias; launch_gate_review remains the source of truth.
STATUS_VALUES = ALLOWED_GATE_STATUSES

WEIGHTS = {
    "scope_readiness": 5,
    "trust_preservation_readiness": 8,
    "business_behavior_contract_readiness": 7,
    "golden_eval_readiness": 10,
    "tail_risk_p0_failure_readiness": 10,
    "model_selection_arena_readiness": 7,
    "grounding_readiness": 6,
    "sop_policy_compilation_readiness": 5,
    "tool_action_safety_readiness": 8,
    "automation_boundary_readiness": 6,
    "human_escalation_readiness": 5,
    "input_output_perimeter_readiness": 6,
    "domain_owner_feedback_loop_readiness": 4,
    "observability_readiness": 5,
    "cost_latency_readiness": 3,
    "journey_business_metrics_readiness": 5,
}

GATE_TO_CATEGORY = {
    "scope gate": "scope_readiness",
    "trust preservation gate": "trust_preservation_readiness",
    "business behavior contract gate": "business_behavior_contract_readiness",
    "golden eval gate": "golden_eval_readiness",
    "tail-risk / p0 failure mode gate": "tail_risk_p0_failure_readiness",
    "model selection gate": "model_selection_arena_readiness",
    "model arena gate": "model_selection_arena_readiness",
    "routing / capability allocation gate": "model_selection_arena_readiness",
    "grounding gate": "grounding_readiness",
    "sop/policy compilation gate": "sop_policy_compilation_readiness",
    "tool/action safety gate": "tool_action_safety_readiness",
    "automation boundary gate": "automation_boundary_readiness",
    "human escalation gate": "human_escalation_readiness",
    "input filter gate": "input_output_perimeter_readiness",
    "output critic gate": "input_output_perimeter_readiness",
    "domain-owner feedback loop gate": "domain_owner_feedback_loop_readiness",
    "observability gate": "observability_readiness",
    "drift monitoring gate": "observability_readiness",
    "cost/latency gate": "cost_latency_readiness",
    "journey metric / durable resolution gate": "journey_business_metrics_readiness",
    "business trust metric gate": "journey_business_metrics_readiness",
}


@dataclass(frozen=True)
class ScoreResult:
    score: int
    evidence_band: str
    passed_gates: list[GateRow]
    weak_gates: list[GateRow]
    not_applicable_gates: list[GateRow]


def score_gates(
    gates: list[GateRow] | LaunchGateReview,
    boundary_coverage_status: str | None = None,
) -> ScoreResult:
    """Compute the weighted evidence-completeness score and band."""

    category_statuses: dict[str, list[str]] = {category: [] for category in WEIGHTS}
    passed: list[GateRow] = []
    weak: list[GateRow] = []
    not_applicable: list[GateRow] = []

    valid_standard_rows = _valid_standard_rows(gates)
    for gate in valid_standard_rows:
        normalized_status = gate.normalized_status
        if normalized_status == "pass":
            passed.append(gate)
        elif normalized_status == "not_applicable":
            not_applicable.append(gate)
        elif normalized_status in {"partial", "fail"}:
            weak.append(gate)

    for gate in _scorable_rows(valid_standard_rows):
        normalized_status = gate.normalized_status
        category = GATE_TO_CATEGORY.get(gate.canonical_gate or "")
        if category:
            category_statuses[category].append(normalized_status)

    # Backward-compatible hint from older report code; ignored by the new model
    # except when no tail-risk gate exists.
    if (
        boundary_coverage_status in ALLOWED_GATE_STATUSES
        and not category_statuses["tail_risk_p0_failure_readiness"]
    ):
        category_statuses["tail_risk_p0_failure_readiness"] = [boundary_coverage_status]

    raw_score = 0.0
    for category, weight in WEIGHTS.items():
        statuses = category_statuses[category]
        if not statuses:
            continue
        raw_score += weight * _category_value(statuses)

    score = int(raw_score + 0.5)
    return ScoreResult(
        score,
        evidence_completeness_band(score),
        passed,
        weak,
        not_applicable,
    )


def gate_statuses(gates: list[GateRow]) -> dict[str, str]:
    """Return unambiguous standard-gate statuses for display compatibility."""

    rows = _valid_standard_rows(gates)
    return {
        gate.canonical_gate: gate.normalized_status
        for gate in rows
        if gate.canonical_gate is not None
    }


def normalize_gate(gate: str) -> str:
    """Backward-compatible gate-name normalization."""

    return normalize_gate_name(gate)


def _category_value(statuses: list[str]) -> float:
    if "fail" in statuses:
        return 0.0
    if "partial" in statuses:
        return 0.5
    if all(status == "not_applicable" for status in statuses):
        return 0.0
    if "pass" in statuses:
        return 1.0
    return 0.0


def _valid_standard_rows(
    gates: list[GateRow] | LaunchGateReview,
) -> list[GateRow]:
    if isinstance(gates, LaunchGateReview):
        rows = gates.valid_rows
    else:
        normalized_rows = [
            replace(
                row,
                canonical_gate=(row.canonical_gate or canonicalize_gate_name(row.gate)),
            )
            for row in gates
        ]
        counts = Counter(
            row.canonical_gate for row in normalized_rows if row.canonical_gate is not None
        )
        duplicates = {gate for gate, count in counts.items() if count > 1}
        rows = [
            row
            for row in normalized_rows
            if row.normalized_status in ALLOWED_GATE_STATUSES
            and row.canonical_gate not in duplicates
        ]
    return [row for row in rows if row.canonical_gate is not None]


def _scorable_rows(valid_standard_rows: list[GateRow]) -> list[GateRow]:
    return [row for row in valid_standard_rows if row.canonical_gate in GATE_TO_CATEGORY]
