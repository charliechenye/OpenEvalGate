from dataclasses import replace

import pytest

from openevalgate.assessment import assess_launch, evidence_completeness_band
from openevalgate.review_policy import BehavioralSufficiency, InvariantOutcome
from openevalgate.schema import HardBlocker, ReviewMode


BLOCKER = HardBlocker("missing_rollback", "Rollback is missing.", "Rollback gate")


def _sufficiency(
    mode: ReviewMode | None = ReviewMode.SHADOW_LAUNCH,
    *,
    state: str = "available",
    policy_present: bool = True,
    policy_valid: bool = True,
    selected_rows: int = 1,
    sufficient: bool = True,
    invariant_status: str = "pass",
) -> BehavioralSufficiency:
    return BehavioralSufficiency(
        state, mode if policy_present and policy_valid else None, mode,
        policy_present, policy_valid, "run" if selected_rows else "run",
        "candidate" if selected_rows else "candidate", selected_rows,
        1, 1 if selected_rows else 0, 1.0 if selected_rows else 0.0,
        1 if selected_rows else 0, () if selected_rows else ("case",), (),
        0, 0, None, (), (), (), sufficient, (),
        (
            InvariantOutcome("no_prohibited_actions", invariant_status, "reason"),
            InvariantOutcome("all_critical_cases_pass", "not_applicable", "reason"),
            InvariantOutcome("required_escalations_pass", "not_applicable", "reason"),
        ),
        True, invariant_status == "pass", sufficient, (),
    )


def _assess(sufficiency: BehavioralSufficiency, *, score: int = 100, valid: bool = True, blockers: list[HardBlocker] | None = None):
    return assess_launch(
        evidence_completeness_score=score,
        project_evidence_valid=valid,
        behavioral_sufficiency=sufficiency,
        hard_blockers=blockers or [],
    )


def test_documentation_mode_is_capped() -> None:
    result = _assess(_sufficiency(ReviewMode.DOCUMENTATION))
    assert result.maximum_permitted_stage == "Documentation review"
    assert result.recommendation == "Documentation review complete"
    assert result.critical_control_status != "Pass"


def test_incomplete_documentation_requires_remediation() -> None:
    result = _assess(_sufficiency(ReviewMode.DOCUMENTATION), score=84)
    assert result.maximum_permitted_stage == "Documentation remediation"
    assert result.recommendation == "Not ready to complete documentation review"


@pytest.mark.parametrize("state", ["not_provided", "empty"])
def test_shadow_mode_allows_missing_or_empty_results(state: str) -> None:
    result = _assess(_sufficiency(state=state, selected_rows=0))
    assert result.maximum_permitted_stage == "Shadow evaluation"
    assert result.recommendation == "Ready for bounded shadow evaluation"
    assert result.critical_control_status == "Not evaluated"


def test_shadow_mode_rejects_invalid_results_and_blockers() -> None:
    invalid = _assess(_sufficiency(state="invalid", selected_rows=0))
    blocked = _assess(_sufficiency(), blockers=[BLOCKER])
    assert invalid.maximum_permitted_stage == "Documentation remediation"
    assert blocked.maximum_permitted_stage == "Documentation remediation"


def test_invalid_policy_has_no_shadow_fallback() -> None:
    invalid = replace(
        _sufficiency(None), policy_present=True, policy_valid=False,
        declared_mode=None, effective_mode=None, sufficient_for_requested_mode=False,
    )
    result = _assess(invalid)
    assert result.maximum_permitted_stage == "Documentation remediation"
    assert "Repair and revalidate review_policy.yaml." in result.recommended_next_actions


@pytest.mark.parametrize("state", ["not_provided", "empty", "invalid"])
def test_controlled_mode_requires_valid_results(state: str) -> None:
    result = _assess(_sufficiency(ReviewMode.CONTROLLED_LAUNCH, state=state, selected_rows=0, sufficient=False))
    assert result.maximum_permitted_stage == "Shadow evaluation"
    assert result.recommendation == "Not ready for controlled launch"


def test_controlled_mode_zero_scope_rows_fails_closed() -> None:
    result = _assess(_sufficiency(ReviewMode.CONTROLLED_LAUNCH, selected_rows=0, sufficient=False))
    assert result.maximum_permitted_stage == "Shadow evaluation with remediation"
    assert "Provide matching result rows for the selected run and candidate." in result.recommended_next_actions


def test_controlled_mode_failure_and_hard_blocker_precedence() -> None:
    failed = _sufficiency(
        ReviewMode.CONTROLLED_LAUNCH, sufficient=False, invariant_status="fail"
    )
    result = _assess(failed, blockers=[BLOCKER])
    assert result.maximum_permitted_stage == "Shadow evaluation with remediation"
    assert result.critical_control_status == "Fail"
    assert result.recommended_next_actions == ["Remediate known hard blockers."]


def test_controlled_mode_can_pass_only_when_every_requirement_passes() -> None:
    result = _assess(_sufficiency(ReviewMode.CONTROLLED_LAUNCH))
    assert result.maximum_permitted_stage == "Controlled launch"
    assert result.recommendation == "Ready for bounded controlled launch"
    assert result.critical_control_status == "Pass"


def test_incomplete_control_evidence_has_highest_precedence() -> None:
    result = _assess(_sufficiency(ReviewMode.CONTROLLED_LAUNCH), score=84)
    assert result.maximum_permitted_stage == "Documentation remediation"
    assert result.recommendation == "Not ready for shadow evaluation"


@pytest.mark.parametrize(
    ("score", "expected"),
    [(100, "Substantially complete"), (85, "Substantially complete"), (84, "Material gaps"), (50, "Material gaps"), (49, "Incomplete")],
)
def test_evidence_completeness_bands(score: int, expected: str) -> None:
    assert evidence_completeness_band(score) == expected
