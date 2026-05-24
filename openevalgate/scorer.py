"""Readiness scoring from launch gate review tables."""

from __future__ import annotations

from dataclasses import dataclass


STATUS_VALUES = {"pass", "partial", "fail", "not_applicable"}

WEIGHTS = {
    "scope_readiness": 8,
    "golden_eval_readiness": 12,
    "boundary_adversarial_coverage": 10,
    "model_selection_arena_readiness": 8,
    "grounding_readiness": 8,
    "tool_action_safety": 10,
    "input_filter_readiness": 6,
    "output_critic_readiness": 8,
    "human_escalation_readiness": 6,
    "observability_readiness": 8,
    "cost_latency_readiness": 6,
    "drift_monitoring_readiness": 5,
    "rollback_readiness": 5,
}

GATE_TO_CATEGORY = {
    "scope gate": "scope_readiness",
    "golden eval gate": "golden_eval_readiness",
    "model selection gate": "model_selection_arena_readiness",
    "model arena gate": "model_selection_arena_readiness",
    "grounding gate": "grounding_readiness",
    "sop/policy compilation gate": "grounding_readiness",
    "tool/action safety gate": "tool_action_safety",
    "input filter gate": "input_filter_readiness",
    "output critic gate": "output_critic_readiness",
    "human escalation gate": "human_escalation_readiness",
    "observability gate": "observability_readiness",
    "cost/latency gate": "cost_latency_readiness",
    "drift monitoring gate": "drift_monitoring_readiness",
    "rollback gate": "rollback_readiness",
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


def score_gates(gates: list[GateRow], boundary_coverage_status: str | None = None) -> ScoreResult:
    """Compute a weighted launch readiness score from gate rows."""

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

        category = GATE_TO_CATEGORY.get(_normalize_gate(gate.gate))
        if category and normalized_status in STATUS_VALUES:
            category_statuses[category].append(normalized_status)

    if boundary_coverage_status in STATUS_VALUES:
        category_statuses["boundary_adversarial_coverage"] = [boundary_coverage_status]

    raw_score = 0.0
    for category, weight in WEIGHTS.items():
        statuses = category_statuses[category]
        if not statuses:
            continue
        if "fail" in statuses:
            category_value = 0.0
        elif "partial" in statuses:
            category_value = 0.5
        elif all(status == "not_applicable" for status in statuses):
            category_value = 0.0
        elif "pass" in statuses:
            category_value = 1.0
        else:
            category_value = 0.0
        raw_score += weight * category_value

    score = int(raw_score + 0.5)
    return ScoreResult(score, readiness_recommendation(score), passed, weak, not_applicable)


def readiness_recommendation(score: int) -> str:
    if score >= 85:
        return "Ready for controlled launch"
    if score >= 70:
        return "Conditional launch"
    if score >= 50:
        return "Shadow launch only"
    return "Not ready"


def _normalize_gate(gate: str) -> str:
    return " ".join(gate.strip().lower().split())
