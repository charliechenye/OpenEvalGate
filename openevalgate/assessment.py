"""Deterministic launch assessment independent from report rendering."""

from __future__ import annotations

from openevalgate.schema import HardBlocker, LaunchAssessment


EVIDENCE_SUFFICIENCY_SCORE = 85
BEHAVIORAL_EVIDENCE_STATES = {"not_provided", "empty", "invalid", "available"}


def assess_launch(
    *,
    evidence_completeness_score: int,
    evidence_package_sufficient: bool,
    behavioral_evidence_state: str,
    hard_blockers: list[HardBlocker],
) -> LaunchAssessment:
    """Apply the launch decision table to validated assessment inputs."""

    if behavioral_evidence_state not in BEHAVIORAL_EVIDENCE_STATES:
        raise ValueError(f"Unknown behavioral evidence state: {behavioral_evidence_state}")

    critical_control_status = _critical_control_status(
        behavioral_evidence_state,
        hard_blockers,
    )

    if not evidence_package_sufficient:
        maximum_permitted_stage = "Documentation remediation"
        recommendation = "Not ready for evaluation"
        next_action = "Complete required evidence and close evidence-package gaps."
    elif behavioral_evidence_state == "invalid":
        maximum_permitted_stage = "Documentation remediation"
        recommendation = "Not ready"
        next_action = "Repair and revalidate eval_results.csv."
    elif behavioral_evidence_state in {"not_provided", "empty"}:
        if hard_blockers:
            maximum_permitted_stage = "Documentation remediation"
            recommendation = "Not ready for shadow evaluation"
            next_action = "Remediate known hard blockers before shadow evaluation."
        else:
            maximum_permitted_stage = "Shadow evaluation"
            recommendation = "Not ready for controlled launch"
            next_action = "Run shadow evaluations and provide valid empirical result rows."
    elif hard_blockers:
        maximum_permitted_stage = "Shadow evaluation or remediation"
        recommendation = "Not ready for controlled launch"
        next_action = "Remediate hard blockers and rerun the affected evaluations."
    else:
        maximum_permitted_stage = "Controlled launch, subject to later threshold policy"
        recommendation = "Ready for bounded controlled launch"
        next_action = "Conduct a bounded controlled launch with monitoring and rollback."

    return LaunchAssessment(
        evidence_completeness_score=evidence_completeness_score,
        evidence_band=evidence_completeness_band(evidence_completeness_score),
        evidence_package_sufficient=evidence_package_sufficient,
        behavioral_evidence_state=behavioral_evidence_state,
        critical_control_status=critical_control_status,
        maximum_permitted_stage=maximum_permitted_stage,
        recommendation=recommendation,
        recommended_next_action=next_action,
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
        return "Pass"
    return "Not evaluated"
