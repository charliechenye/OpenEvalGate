"""Markdown launch readiness report generation."""

from __future__ import annotations

import csv
import re
from collections import Counter
from pathlib import Path
from typing import Any

from openevalgate.eval_results import summarize_eval_results
from openevalgate.schema import HardBlocker, load_eval_cases, validate_eval_cases
from openevalgate.scorer import GateRow, gate_statuses, normalize_gate, score_gates
from openevalgate.validator import check_project


def generate_report(project_dir: str | Path) -> str:
    """Generate a deterministic Markdown launch readiness report."""

    root = Path(project_dir)
    check = check_project(root)
    cases = _safe_load_cases(root / "eval_cases.yaml")
    gates = parse_launch_gate_review(root / "launch_gate_review.md") if (root / "launch_gate_review.md").exists() else []
    blockers = evaluate_hard_blockers(root, gates, check.missing_required)
    score = score_gates(gates, hard_blockers=blockers)
    system_name, assistant_type = _project_identity(root, cases)

    sections = [
        f"# Launch Readiness Report: {system_name}",
        "",
        "## Executive Summary",
        _executive_summary(system_name, assistant_type, score.score, score.recommendation, blockers),
        "",
        "## Overall Readiness Score",
        f"{score.score}/100",
        "",
        "## Recommendation",
        score.recommendation,
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
        _table_file_summary(root / "human_escalation_design.md", "Human escalation design"),
        "",
        "## Tool/Action Safety Summary",
        _action_risk_summary(root / "action_risk_matrix.csv"),
        "",
        "## Input/Output Perimeter Summary",
        _input_output_summary(root),
        "",
        "## Model Arena Summary",
        _csv_summary(root / "model_arena_scorecard.csv", "model", "No model arena scorecard found."),
        "",
        "## Metric Stack Summary",
        _artifact_summary(root / "chatbot_success_metric_stack.md", "Chatbot success metric stack is present.", "Chatbot success metric stack is missing."),
        "",
        "## Domain-Owner Feedback Loop Summary",
        _artifact_summary(root / "domain_owner_feedback_loop.md", "Domain-owner feedback loop evidence is present.", "No domain-owner feedback loop artifact found."),
        "",
        "## Observability / Rollback Summary",
        _observability_rollback_summary(gates),
        "",
        "## Eval Results Summary",
        _eval_results_summary(root),
        "",
        "## Required Mitigations",
        _required_mitigations(score.weak_gates, check.missing_required, blockers),
        "",
        "## Suggested Next Actions",
        _next_actions(score.weak_gates, score.score, check.missing_required, blockers),
        "",
        "## Final Launch Recommendation",
        _final_recommendation(score.recommendation, blockers),
        "",
    ]

    return "\n".join(sections)


def write_report(project_dir: str | Path, output_path: str | Path) -> Path:
    report = generate_report(project_dir)
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(report, encoding="utf-8")
    return target


def parse_launch_gate_review(path: str | Path) -> list[GateRow]:
    """Parse the Markdown launch gate table used by OpenEvalGate templates."""

    rows: list[GateRow] = []
    if not Path(path).is_file():
        return rows

    for line in Path(path).read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or "---" in stripped:
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) < 5 or cells[0].lower() == "gate":
            continue
        rows.append(GateRow(cells[0], cells[1].lower(), cells[2], cells[3], cells[4]))
    return rows


