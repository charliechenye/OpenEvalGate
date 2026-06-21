"""Markdown launch readiness report generation."""

from __future__ import annotations

import csv
import re
from collections import Counter
from pathlib import Path
from typing import Any

from openevalgate.action_risk import ActionRiskReview
from openevalgate.assessment import assess_launch, behavioral_evidence_display
from openevalgate.escalation import summarize_escalation_contract
from openevalgate.eval_results import BehavioralEvidence, classify_behavioral_evidence
from openevalgate.hard_gate_policy import HardGateEvaluation
from openevalgate.launch_gate_review import GateRow, is_meaningful_mitigation
from openevalgate.project_inspection import inspect_project
from openevalgate.routing import summarize_routing_policy
from openevalgate.review_policy import evaluate_behavioral_sufficiency
from openevalgate.schema import (
    HardBlocker,
    LaunchAssessment,
    ReviewMode,
    ValidationIssue,
    load_eval_cases,
)
from openevalgate.scorer import gate_statuses, score_gates


def generate_report(project_dir: str | Path) -> str:
    """Generate a deterministic Markdown launch readiness report."""

    root = Path(project_dir)
    inspection = inspect_project(root)
    check = inspection.check
    cases = _safe_load_cases(root / "eval_cases.yaml")
    gates = inspection.launch_gate_review.valid_rows
    behavioral_evidence = classify_behavioral_evidence(root)
    behavioral_sufficiency = evaluate_behavioral_sufficiency(root)
    blockers = inspection.hard_blockers
    score = score_gates(inspection.launch_gate_review)
    project_evidence_valid = (
        not check.missing_required
        and not _non_behavioral_issues(check.issues)
        and not inspection.policy_issues
    )
    assessment = assess_launch(
        evidence_completeness_score=score.score,
        project_evidence_valid=project_evidence_valid,
        behavioral_sufficiency=behavioral_sufficiency,
        hard_blockers=blockers,
    )
    system_name, assistant_type = _project_identity(root, cases)

    sections = [
        f"# Launch Readiness Report: {system_name}",
        "",
        "## Executive Summary",
        _executive_summary(system_name, assistant_type, assessment),
        "",
        "## Evidence Completeness Score",
        f"{assessment.evidence_completeness_score}/100",
        f"Evidence package band: {assessment.evidence_band}",
        (
            "Control evidence completeness threshold met: "
            f"{'Yes' if assessment.control_evidence_completeness_threshold_met else 'No'}"
        ),
        "",
        (
            "This score measures declared launch-control and governance evidence completeness. "
            "It does not measure observed behavioral quality or determine launch readiness by itself."
        ),
        (
            "Meeting this threshold does not override hard blockers or grant permission "
            "to begin shadow evaluation."
        ),
        "",
        "## Hard-Gate Evaluation",
        _hard_gate_evaluation_table(inspection.evaluations),
        "",
        "## Hard Blockers",
        _hard_blocker_summary(blockers),
        "",
        "## Trust Preservation Summary",
        _artifact_summary(root / "trust_preservation_review.md", "Trust preservation review is present.", "Trust preservation review is missing."),
        "",
        "## Business Behavior Contract Summary",
        _artifact_summary(root / "business_behavior_contract.md", "Business behavior contract is present.", "Business behavior contract is missing."),
        "",
        "## Golden Eval Summary",
        _eval_summary(cases),
        "",
        "## Tail-Risk / P0 Failure Mode Summary",
        _artifact_summary(root / "p0_failure_mode_checklist.md", "P0 failure mode checklist is present.", "P0 failure mode checklist is missing."),
        "",
        "## Automation Boundary Summary",
        _table_file_summary(root / "automation_boundary_matrix.md", "Automation boundary matrix"),
        "",
        "## Human Escalation Summary",
        _human_escalation_summary(root),
        "",
        "## Tool/Action Safety Summary",
        _action_risk_summary(check.action_risk_review),
        "",
        "## Input/Output Perimeter Summary",
        _input_output_summary(root),
        "",
        "## Model Arena Summary",
        _csv_summary(root / "model_arena_scorecard.csv", "model", "No model arena scorecard found."),
        "",
        "## Routing / Capability Allocation Summary",
        _routing_policy_summary(root),
        "",
        "## Metric Stack Summary",
        _artifact_summary(root / "chatbot_success_metric_stack.md", "Chatbot success metric stack is present.", "Chatbot success metric stack is missing."),
        "",
        "## Domain-Owner Feedback Loop Summary",
        _artifact_summary(root / "domain_owner_feedback_loop.md", "Domain-owner feedback loop evidence is present.", "No domain-owner feedback loop artifact found."),
        "",
        "## Observability / Rollback Summary",
        _observability_rollback_summary(gates, inspection.evaluations),
        "",
        "## Review Mode and Behavioral Sufficiency",
        _behavioral_sufficiency_summary(assessment),
        "",
        "## Observed Behavioral Quality",
        _observed_behavioral_quality(behavioral_evidence),
        "",
        "## Critical-Control Status",
        _critical_control_summary(assessment),
        "",
        "## Maximum Permitted Stage",
        assessment.maximum_permitted_stage,
        "",
        "## Required Mitigations",
        _required_mitigations(score.weak_gates, check.missing_required, blockers),
        "",
        "## Recommended Next Actions",
        _recommended_next_actions(assessment),
        "",
        "## Final Launch Recommendation",
        assessment.recommendation,
        "",
    ]

    return "\n".join(sections)


