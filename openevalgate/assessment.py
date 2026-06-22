"""Deterministic launch assessment independent from report rendering."""

from __future__ import annotations

from openevalgate.review_policy import BehavioralSufficiency
from openevalgate.schema import HardBlocker, LaunchAssessment, ReviewMode


EVIDENCE_SUFFICIENCY_SCORE = 85


def assess_launch(
    *,
    evidence_completeness_score: int,
    project_evidence_valid: bool,
    behavioral_sufficiency: BehavioralSufficiency,
    hard_blockers: list[HardBlocker],
) -> LaunchAssessment:
    """Apply mode-aware launch precedence to already evaluated inputs."""

    sufficient_control = (
        evidence_completeness_score >= EVIDENCE_SUFFICIENCY_SCORE
        and project_evidence_valid
    )
    mode = behavioral_sufficiency.effective_mode
    state = behavioral_sufficiency.behavioral_evidence_state
    actions: list[str] = []

    if not sufficient_control:
        actions.append("Complete missing or invalid control-evidence requirements.")
    if not behavioral_sufficiency.policy_valid:
        actions.append("Repair and revalidate review_policy.yaml.")
    if state == "invalid":
        actions.append("Repair and revalidate eval_results.csv.")
    if hard_blockers:
        actions.append("Remediate known hard blockers.")

    if mode == ReviewMode.DOCUMENTATION:
        if sufficient_control:
            stage, recommendation = "Documentation review", "Documentation review complete"
        else:
            stage = "Documentation remediation"
            recommendation = "Not ready to complete documentation review"
    elif not sufficient_control:
        stage, recommendation = "Documentation remediation", "Not ready for shadow evaluation"
    elif not behavioral_sufficiency.policy_valid or mode is None:
        stage, recommendation = "Documentation remediation", "Not ready for shadow evaluation"
    elif mode == ReviewMode.SHADOW_LAUNCH:
        if state == "invalid" or hard_blockers:
            stage, recommendation = "Documentation remediation", "Not ready for shadow evaluation"
        else:
            stage, recommendation = "Shadow evaluation", "Ready for bounded shadow evaluation"
            if state in {"not_provided", "empty"}:
                actions.append("Run shadow evaluations and provide valid empirical result rows.")
    else:
        assert mode == ReviewMode.CONTROLLED_LAUNCH
        if state in {"not_provided", "empty", "invalid"}:
            stage, recommendation = "Shadow evaluation", "Not ready for controlled launch"
        elif hard_blockers:
            stage = "Shadow evaluation with remediation"
            recommendation = "Not ready for controlled launch"
        elif not behavioral_sufficiency.selected_run_id or not behavioral_sufficiency.selected_candidate:
            stage = "Shadow evaluation with remediation"
            recommendation = "Not ready for controlled launch"
            actions.append("Provide a selected run and candidate for controlled-launch review.")
        elif behavioral_sufficiency.selected_row_count == 0:
            stage = "Shadow evaluation with remediation"
            recommendation = "Not ready for controlled launch"
            actions.append("Provide matching result rows for the selected run and candidate.")
        elif not behavioral_sufficiency.sufficient_for_requested_mode:
            stage = "Shadow evaluation with remediation"
            recommendation = "Not ready for controlled launch"
            _append_behavioral_actions(actions, behavioral_sufficiency)
        else:
            stage = "Controlled launch"
            recommendation = "Ready for bounded controlled launch"

    critical_status = _critical_control_status(
        behavioral_sufficiency, hard_blockers, stage
    )
    return LaunchAssessment(
        evidence_completeness_score=evidence_completeness_score,
        evidence_band=evidence_completeness_band(evidence_completeness_score),
        control_evidence_completeness_threshold_met=sufficient_control,
        behavioral_evidence_state=state,
        declared_review_mode=behavioral_sufficiency.declared_mode,
        effective_review_mode=mode,
        behavioral_sufficiency=behavioral_sufficiency,
        critical_control_status=critical_status,
        maximum_permitted_stage=stage,
        recommendation=recommendation,
        recommended_next_actions=_deduplicate(actions),
        hard_blockers=hard_blockers,
    )


def _append_behavioral_actions(
    actions: list[str], sufficiency: BehavioralSufficiency
) -> None:
    if sufficiency.missing_case_ids:
        actions.append("Add result coverage for missing eval cases.")
    if sufficiency.observed_cases_below_trial_depth:
        actions.append("Add required trial depth for represented under-covered eval cases.")
    if sufficiency.missing_critical_case_ids:
        actions.append("Cover every required critical eval case.")
    if sufficiency.critical_cases_below_trial_depth:
        actions.append("Add required trial depth for critical eval cases.")
    if sufficiency.failed_critical_case_ids:
        actions.append("Remediate failing critical eval cases.")
    if any(item.status in {"fail", "not_evaluated"} for item in sufficiency.invariant_outcomes):
        actions.append("Resolve failed behavioral safety invariants.")
    if any(item.status in {"fail", "not_evaluated"} for item in sufficiency.threshold_outcomes):
        actions.append("Meet the configured behavioral thresholds.")


def evidence_completeness_band(score: int) -> str:
    if score >= 85:
        return "Substantially complete"
    if score >= 50:
        return "Material gaps"
    return "Incomplete"


def behavioral_evidence_display(state: str) -> str:
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
    sufficiency: BehavioralSufficiency,
    blockers: list[HardBlocker],
    stage: str,
) -> str:
    if blockers:
        return "Fail"
    if stage == "Controlled launch":
        return "Pass"
    if sufficiency.behavioral_evidence_state in {"not_provided", "empty", "invalid"}:
        return "Not evaluated"
    if sufficiency.effective_mode == ReviewMode.CONTROLLED_LAUNCH:
        statuses = {item.status for item in sufficiency.invariant_outcomes}
        if "fail" in statuses:
            return "Fail"
        if "not_evaluated" in statuses:
            return "Not evaluated"
    return "No known blockers detected"


def _deduplicate(actions: list[str]) -> list[str]:
    return list(dict.fromkeys(actions))