def evaluate_hard_blockers(root: Path, gates: list[GateRow], missing_required: list[str]) -> list[HardBlocker]:
    """Evaluate launch blockers that override the numeric readiness score."""

    blockers: list[HardBlocker] = []
    statuses = gate_statuses(gates)
    cases = _safe_load_cases(root / "eval_cases.yaml")
    high_impact = _has_high_impact(cases, root / "action_risk_matrix.csv")

    if "assistant_prd.md" in missing_required or _gate_missing_or_failed(statuses, "scope gate"):
        blockers.append(HardBlocker("missing_scope", "No passing supported/unsupported scope gate.", "assistant_prd.md or Scope gate"))

    eval_path = root / "eval_cases.yaml"
    eval_valid = eval_path.is_file() and validate_eval_cases(eval_path).valid
    if not eval_valid or _gate_missing_or_failed(statuses, "golden eval gate"):
        blockers.append(HardBlocker("missing_golden_eval", "No valid golden eval set with passing gate.", "eval_cases.yaml or Golden eval gate"))

    if high_impact and ((root / "p0_failure_mode_checklist.md").is_file() is False or _gate_missing_or_failed(statuses, "tail-risk / p0 failure mode gate")):
        blockers.append(HardBlocker("missing_tail_risk_review", "High-impact workflows lack passing tail-risk/P0 review.", "p0_failure_mode_checklist.md or Tail-risk / P0 gate"))

    unsafe_actions = _high_risk_actions_without_controls(root / "action_risk_matrix.csv")
    if unsafe_actions:
        blockers.append(HardBlocker("ungated_high_risk_action", "High-risk action lacks deterministic enforcement or human approval.", ", ".join(unsafe_actions)))

    if high_impact and ((root / "human_escalation_design.md").is_file() is False or _gate_missing_or_failed(statuses, "human escalation gate")):
        blockers.append(HardBlocker("missing_escalation_path", "High-risk or low-confidence cases lack a passing escalation path.", "human_escalation_design.md or Human escalation gate"))

    if _gate_not_passing(statuses, "rollback gate"):
        blockers.append(HardBlocker("missing_rollback", "Rollback gate is missing or not passing.", "Rollback gate"))

    if _gate_not_passing(statuses, "owner signoff gate"):
        blockers.append(HardBlocker("missing_owner_signoff", "Owner signoff gate is missing or not passing.", "Owner signoff gate"))

    if _gate_missing_or_failed(statuses, "observability gate"):
        blockers.append(HardBlocker("missing_monitoring", "Monitoring/observability gate is missing or failed.", "Observability gate"))

    return blockers


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


def _executive_summary(system_name: str, assistant_type: str, score: int, recommendation: str, blockers: list[HardBlocker]) -> str:
    blocker_text = "No hard blockers detected." if not blockers else f"{len(blockers)} hard blocker(s) require remediation."
    return "\n".join(
        [
            f"- **System name:** {system_name}",
            f"- **Assistant type:** {assistant_type}",
            f"- **Overall readiness score:** {score}/100",
            f"- **Recommendation:** {recommendation}",
            f"- **Launch blocker status:** {blocker_text}",
        ]
    )


def _hard_blocker_summary(blockers: list[HardBlocker]) -> str:
    if not blockers:
        return "No hard blockers detected."
    return "\n".join(f"- **{blocker.id}:** {blocker.reason} Evidence: {blocker.evidence}" for blocker in blockers)


def _artifact_summary(path: Path, present: str, missing: str) -> str:
    return f"- {present}" if path.is_file() else f"- {missing}"


def _table_file_summary(path: Path, label: str) -> str:
    if not path.is_file():
        return f"- {label} is missing."
    rows = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip().startswith("|") and "---" not in line]
    data_rows = max(len(rows) - 1, 0)
    return f"- {label} is present with {data_rows} row(s)."


def _action_risk_summary(path: Path) -> str:
    if not path.is_file():
        return "No action risk matrix found."
    rows = _read_csv(path)
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


def _observability_rollback_summary(gates: list[GateRow]) -> str:
    statuses = gate_statuses(gates)
    observability = statuses.get("observability gate", "missing")
    drift = statuses.get("drift monitoring gate", "missing")
    rollback = statuses.get("rollback gate", "missing")
    return f"- Observability gate: {observability}\n- Drift monitoring gate: {drift}\n- Rollback gate: {rollback}"


def _required_mitigations(weak_gates: list[GateRow], missing_required: list[str], blockers: list[HardBlocker]) -> str:
    lines: list[str] = []
    for blocker in blockers:
        lines.append(f"- Launch blocker: {blocker.reason}")
    for missing in missing_required:
        lines.append(f"- Add missing required launch file: `{missing}`.")
    for gate in weak_gates:
        if gate.mitigation and gate.mitigation.lower() not in {"none", "n/a"}:
            lines.append(f"- {gate.gate}: {gate.mitigation}")
    return "\n".join(lines) if lines else "No required mitigations recorded."