def write_report(project_dir: str | Path, output_path: str | Path) -> Path:
    report = generate_report(project_dir)
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(report, encoding="utf-8", newline="\n")
    return target


def _project_identity(root: Path, cases: list[dict[str, Any]]) -> tuple[str, str]:
    prd = root / "assistant_prd.md"
    system_name = root.name.replace("_", " ").title()
    assistant_type = cases[0].get("assistant_type", "unknown") if cases else "unknown"

    if prd.is_file():
        text = prd.read_text(encoding="utf-8")
        title = re.search(r"^#\s+(.+)$", text, flags=re.MULTILINE)
        if title:
            system_name = title.group(1).strip()
        match = re.search(r"\*\*Assistant type:\*\*\s*(.+)", text)
        if match:
            assistant_type = match.group(1).strip()

    return system_name, assistant_type


def _executive_summary(
    system_name: str,
    assistant_type: str,
    assessment: LaunchAssessment,
) -> str:
    return "\n".join(
        [
            f"- **System name:** {system_name}",
            f"- **Assistant type:** {assistant_type}",
            f"- **Evidence completeness score:** {assessment.evidence_completeness_score}/100",
            f"- **Evidence package band:** {assessment.evidence_band}",
            f"- **Behavioral evidence status:** {behavioral_evidence_display(assessment.behavioral_evidence_state)}",
            f"- **Declared review mode:** {_mode_display(assessment.declared_review_mode)}",
            f"- **Effective review mode:** {_mode_display(assessment.effective_review_mode)}",
            (
                "- **Sufficiency for effective review mode:** "
                + ("Sufficient" if assessment.behavioral_sufficiency.sufficient_for_effective_mode else "Insufficient")
            ),
            f"- **Critical-control status:** {assessment.critical_control_status}",
            f"- **Maximum permitted stage:** {assessment.maximum_permitted_stage}",
            f"- **Final launch recommendation:** {assessment.recommendation}",
            "- **Recommended next actions:** "
            + "; ".join(
                action.rstrip(".") for action in assessment.recommended_next_actions
            )
            + ".",
            f"- **Hard blockers:** {len(assessment.hard_blockers)}",
        ]
    )


def _hard_blocker_summary(blockers: list[HardBlocker]) -> str:
    if not blockers:
        return "No hard blockers detected."
    return "\n".join(f"- **{blocker.id}:** {blocker.reason} Evidence: {blocker.evidence}" for blocker in blockers)


