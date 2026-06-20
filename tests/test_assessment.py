import pytest

from openevalgate.assessment import assess_launch, evidence_completeness_band
from openevalgate.schema import HardBlocker


ROLLBACK_BLOCKER = HardBlocker(
    "missing_rollback",
    "Rollback gate is missing or not passing.",
    "Rollback gate",
)


def test_complete_evidence_without_results_permits_shadow_evaluation_only() -> None:
    result = assess_launch(
        evidence_completeness_score=100,
        project_evidence_valid=True,
        behavioral_evidence_state="empty",
        hard_blockers=[],
    )

    assert result.maximum_permitted_stage == "Shadow evaluation"
    assert result.recommendation == "Not ready for controlled launch"
    assert result.critical_control_status == "Not evaluated"


def test_missing_results_with_blocker_requires_documentation_remediation() -> None:
    result = assess_launch(
        evidence_completeness_score=100,
        project_evidence_valid=True,
        behavioral_evidence_state="not_provided",
        hard_blockers=[ROLLBACK_BLOCKER],
    )

    assert result.critical_control_status == "Fail"
    assert result.maximum_permitted_stage == "Documentation remediation"
    assert result.recommendation == "Not ready for shadow evaluation"


def test_invalid_results_are_not_treated_as_missing() -> None:
    result = assess_launch(
        evidence_completeness_score=100,
        project_evidence_valid=True,
        behavioral_evidence_state="invalid",
        hard_blockers=[],
    )

    assert result.behavioral_evidence_state == "invalid"
    assert result.recommendation == "Not ready"
    assert result.maximum_permitted_stage == "Documentation remediation"


def test_valid_results_with_blocker_are_not_ready_for_controlled_launch() -> None:
    result = assess_launch(
        evidence_completeness_score=100,
        project_evidence_valid=True,
        behavioral_evidence_state="available",
        hard_blockers=[ROLLBACK_BLOCKER],
    )

    assert result.critical_control_status == "Fail"
    assert result.maximum_permitted_stage == "Shadow evaluation with remediation"
    assert result.recommendation == "Not ready for controlled launch"


def test_valid_results_without_blockers_remain_shadow_only() -> None:
    result = assess_launch(
        evidence_completeness_score=100,
        project_evidence_valid=True,
        behavioral_evidence_state="available",
        hard_blockers=[],
    )

    assert result.critical_control_status == "No known blockers detected"
    assert result.maximum_permitted_stage == "Shadow evaluation"
    assert result.recommendation == "Controlled-launch readiness not yet determined"
    assert result.recommended_next_actions == [
        "Verify required-slice coverage and behavioral thresholds before controlled launch."
    ]


@pytest.mark.parametrize("score", [0, 49, 50, 84, 85, 100])
def test_score_alone_cannot_make_missing_results_launch_ready(score: int) -> None:
    result = assess_launch(
        evidence_completeness_score=score,
        project_evidence_valid=True,
        behavioral_evidence_state="not_provided",
        hard_blockers=[],
    )

    assert result.recommendation != "Ready for bounded controlled launch"


def test_incomplete_evidence_package_takes_precedence() -> None:
    result = assess_launch(
        evidence_completeness_score=84,
        project_evidence_valid=True,
        behavioral_evidence_state="available",
        hard_blockers=[],
    )

    assert result.maximum_permitted_stage == "Documentation remediation"
    assert result.recommendation == "Not ready for evaluation"


def test_score_84_is_insufficient_for_shadow_evaluation() -> None:
    result = assess_launch(
        evidence_completeness_score=84,
        project_evidence_valid=True,
        behavioral_evidence_state="available",
        hard_blockers=[],
    )

    assert not result.control_evidence_completeness_threshold_met


def test_score_85_is_sufficient_for_shadow_evaluation() -> None:
    result = assess_launch(
        evidence_completeness_score=85,
        project_evidence_valid=True,
        behavioral_evidence_state="available",
        hard_blockers=[],
    )

    assert result.control_evidence_completeness_threshold_met
    assert result.maximum_permitted_stage == "Shadow evaluation"


def test_project_validation_error_makes_score_85_insufficient() -> None:
    result = assess_launch(
        evidence_completeness_score=85,
        project_evidence_valid=False,
        behavioral_evidence_state="available",
        hard_blockers=[],
    )

    assert not result.control_evidence_completeness_threshold_met
    assert result.maximum_permitted_stage == "Documentation remediation"


def test_invalid_results_and_incomplete_package_accumulate_actions() -> None:
    result = assess_launch(
        evidence_completeness_score=84,
        project_evidence_valid=False,
        behavioral_evidence_state="invalid",
        hard_blockers=[ROLLBACK_BLOCKER],
    )

    assert result.recommended_next_actions == [
        "Repair and revalidate eval_results.csv.",
        "Complete missing or invalid control-evidence requirements.",
        "Remediate known hard blockers.",
    ]


@pytest.mark.parametrize(
    ("score", "project_valid", "state", "blockers"),
    [
        (100, True, "available", []),
        (100, True, "available", [ROLLBACK_BLOCKER]),
        (100, True, "empty", []),
        (84, True, "available", []),
    ],
)
def test_no_assessment_path_authorizes_controlled_launch(
    score: int,
    project_valid: bool,
    state: str,
    blockers: list[HardBlocker],
) -> None:
    result = assess_launch(
        evidence_completeness_score=score,
        project_evidence_valid=project_valid,
        behavioral_evidence_state=state,
        hard_blockers=blockers,
    )

    assert result.recommendation != "Ready for bounded controlled launch"
    assert result.maximum_permitted_stage != "Controlled launch"
    assert result.critical_control_status != "Pass"


@pytest.mark.parametrize(
    ("score", "expected"),
    [(100, "Substantially complete"), (85, "Substantially complete"), (84, "Material gaps"), (50, "Material gaps"), (49, "Incomplete")],
)
def test_evidence_completeness_bands_have_no_deployment_language(
    score: int,
    expected: str,
) -> None:
    assert evidence_completeness_band(score) == expected
