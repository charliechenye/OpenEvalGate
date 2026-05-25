"""Readiness scoring and hard-blocker evaluation."""

from __future__ import annotations

from dataclasses import dataclass

from openevalgate.schema import HardBlocker


STATUS_VALUES = {"pass", "partial", "fail", "not_applicable"}

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
    "tail-risk/p0 failure mode gate": "tail_risk_p0_failure_readiness",
    "model selection gate": "model_selection_arena_readiness",
    "model arena gate": "model_selection_arena_readiness",
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
class GateRow:
    gate: str
    status: str
    evidence: str
    mitigation: str
    owner: str


@dataclass(frozen=True)
class ScoreResult:
    score: int
    recommendation: str
    passed_gates: list[GateRow]
    weak_gates: list[GateRow]
    not_applicable_gates: list[GateRow]
    hard_blockers: list[HardBlocker]


def score_gates(
    gates: list[GateRow],
    boundary_coverage_status: str | None = None,
    hard_blockers: list[HardBlocker] | None = None,
) -> ScoreResult:
    """Compute weighted launch readiness score and recommendation."""

    blockers = hard_blockers or []
    category_statuses: dict[str, list[str]] = {category: [] for category in WEIGHTS}
    passed: list[GateRow] = []
    weak: list[GateRow] = []
    not_applicable: list[GateRow] = []

    for gate in gates:
        normalized_status = gate.status.strip().lower()
        if normalized_status == "pass":
            passed.append(gate)
        elif normalized_status == "not_applicable":
            not_applicable.append(gate)
        elif normalized_status in {"partial", "fail"}:
            weak.append(gate)

        category = GATE_TO_CATEGORY.get(normalize_gate(gate.gate))
        if category and normalized_status in STATUS_VALUES:
            category_statuses[category].append(normalized_status)

    # Backward-compatible hint from older report code; ignored by the new model
    # except when no tail-risk gate exists.
    if boundary_coverage_status in STATUS_VALUES and not category_statuses["tail_risk_p0_failure_readiness"]:
        category_statuses["tail_risk_p0_failure_readiness"] = [boundary_coverage_status]

    raw_score = 0.0
    for category, weight in WEIGHTS.items():
        statuses = category_statuses[category]
        if not statuses:
            continue
        raw_score += weight * _category_value(statuses)

    score = int(raw_score + 0.5)
    recommendation = "Not ready" if blockers else readiness_recommendation(score)
    return ScoreResult(score, recommendation, passed, weak, not_applicable, blockers)


def readiness_recommendation(score: int) -> str:
    if score >= 85:
        return "Ready for controlled launch"
    if score >= 70:
        return "Conditional launch"
    if score >= 50:
        return "Shadow launch only"
    return "Not ready"


def gate_statuses(gates: list[GateRow]) -> dict[str, str]:
    return {normalize_gate(gate.gate): gate.status.strip().lower() for gate in gates}


def normalize_gate(gate: str) -> str:
    return " ".join(gate.strip().lower().split())


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