def _hard_gate_evaluation_table(
    evaluations: list[HardGateEvaluation],
) -> str:
    lines = [
        "| Gate | Applicable | Required status | Actual status | Outcome |",
        "| --- | --- | --- | --- | --- |",
    ]
    for evaluation in evaluations:
        if evaluation.applicable is None:
            applicable = "Unknown"
        else:
            applicable = "Yes" if evaluation.applicable else "No"
        lines.append(
            "| "
            + " | ".join(
                [
                    evaluation.gate,
                    applicable,
                    evaluation.required_status,
                    evaluation.actual_status,
                    evaluation.outcome,
                ]
            )
            + " |"
        )
    return "\n".join(lines)


def _artifact_summary(path: Path, present: str, missing: str) -> str:
    return f"- {present}" if path.is_file() else f"- {missing}"


def _table_file_summary(path: Path, label: str) -> str:
    if not path.is_file():
        return f"- {label} is missing."
    rows = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip().startswith("|") and "---" not in line]
    data_rows = max(len(rows) - 1, 0)
    return f"- {label} is present with {data_rows} row(s)."


def _human_escalation_summary(root: Path) -> str:
    design_path = root / "human_escalation_design.md"
    contract = summarize_escalation_contract(root / "escalation_contract.yaml")
    lines = [_table_file_summary(design_path, "Human escalation design")]
    if not contract.present:
        lines.append("- Structured escalation contract: not provided (optional).")
        return "\n".join(lines)
    lines.extend(
        [
            f"- Structured escalation contract: {'valid' if contract.valid else 'invalid'}.",
            f"- Workflow: {contract.workflow_id or 'unknown'}",
            f"- Triggers: {contract.trigger_count}",
            f"- Destinations: {contract.destination_count} ({', '.join(contract.destinations) or 'none'})",
            f"- Handoff types: {', '.join(contract.handoff_types) or 'none'}",
            f"- Destination SLA coverage: {_format_rate(contract.sla_coverage)}",
            f"- Destination fallback coverage: {_format_rate(contract.fallback_coverage)}",
            f"- Checkpoint required: {_format_optional_bool(contract.checkpoint_required)}",
            f"- Idempotency required: {_format_optional_bool(contract.idempotency_required)}",
            f"- Resume behavior defined: {_format_optional_bool(contract.resume_behavior_defined)}",
            f"- Required eval slices: {contract.required_eval_slice_count}",
            f"- Eval handoff coverage: {_eval_handoff_coverage(root)}",
        ]
    )
    return "\n".join(lines)


def _routing_policy_summary(root: Path) -> str:
    summary = summarize_routing_policy(root / "routing_policy.yaml")
    if not summary.present:
        return "- Structured routing policy: not provided (optional)."
    return "\n".join(
        [
            f"- Structured routing policy: {'valid' if summary.valid else 'invalid'}.",
            f"- Policy: {summary.policy_id or 'unknown'}",
            f"- Version: {summary.version or 'unknown'}",
            f"- Approved models: {summary.model_count}",
            f"- Workflows: {summary.workflow_count}",
            (
                "- Workflow kinds: "
                f"subagent={summary.subagent_count}, "
                f"deterministic={summary.deterministic_count}, "
                f"human={summary.human_count}"
            ),
            (
                "- Assignment modes: "
                f"fixed={summary.fixed_count}, "
                f"adaptive={summary.adaptive_count}, "
                f"none={summary.no_model_count}"
            ),
            f"- Workflow fallback coverage: {_format_rate(summary.fallback_coverage)}",
            f"- Workflow eval coverage: {_format_rate(summary.eval_coverage)}",
            f"- High-risk control coverage: {_format_rate(summary.high_risk_control_coverage)}",
            f"- Rollback defined: {_format_optional_bool(summary.rollback_defined)}",
        ]
    )


