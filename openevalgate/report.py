"""Markdown launch readiness report generation."""

from __future__ import annotations

import csv
import re
from collections import Counter
from pathlib import Path
from typing import Any

from openevalgate.eval_results import summarize_eval_results
from openevalgate.schema import load_eval_cases
from openevalgate.scorer import GateRow, score_gates
from openevalgate.validator import check_project


def generate_report(project_dir: str | Path) -> str:
    """Generate a deterministic Markdown launch readiness report."""

    root = Path(project_dir)
    check = check_project(root)
    cases = load_eval_cases(root / "eval_cases.yaml") if (root / "eval_cases.yaml").exists() else []
    gates = parse_launch_gate_review(root / "launch_gate_review.md") if (root / "launch_gate_review.md").exists() else []
    score = score_gates(gates, boundary_coverage_status=_boundary_coverage_status(cases))
    system_name, assistant_type = _project_identity(root, cases)

    sections = [
        f"# Launch Readiness Report: {system_name}",
        "",
        f"- **System name:** {system_name}",
        f"- **Assistant type:** {assistant_type}",
        f"- **Launch recommendation:** {score.recommendation}",
        f"- **Overall readiness score:** {score.score}/100",
        "",
        "## Passed Gates",
        _gate_list(score.passed_gates, empty="No passed gates recorded."),
        "",
        "## Failed Or Weak Gates",
        _gate_list(score.weak_gates, empty="No weak gates recorded."),
        "",
        "## Required Mitigations",
        _mitigation_list(score.weak_gates),
        "",
        "## Top Production Risks",
        _top_risks(cases, root),
        "",
        "## Suggested Next Actions",
        _next_actions(score.weak_gates, score.score, check.missing_required),
        "",
        "## Checklist Summary",
        _checklist_summary(gates, score.not_applicable_gates, check.missing_required),
        "",
        "## Eval Set Summary",
        _eval_summary(cases),
        "",
        "## Eval Results Summary",
        _eval_results_summary(root),
        "",
        "## Model Arena Summary",
        _csv_summary(root / "model_arena_scorecard.csv", "model", "No model arena scorecard found."),
        "",
        "## Action Risk Summary",
        _csv_summary(root / "action_risk_matrix.csv", "action", "No action risk matrix found."),
        "",
        "## Output Critic Summary",
        _csv_summary(root / "output_critic_rubric.csv", "dimension", "No output critic rubric found."),
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


def _gate_list(gates: list[GateRow], empty: str) -> str:
    if not gates:
        return empty
    return "\n".join(f"- {gate.gate}: {gate.status}" for gate in gates)


def _mitigation_list(gates: list[GateRow]) -> str:
    mitigations = [f"- {gate.gate}: {gate.mitigation}" for gate in gates if gate.mitigation and gate.mitigation.lower() not in {"none", "n/a"}]
    return "\n".join(mitigations) if mitigations else "No required mitigations recorded."


def _top_risks(cases: list[dict[str, Any]], root: Path) -> str:
    risk_counts = Counter(str(case.get("risk_tier", "unknown")) for case in cases)
    risks: list[str] = []
    for tier in ("prohibited", "high", "medium"):
        count = risk_counts.get(tier, 0)
        if count:
            risks.append(f"- {count} eval case(s) marked {tier} risk.")

    action_path = root / "action_risk_matrix.csv"
    if action_path.is_file():
        high_actions = [
            row.get("action", "")
            for row in _read_csv(action_path)
            if row.get("risk_tier", "").lower() in {"high", "prohibited"}
        ]
        if high_actions:
            risks.append(f"- High-risk actions require deterministic gates: {', '.join(high_actions[:5])}.")

    return "\n".join(risks) if risks else "No high or prohibited production risks recorded."


def _next_actions(weak_gates: list[GateRow], score: int, missing_required: list[str]) -> str:
    actions: list[str] = []
    for missing in missing_required:
        actions.append(f"- Add missing required launch file: `{missing}`.")
    for gate in weak_gates[:5]:
        actions.append(f"- Close mitigation for {gate.gate}.")
    if score < 70:
        actions.append("- Run in shadow mode until failed gates are remediated.")
    elif score < 85:
        actions.append("- Limit rollout to a controlled launch cohort with explicit rollback criteria.")
    if not actions:
        actions.append("- Proceed with controlled launch review and monitor drift, quality, cost, and escalation rates.")
    return "\n".join(actions)


def _checklist_summary(gates: list[GateRow], not_applicable: list[GateRow], missing_required: list[str]) -> str:
    counts = Counter(gate.status for gate in gates)
    lines = [
        f"- Pass: {counts.get('pass', 0)}",
        f"- Partial: {counts.get('partial', 0)}",
        f"- Fail: {counts.get('fail', 0)}",
        f"- Not applicable: {counts.get('not_applicable', 0)}",
    ]
    if not_applicable:
        lines.append("- Not applicable gates: " + ", ".join(gate.gate for gate in not_applicable))
    if missing_required:
        lines.append("- Missing required files: " + ", ".join(missing_required))
    return "\n".join(lines)


def _eval_summary(cases: list[dict[str, Any]]) -> str:
    if not cases:
        return "No eval cases found."
    case_types = Counter(str(case.get("case_type", "unknown")) for case in cases)
    risk_tiers = Counter(str(case.get("risk_tier", "unknown")) for case in cases)
    routes = Counter(str(case.get("expected_route", "unknown")) for case in cases)
    return "\n".join(
        [
            f"- Total cases: {len(cases)}",
            "- Case types: " + _counter_summary(case_types),
            "- Risk tiers: " + _counter_summary(risk_tiers),
            "- Expected routes: " + _counter_summary(routes),
        ]
    )


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
    ]
    if summary.observed_output_paths:
        lines.append("- Observed output paths: " + ", ".join(summary.observed_output_paths[:8]))
    return "\n".join(lines)


def _boundary_coverage_status(cases: list[dict[str, Any]]) -> str:
    case_types = {str(case.get("case_type", "")) for case in cases}
    has_boundary = "synthetic_boundary" in case_types
    has_adversarial = "adversarial" in case_types
    if has_boundary and has_adversarial:
        return "pass"
    if has_boundary or has_adversarial:
        return "partial"
    return "fail"


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
