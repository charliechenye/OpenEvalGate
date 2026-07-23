"""Deterministic machine-readable and review-card output."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from openevalgate import __version__
from openevalgate.assessment import assess_launch
from openevalgate.project_inspection import inspect_project
from openevalgate.provenance import RunIdentityInspection
from openevalgate.review_policy import evaluate_behavioral_sufficiency
from openevalgate.schema import ReviewMode, ValidationIssue, load_eval_cases, validate_eval_cases
from openevalgate.scorer import score_gates


OUTPUT_SCHEMA_VERSION = "1"


def validate_output(path: str | Path) -> dict[str, Any]:
    """Return the stable JSON envelope for golden eval-case validation."""

    target = Path(path)
    result = validate_eval_cases(target)
    return {
        "schema_version": OUTPUT_SCHEMA_VERSION,
        "tool": {"name": "openevalgate", "version": __version__},
        "command": "validate",
        "status": "valid" if result.valid else "invalid",
        "case_count": result.case_count,
        "issues": [_issue_payload(issue, target.parent) for issue in result.issues],
    }


def check_output(project_dir: str | Path) -> dict[str, Any]:
    """Return the stable JSON envelope for structural project validation."""

    root = Path(project_dir)
    inspection = inspect_project(root)
    issues = [*inspection.check.issues, *inspection.policy_issues]
    return {
        "schema_version": OUTPUT_SCHEMA_VERSION,
        "tool": {"name": "openevalgate", "version": __version__},
        "command": "check",
        "status": "valid" if inspection.valid else "invalid",
        "project": {"name": root.name},
        "required_files": {
            "missing": sorted(inspection.check.missing_required),
            "optional_present": sorted(inspection.check.present_optional),
        },
        "run_identity": _provenance_payload(inspection.run_identity_inspection, root),
        "issues": [_issue_payload(issue, root) for issue in issues],
    }


def report_output(project_dir: str | Path) -> dict[str, Any]:
    """Return a deterministic decision envelope without generated timestamps."""

    root = Path(project_dir)
    inspection = inspect_project(root)
    check = inspection.check
    cases = _safe_load_cases(root / "eval_cases.yaml")
    behavioral_sufficiency = evaluate_behavioral_sufficiency(
        root,
        identity_inspection=inspection.run_identity_inspection,
    )
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
        hard_blockers=inspection.hard_blockers,
    )
    recommendation = assessment.recommendation
    status = "blocked" if recommendation.startswith("Not ready") else "pass"
    all_issues = [*check.issues, *inspection.policy_issues, *behavioral_sufficiency.issues]
    return {
        "schema_version": OUTPUT_SCHEMA_VERSION,
        "tool": {"name": "openevalgate", "version": __version__},
        "command": "report",
        "status": status,
        "project": {
            "name": root.name,
            "system_name": _project_identity(root, cases)[0],
            "assistant_type": _project_identity(root, cases)[1],
        },
        "assessment": {
            "evidence_completeness_score": assessment.evidence_completeness_score,
            "evidence_band": assessment.evidence_band,
            "control_evidence_threshold_met": assessment.control_evidence_completeness_threshold_met,
            "behavioral_evidence_state": assessment.behavioral_evidence_state,
            "declared_review_mode": _mode_value(assessment.declared_review_mode),
            "effective_review_mode": _mode_value(assessment.effective_review_mode),
            "critical_control_status": assessment.critical_control_status,
            "maximum_permitted_stage": assessment.maximum_permitted_stage,
            "recommendation": recommendation,
            "recommended_next_actions": list(assessment.recommended_next_actions),
        },
        "behavioral_sufficiency": _behavioral_payload(assessment.behavioral_sufficiency),
        "run_identity": _provenance_payload(inspection.run_identity_inspection, root),
        "blockers": [
            {
                "id": blocker.id,
                "reason": blocker.reason,
                "evidence": blocker.evidence,
            }
            for blocker in sorted(inspection.hard_blockers, key=lambda item: item.id)
        ],
        "issues": [_issue_payload(issue, root) for issue in all_issues],
        "limitations": [
            "This is a bounded evidence assessment, not deployment authorization.",
            "The result is only as reliable as the supplied evidence.",
            "OpenEvalGate does not certify compliance or guarantee safe deployment.",
        ],
    }


def render_json(payload: dict[str, Any]) -> str:
    """Serialize an output payload with stable formatting."""

    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def render_card(payload: dict[str, Any]) -> str:
    """Render a compact review artifact for CI summaries and launch meetings."""

    assessment = payload.get("assessment", {})
    provenance = payload.get("run_identity", {})
    blockers = payload.get("blockers", [])
    actions = assessment.get("recommended_next_actions", [])
    lines = [
        f"# OpenEvalGate Decision Card: {payload.get('project', {}).get('system_name', 'Project')}",
        "",
        f"- **Status:** {str(payload.get('status', 'unknown')).capitalize()}",
        f"- **Recommendation:** {assessment.get('recommendation', 'Not available')}",
        f"- **Review mode:** {assessment.get('effective_review_mode') or 'Not configured'}",
        f"- **Evidence completeness:** {assessment.get('evidence_completeness_score', 'unknown')}/100",
        f"- **Behavioral evidence:** {assessment.get('behavioral_evidence_state', 'unknown')}",
        f"- **Critical-control status:** {assessment.get('critical_control_status', 'unknown')}",
        f"- **Provenance:** {provenance.get('status', 'unknown')}",
        f"- **Freshness:** {provenance.get('classification', {}).get('freshness', 'unknown')}",
        f"- **Recency:** {provenance.get('classification', {}).get('recency', 'unknown')}",
        "",
        "## Blockers",
    ]
    if blockers:
        lines.extend(f"- `{item['id']}` — {item['reason']}" for item in blockers)
    else:
        lines.append("- None identified; absence of a blocker is not authorization.")
    lines.extend(["", "## Next actions"])
    if actions:
        lines.extend(f"- {action}" for action in actions)
    else:
        lines.append("- No additional actions recorded.")
    lines.extend(
        [
            "",
            "> This card is a deterministic evidence assessment. It is not compliance certification, deployment authorization, or a safety guarantee.",
            "",
        ]
    )
    return "\n".join(lines)


def _project_identity(root: Path, cases: list[dict[str, Any]]) -> tuple[str, str]:
    system_name = root.name.replace("_", " ").title()
    assistant_type = cases[0].get("assistant_type", "unknown") if cases else "unknown"
    prd = root / "assistant_prd.md"
    if prd.is_file():
        text = prd.read_text(encoding="utf-8")
        title = re.search(r"^#\s+(.+)$", text, flags=re.MULTILINE)
        if title:
            system_name = title.group(1).strip()
        match = re.search(r"\*\*Assistant type:\*\*\s*(.+)", text)
        if match:
            assistant_type = match.group(1).strip()
    return system_name, assistant_type


def _safe_load_cases(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    try:
        return load_eval_cases(path)
    except Exception:  # noqa: BLE001 - output should remain useful for malformed projects.
        return []


def _non_behavioral_issues(issues: list[ValidationIssue]) -> list[ValidationIssue]:
    return [issue for issue in issues if issue.source not in {"eval_results", "review_policy"}]


def _mode_value(value: ReviewMode | None) -> str | None:
    return value.value if value is not None else None


def _issue_payload(issue: ValidationIssue, root: Path) -> dict[str, str]:
    return {
        "path": _relative_path(issue.path, root),
        "message": issue.message,
        "source": issue.source,
    }


def _provenance_payload(inspection: RunIdentityInspection, root: Path) -> dict[str, Any]:
    identity = inspection.identity
    identity_payload: dict[str, Any] | None = None
    if identity is not None:
        identity_payload = {
            "run_id": identity.run_id,
            "status": identity.run_status,
            "candidate_id": identity.candidate_id,
            "candidate_version": identity.candidate_version,
            "evaluator": {
                "kind": identity.evaluator.kind,
                "id": identity.evaluator.evaluator_id,
                "version": identity.evaluator.evaluator_version,
            },
            "results_path": _relative_path(str(identity.results_path), root),
        }
    return {
        "status": inspection.status.value,
        "manifest_path": _relative_path(str(inspection.manifest_path), root)
        if inspection.manifest_path
        else None,
        "review_context_path": _relative_path(str(inspection.review_context_path), root)
        if inspection.review_context_path
        else None,
        "classification": {
            "validity": inspection.classification.validity.value,
            "freshness": inspection.classification.freshness.value,
            "recency": inspection.classification.recency.value,
            "assurance": inspection.classification.assurance.value,
        },
        "identity": identity_payload,
        "findings": [
            {
                "id": finding.id,
                "path": _relative_path(finding.path, root),
                "message": finding.message,
            }
            for finding in inspection.findings
        ],
    }


def _behavioral_payload(value: Any) -> dict[str, Any]:
    return {
        "selected_run_id": value.selected_run_id,
        "selected_candidate": value.selected_candidate,
        "selected_row_count": value.selected_row_count,
        "expected_case_count": value.expected_case_count,
        "observed_case_count": value.observed_case_count,
        "case_coverage": value.case_coverage,
        "missing_case_ids": list(value.missing_case_ids),
        "expected_critical_case_count": value.expected_critical_case_count,
        "observed_critical_case_count": value.observed_critical_case_count,
        "critical_case_coverage": value.critical_case_coverage,
        "missing_critical_case_ids": list(value.missing_critical_case_ids),
        "failed_critical_case_ids": list(value.failed_critical_case_ids),
        "coverage_sufficient": value.coverage_sufficient,
        "thresholds_satisfied": value.thresholds_satisfied,
        "behavioral_invariants_satisfied": value.behavioral_invariants_satisfied,
        "sufficient_for_requested_mode": value.sufficient_for_requested_mode,
        "thresholds": [
            {
                "metric": item.metric,
                "actual": item.actual_value,
                "comparator": item.comparator,
                "configured_threshold": item.configured_threshold,
                "status": item.status,
            }
            for item in value.threshold_outcomes
        ],
        "invariants": [
            {"id": item.invariant_id, "status": item.status, "reason": item.reason}
            for item in value.invariant_outcomes
        ],
    }


def _relative_path(value: str, root: Path) -> str:
    if not value:
        return value
    candidate = Path(value)
    if not candidate.is_absolute():
        return value
    try:
        return candidate.resolve(strict=False).relative_to(root.resolve(strict=False)).as_posix()
    except ValueError:
        return "<outside-project>"