def _action_risk_summary(review: ActionRiskReview) -> str:
    if not review.present:
        return "No action risk matrix found."
    if not review.valid:
        risk_counts = _diagnostic_action_risk_counts(review)
        return "\n".join(
            [
                (
                    "- Action-risk matrix: invalid; the following counts "
                    "are diagnostic only and were not used for policy decisions."
                ),
                f"- Rows: {len(review.rows)}",
                "- Risk tiers: " + _counter_summary(risk_counts),
            ]
        )
    rows = review.rows
    risk_counts = Counter(row.get("risk_tier", "unknown").lower() for row in rows)
    high_actions = [row.get("action", "") for row in rows if row.get("risk_tier", "").lower() in {"high", "prohibited"}]
    lines = [
        f"- Rows: {len(rows)}",
        "- Risk tiers: " + _counter_summary(risk_counts),
    ]
    if high_actions:
        lines.append("- High/prohibited actions: " + ", ".join(high_actions))
    return "\n".join(lines)


def _input_output_summary(root: Path) -> str:
    input_filter = "Input filter gate evidence is in launch_gate_review.md."
    critic = _csv_summary(root / "output_critic_rubric.csv", "dimension", "No output critic rubric found.")
    return f"- {input_filter}\n{critic}"


def _observability_rollback_summary(
    gates: list[GateRow],
    evaluations: list[HardGateEvaluation],
) -> str:
    statuses = gate_statuses(gates)
    observability = _hard_gate_actual_status(
        evaluations,
        "observability gate",
    )
    drift = statuses.get("drift monitoring gate", "missing")
    rollback = _hard_gate_actual_status(evaluations, "rollback gate")
    return f"- Observability gate: {observability}\n- Drift monitoring gate: {drift}\n- Rollback gate: {rollback}"


def _hard_gate_actual_status(
    evaluations: list[HardGateEvaluation],
    gate: str,
) -> str:
    evaluation = next(
        (item for item in evaluations if item.gate == gate),
        None,
    )
    return evaluation.actual_status if evaluation else "missing"


def _diagnostic_action_risk_counts(
    review: ActionRiskReview,
) -> Counter[str]:
    positions = review.header_positions.get("risk_tier", ())
    if len(positions) != 1:
        return Counter({"unknown": len(review.rows)})
    risk_index = positions[0]
    counts: Counter[str] = Counter()
    for row in review.rows:
        value = (
            row.raw_cells[risk_index].strip().lower()
            if risk_index < len(row.raw_cells)
            else ""
        )
        counts[value or "unknown"] += 1
    return counts


def _required_mitigations(weak_gates: list[GateRow], missing_required: list[str], blockers: list[HardBlocker]) -> str:
    lines: list[str] = []
    for blocker in blockers:
        lines.append(f"- Launch blocker: {blocker.reason}")
    for missing in missing_required:
        lines.append(f"- Add missing required launch file: `{missing}`.")
    for gate in weak_gates:
        if is_meaningful_mitigation(gate.mitigation):
            lines.append(f"- {gate.gate}: {gate.mitigation}")
        else:
            lines.append(f"- {gate.gate}: mitigation not provided.")
    return "\n".join(lines) if lines else "No required mitigations recorded."


def _eval_summary(cases: list[dict[str, Any]]) -> str:
    if not cases:
        return "No eval cases found."
    case_types = Counter(str(case.get("case_type", "unknown")) for case in cases)
    risk_tiers = Counter(str(case.get("risk_tier", "unknown")) for case in cases)
    routes = Counter(str(case.get("expected_route", "unknown")) for case in cases)
    workflow_routes = Counter(
        str(case.get("expected_workflow_route"))
        for case in cases
        if case.get("expected_workflow_route")
    )
    boundary_cases = [case for case in cases if isinstance(case.get("boundary"), dict)]
    boundary_families = {
        str(case["boundary"].get("family_id"))
        for case in boundary_cases
        if case["boundary"].get("family_id")
    }
    lines = [
        f"- Total cases: {len(cases)}",
        "- Case types: " + _counter_summary(case_types),
        "- Risk tiers: " + _counter_summary(risk_tiers),
        "- Expected admission routes: " + _counter_summary(routes),
        f"- Boundary metadata coverage: {len(boundary_cases)}/{len(cases)} cases across {len(boundary_families)} contrast family/families",
    ]
    if workflow_routes:
        lines.append("- Expected workflow routes: " + _counter_summary(workflow_routes))
    return "\n".join(lines)


