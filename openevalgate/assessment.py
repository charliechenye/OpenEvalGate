"""Deterministic launch assessment independent from report rendering."""

from __future__ import annotations

from openevalgate.schema import HardBlocker, LaunchAssessment


EVIDENCE_SUFFICIENCY_SCORE = 85
BEHAVIORAL_EVIDENCE_STATES = {"not_provided", "empty", "invalid", "available"}


def assess_launch(
    *,
    evidence_completeness_score: int,
    project_evidence_valid: bool,
    behavioral_evidence_state: str,
    hard_blockers: list[HardBlocker],
) -> LaunchAssessment:
    """Apply the launch decision table to validated assessment inputs."""

    if behavioral_evidence_state not in BEHAVIORAL_EVIDENCE_STATES:
        raise ValueError(f"Unknown behavioral evidence state: {behavioral_evidence_state}")

    control_evidence_completeness_threshold_met = (
        evidence_completeness_score >= EVIDENCE_SUFFICIENCY_SCORE
        and project_evidence_valid
    )
    critical_control_status = _critical_control_status(
        behavioral_evidence_state,
        hard_blockers,
    )
    next_actions: list[str] = []

    if behavioral_evidence_state == "invalid":
        next_actions.append("Repair and revalidate eval_results.csv.")
    if not control_evidence_completeness_threshold_met:
        next_actions.append("Complete missing or invalid control-evidence requirements.")
    if hard_blockers:
        next_actions.append("Remediate known hard blockers.")

    if not control_evidence_completeness_threshold_met:
        maximum_permitted_stage = "Documentation remediation"
        recommendation = "Not ready for evaluation"
    elif behavioral_evidence_state == "invalid":
        maximum_permitted_stage = "Documentation remediation"
        recommendation = "Not ready"
    elif behavioral_evidence_state in {"not_provided", "empty"}:
        if hard_blockers:
            maximum_permitted_stage = "Documentation remediation"
            recommendation = "Not ready for shadow evaluation"
        else:
            maximum_permitted_stage = "Shadow evaluation"
            recommendation = "Not ready for controlled launch"
            next_actions.append("Run shadow evaluations and provide valid empirical result rows.")
    elif hard_blockers:
        maximum_permitted_stage = "Shadow evaluation with remediation"
        recommendation = "Not ready for controlled launch"
    else:
        maximum_permitted_stage = "Shadow evaluation"
        recommendation = "Controlled-launch readiness not yet determined"
        next_actions.append(
            "Verify required-slice coverage and behavioral thresholds before controlled launch."
        )

    return LaunchAssessment(
        evidence_completeness_score=evidence_completeness_score,
        evidence_band=evidence_completeness_band(evidence_completeness_score),
        control_evidence_completeness_threshold_met=(
            control_evidence_completeness_threshold_met
        ),
        behavioral_evidence_state=behavioral_evidence_state,
        critical_control_status=critical_control_status,
        maximum_permitted_stage=maximum_permitted_stage,
        recommendation=recommendation,
        recommended_next_actions=next_actions,
        hard_blockers=hard_blockers,
    )


def evidence_completeness_band(score: int) -> str:
    """Describe evidence-package completeness without deployment semantics."""

    if score >= 85:
        return "Substantially complete"
    if score >= 50:
        return "Material gaps"
    return "Incomplete"


def behavioral_evidence_display(state: str) -> str:
    """Return the required human-readable behavioral-evidence wording."""

    displays = {
        "not_provided": "Not evaluated — no results provided.",
        "empty": "Not evaluated — results file contains no rows.",
        "invalid": "Invalid — results could not be validated.",
        "available": "Evaluated — valid empirical rows are available.",
    }
    try:
        return displays[state]
    except KeyError as exc:
        raise ValueError(f"Unknown behavioral evidence state: {state}") from exc


def _critical_control_status(
    behavioral_evidence_state: str,
    hard_blockers: list[HardBlocker],
) -> str:
    if hard_blockers:
        return "Fail"
    if behavioral_evidence_state == "available":
        return "No known blockers detected"
    return "Not evaluated"