def _next_actions(weak_gates: list[GateRow], score: int, missing_required: list[str], blockers: list[HardBlocker]) -> str:
    actions: list[str] = []
    if blockers:
        actions.append("- Resolve hard blockers before any user-facing launch.")
    for missing in missing_required[:5]:
        actions.append(f"- Add `{missing}` and rerun `openevalgate check`.")
    for gate in weak_gates[:5]:
        actions.append(f"- Close mitigation for {gate.gate}.")
    if not blockers and score < 70:
        actions.append("- Run in shadow mode until failed gates are remediated.")
    elif not blockers and score < 85:
        actions.append("- Limit rollout to a controlled launch cohort with explicit rollback criteria.")
    if not actions:
        actions.append("- Proceed with controlled launch review and monitor drift, quality, cost, resolution, and trust metrics.")
    return "\n".join(actions)


def _final_recommendation(recommendation: str, blockers: list[HardBlocker]) -> str:
    if blockers:
        return f"{recommendation}. Do not launch until hard blockers are resolved."
    return f"{recommendation}. Continue monitoring trust, durable resolution, tail risk, and rollback criteria."


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


def _eval_results_summary(root: Path) -> str:
    summary = summarize_eval_results(root)
    if summary is None:
        return "No eval results found. Candidate assistant execution results have not been fed back into this project yet."
    if summary.row_count == 0:
        return "eval_results.csv exists but has no result rows."

    lines = [
        f"- Total result rows: {summary.row_count}",
        f"- Latest run ID: {summary.latest_run_id or 'unknown'}",
        "- Candidate coverage: " + (", ".join(summary.candidates) if summary.candidates else "unknown"),
        f"- Pass rate: {_format_rate(summary.pass_rate)}",
        f"- Route match rate: {_format_rate(summary.route_match_rate)}",
        "- Failed case IDs: " + (", ".join(summary.failed_case_ids) if summary.failed_case_ids else "none"),
        "- Top failure categories: " + (_counter_summary(summary.failure_categories) if summary.failure_categories else "none"),
        f"- Workflow-route accuracy: {_format_rate(summary.workflow_route_accuracy)}",
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
    ]
    if summary.observed_output_paths:
        lines.append("- Observed output paths: " + ", ".join(summary.observed_output_paths[:8]))
    return "\n".join(lines)


def _safe_load_cases(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    try:
        return load_eval_cases(path)
    except Exception:  # noqa: BLE001 - report should still render with malformed eval YAML.
        return []


def _has_high_impact(cases: list[dict[str, Any]], action_path: Path) -> bool:
    if any(str(case.get("risk_tier", "")).lower() in {"high", "prohibited"} for case in cases):
        return True
    if action_path.is_file():
        return any(row.get("risk_tier", "").lower() in {"high", "prohibited"} for row in _read_csv(action_path))
    return False


def _high_risk_actions_without_controls(path: Path) -> list[str]:
    if not path.is_file():
        return []
    unsafe: list[str] = []
    for row in _read_csv(path):
        if row.get("risk_tier", "").lower() not in {"high", "prohibited"}:
            continue
        deterministic_gate = row.get("deterministic_gate", "").strip().lower()
        human_review = row.get("human_review_required", "").strip().lower()
        has_gate = deterministic_gate not in {"", "none", "n/a"}
        has_review = human_review == "true"
        if not has_gate and not has_review:
            unsafe.append(row.get("action", "unknown_action"))
    return unsafe


def _gate_missing_or_failed(statuses: dict[str, str], gate: str) -> bool:
    status = statuses.get(normalize_gate(gate))
    return status is None or status == "fail"


def _gate_not_passing(statuses: dict[str, str], gate: str) -> bool:
    return statuses.get(normalize_gate(gate)) != "pass"


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