def _observed_behavioral_quality(evidence: BehavioralEvidence) -> str:
    display = behavioral_evidence_display(evidence.state)
    scope_note = (
        "This section summarizes all valid behavioral rows in the results file. "
        "Controlled-launch authorization, when requested, uses only the selected "
        "run and candidate shown above."
    )
    if evidence.state != "available":
        lines = [scope_note, "", f"**{display}**"]
        if evidence.issues:
            lines.extend(
                [
                    "",
                    "Validation issues:",
                    "",
                    *[f"- `{issue.path}`: {issue.message}" for issue in evidence.issues],
                ]
            )
        return "\n".join(lines)

    summary = evidence.summary
    assert summary is not None

    lines = [
        scope_note,
        "",
        f"**{display}**",
        "",
        f"- Total result rows: {summary.row_count}",
        f"- Latest run ID: {summary.latest_run_id or 'unknown'}",
        "- Candidate coverage: " + (", ".join(summary.candidates) if summary.candidates else "unknown"),
        f"- Eval pass rate: {_format_rate(summary.pass_rate)}",
        f"- Admission-route match rate: {_format_rate(summary.route_match_rate)}",
        "- Failed case IDs: " + (", ".join(summary.failed_case_ids) if summary.failed_case_ids else "none"),
        "- Top failure categories: " + (_counter_summary(summary.failure_categories) if summary.failure_categories else "none"),
        f"- Workflow-route accuracy: {_format_rate(summary.workflow_route_accuracy)}",
        f"- Workflow-assignment accuracy: {_format_rate(summary.workflow_assignment_accuracy)}",
        f"- Model-policy compliance: {_format_rate(summary.model_policy_compliance)}",
        f"- Routing-policy version match: {_format_rate(summary.routing_policy_version_match_rate)}",
        f"- Deterministic/no-model path compliance: {_format_rate(summary.deterministic_path_compliance)}",
        f"- Trajectory pass rate: {_format_rate(summary.trajectory_pass_rate)}",
        f"- End-state pass rate: {_format_rate(summary.end_state_pass_rate)}",
        f"- Prohibited-action rate: {_format_rate(summary.prohibited_action_rate)}",
        (
            f"- Contrast-family reliability: {_format_rate(summary.contrast_family_reliability)} "
            f"({summary.complete_boundary_family_count}/{summary.boundary_family_count} families have complete result coverage)"
        ),
        f"- Semantic stability: {_format_rate(summary.semantic_stability)}",
        (
            f"- Repeated-run reliability: {_format_rate(summary.repeated_run_reliability)} "
            f"({summary.repeated_case_count} repeatedly evaluated case(s))"
        ),
        f"- Required-escalation recall: {_format_rate(summary.required_escalation_recall)}",
        f"- Over-escalation rate: {_format_rate(summary.over_escalation_rate)}",
        f"- Destination accuracy: {_format_rate(summary.destination_accuracy)}",
        f"- Context-preservation rate: {_format_rate(summary.context_preservation_rate)}",
        f"- Fallback success rate: {_format_rate(summary.fallback_success_rate)}",
        f"- Resume success rate: {_format_rate(summary.resume_success_rate)}",
        f"- Late-escalation rate: {_format_rate(summary.late_escalation_rate)}",
    ]
    if summary.observed_output_paths:
        lines.append("- Observed output paths: " + ", ".join(summary.observed_output_paths[:8]))
    return "\n".join(lines)


