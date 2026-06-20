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
        evidence_package_sufficient=True,
        behavioral_evidence_state="empty",
        hard_blockers=[],
    )

    assert result.maximum_permitted_stage == "Shadow evaluation"
    assert result.recommendation == "Not ready for controlled launch"
    assert result.critical_control_status == "Not evaluated"


def test_missing_results_with_blocker_requires_documentation_remediation() -> None:
    result = assess_launch(
        evidence_completeness_score=100,
        evidence_package_sufficient=True,
        behavioral_evidence_state="not_provided",
        hard_blockers=[ROLLBACK_BLOCKER],
    )

    assert result.critical_control_status == "Fail"
    assert result.maximum_permitted_stage == "Documentation remediation"
    assert result.recommendation == "Not ready for shadow evaluation"


def test_invalid_results_are_not_treated_as_missing() -> None:
    result = assess_launch(
        evidence_completeness_score=100,
        evidence_package_sufficient=True,
        behavioral_evidence_state="invalid",
        hard_blockers=[],
    )

    assert result.behavioral_evidence_state == "invalid"
    assert result.recommendation == "Not ready"
    assert result.maximum_permitted_stage == "Documentation remediation"


def test_valid_results_with_blocker_are_not_ready_for_controlled_launch() -> None:
    result = assess_launch(
        evidence_completeness_score=100,
        evidence_package_sufficient=True,
        behavioral_evidence_state="available",
        hard_blockers=[ROLLBACK_BLOCKER],
    )

    assert result.critical_control_status == "Fail"
    assert result.maximum_permitted_stage == "Shadow evaluation or remediation"
    assert result.recommendation == "Not ready for controlled launch"


def test_valid_results_without_blockers_permit_bounded_controlled_launch() -> None:
    result = assess_launch(
        evidence_completeness_score=100,
        evidence_package_sufficient=True,
        behavioral_evidence_state="available",
        hard_blockers=[],
    )

    assert result.critical_control_status == "Pass"
    assert result.recommendation == "Ready for bounded controlled launch"


@pytest.mark.parametrize("score", [0, 49, 50, 84, 85, 100])
def test_score_alone_cannot_make_missing_results_launch_ready(score: int) -> None:
    result = assess_launch(
        evidence_completeness_score=score,
        evidence_package_sufficient=score >= 85,
        behavioral_evidence_state="not_provided",
        hard_blockers=[],
    )

    assert result.recommendation != "Ready for bounded controlled launch"


def test_incomplete_evidence_package_takes_precedence() -> None:
    result = assess_launch(
        evidence_completeness_score=84,
        evidence_package_sufficient=False,
        behavioral_evidence_state="available",
        hard_blockers=[],
    )

    assert result.maximum_permitted_stage == "Documentation remediation"
    assert result.recommendation == "Not ready for evaluation"


@pytest.mark.parametrize(
    ("score", "expected"),
    [(100, "Substantially complete"), (85, "Substantially complete"), (84, "Material gaps"), (50, "Material gaps"), (49, "Incomplete")],
)
def test_evidence_completeness_bands_have_no_deployment_language(
    score: int,
    expected: str,
) -> None:
    assert evidence_completeness_band(score) == expected