def _critical_control_summary(assessment: LaunchAssessment) -> str:
    if assessment.critical_control_status == "Not evaluated":
        return (
            "**Not evaluated**\n\n"
            "No known blockers were found, but critical-control sufficiency has not been evaluated."
        )
    if assessment.critical_control_status == "No known blockers detected":
        return (
            "**No known blockers detected**\n\n"
            "Available evidence has not established that all critical controls are satisfied."
        )
    if assessment.critical_control_status == "Pass":
        return "**Pass**\n\nAll bounded controlled-launch requirements are satisfied."
    return "\n".join(
        [
            "**Fail**",
            "",
            "The following critical controls failed:",
            "",
            *[f"- `{blocker.id}`" for blocker in assessment.hard_blockers],
        ]
    )


def _recommended_next_actions(assessment: LaunchAssessment) -> str:
    return "\n".join(
        f"- {action}" for action in assessment.recommended_next_actions
    )


def _non_behavioral_issues(issues: list[ValidationIssue]) -> list[ValidationIssue]:
    return [
        issue for issue in issues
        if issue.source not in {"eval_results", "review_policy"}
    ]


def _non_eval_result_issues(issues: list[ValidationIssue]) -> list[ValidationIssue]:
    """Backward-compatible test helper for result-only filtering."""
    return [issue for issue in issues if issue.source != "eval_results"]


def _mode_display(mode: Any) -> str:
    return mode.value if mode is not None else "Not configured"


def _behavioral_sufficiency_summary(assessment: LaunchAssessment) -> str:
    value = assessment.behavioral_sufficiency
    if not value.policy_present:
        policy_display = "Not provided"
    elif not value.policy_valid:
        policy_display = "Invalid"
    else:
        policy_display = "Present"
    selected_state = _selected_scope_state(value)
    selected_value = lambda actual, empty="none": _selected_scope_value(
        value, selected_state, actual, empty=empty
    )
    lines = [
        f"- Review policy: {policy_display}",
        f"- Declared review mode: {_mode_display(value.declared_mode)}",
        f"- Effective review mode: {_mode_display(value.effective_mode)}",
        f"- Selected run: {value.selected_run_id or 'Not configured'}",
        f"- Selected candidate: {value.selected_candidate or 'Not configured'}",
        f"- Selected result rows: {selected_value(str(value.selected_row_count))}",
        f"- Expected eval cases: {value.expected_case_count}",
        f"- Observed eval cases: {selected_value(str(value.observed_case_count))}",
        f"- Case coverage: {_selected_scope_rate(value.case_coverage, value, selected_state)}",
        f"- Cases meeting minimum trial depth: {selected_value(str(value.cases_meeting_trial_depth_count))}",
        f"- Missing eval cases: {selected_value(', '.join(value.missing_case_ids))}",
        (
            "- Represented cases below trial depth: "
            + selected_value(", ".join(value.observed_cases_below_trial_depth))
        ),
        f"- Expected critical cases: {value.expected_critical_case_count}",
        f"- Observed critical cases: {selected_value(str(value.observed_critical_case_count))}",
        f"- Critical-case coverage: {_selected_scope_rate(value.critical_case_coverage, value, selected_state, critical=True)}",
        f"- Missing critical cases: {selected_value(', '.join(value.missing_critical_case_ids))}",
        (
            "- Critical cases below trial depth: "
            + selected_value(", ".join(value.critical_cases_below_trial_depth))
        ),
        f"- Failing critical cases: {selected_value(', '.join(value.failed_critical_case_ids))}",
        (
            "- Sufficiency for effective review mode: "
            + ("Yes" if value.sufficient_for_effective_mode else "No")
        ),
        "",
        "| Metric | Actual | Requirement | Status |",
        "| --- | --- | --- | --- |",
    ]
    outcomes = {item.metric: item for item in value.threshold_outcomes}
    for metric in ("pass_rate", "route_match_rate"):
        outcome = outcomes.get(metric)
        if outcome is None:
            lines.append(f"| {metric} | Not evaluated | Not configured | Not configured |")
        else:
            actual = _outcome_value(outcome.actual_value, value, selected_state)
            lines.append(
                f"| {metric} | {actual} | >= {outcome.configured_threshold:.0%} | {_status_display(outcome.status)} |"
            )
    lines.extend([
        "",
        "Controlled-launch behavioral invariants",
        "",
        "| Invariant | Status | Reason |",
        "| --- | --- | --- |",
    ])
    for outcome in value.invariant_outcomes:
        lines.append(
            f"| {outcome.invariant_id} | {_status_display(outcome.status)} | {outcome.reason} |"
        )
    if value.effective_mode != ReviewMode.CONTROLLED_LAUNCH:
        lines.extend([
            "",
            (
                "These invariants are informational in the current review mode "
                "and do not authorize controlled launch."
            ),
        ])
    return "\n".join(lines)


def _selected_scope_state(sufficiency: Any) -> str:
    if not sufficiency.policy_valid:
        return "invalid_policy"
    if sufficiency.behavioral_evidence_state == "invalid":
        return "invalid_behavioral_evidence"
    if not sufficiency.selected_scope_configured:
        return "not_evaluated"
    return "evaluated"


def _selected_scope_value(
    sufficiency: Any,
    state: str,
    value: str,
    *,
    empty: str = "none",
) -> str:
    if state == "invalid_policy":
        return "Unavailable due to invalid review policy"
    if state == "invalid_behavioral_evidence":
        return "Unavailable due to invalid behavioral evidence"
    if state == "not_evaluated":
        return "Not evaluated"
    return value or empty


def _selected_scope_rate(
    value: float | None,
    sufficiency: Any,
    state: str,
    critical: bool = False,
) -> str:
    unavailable = _selected_scope_value(sufficiency, state, "")
    if state != "evaluated":
        return unavailable
    if value is None:
        if critical and sufficiency.expected_critical_case_count == 0:
            return "Not applicable"
        return "Not evaluated"
    return f"{value:.0%}"


def _outcome_value(value: float | None, sufficiency: Any, state: str) -> str:
    if state == "invalid_policy":
        return "Unavailable due to invalid review policy"
    if state == "invalid_behavioral_evidence":
        return "Unavailable due to invalid behavioral evidence"
    return "Not evaluated" if value is None else f"{value:.0%}"


def _status_display(status: str) -> str:
    return {
        "pass": "Pass",
        "fail": "Fail",
        "not_evaluated": "Not evaluated",
        "not_applicable": "Not applicable",
    }.get(status, status)


def _safe_load_cases(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    try:
        return load_eval_cases(path)
    except Exception:  # noqa: BLE001 - report should still render with malformed eval YAML.
        return []


def _eval_handoff_coverage(root: Path) -> str:
    cases = _safe_load_cases(root / "eval_cases.yaml")
    required = [
        case
        for case in cases
        if case.get("expected_workflow_route") in {"approval", "escalate"}
    ]
    covered = sum(1 for case in required if isinstance(case.get("expected_handoff"), dict))
    return f"{covered}/{len(required)} required-handoff cases"


def _csv_summary(path: Path, label_field: str, missing: str) -> str:
    if not path.is_file():
        return missing
    rows = _read_csv(path)
    if not rows:
        return f"{path.name} exists but has no rows."
    labels = [row.get(label_field, "") for row in rows if row.get(label_field)]
    summary = [f"- Rows: {len(rows)}"]
    if labels:
        summary.append(f"- Covered {label_field}s: {', '.join(labels[:8])}")
    return "\n".join(summary)


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _counter_summary(counter: Counter[str]) -> str:
    return ", ".join(f"{name}={count}" for name, count in sorted(counter.items()))


def _format_rate(value: float | None) -> str:
    if value is None:
        return "unknown"
    return f"{value:.0%}"


def _format_optional_bool(value: bool | None) -> str:
    if value is None:
        return "unknown"
    return "yes" if value else "no"
