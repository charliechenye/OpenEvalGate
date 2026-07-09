from pathlib import Path

import pytest
import yaml

from openevalgate.provenance import RunIdentityStatus, inspect_run_identity


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / "spec" / "fixtures" / "provenance" / "v1"

EXPECTED_STATUS = {
    "aborted-run": RunIdentityStatus.COMPLETE,
    "candidate-alias-mismatch": RunIdentityStatus.INVALID,
    "contradictory-duplicate-resource": RunIdentityStatus.INVALID,
    "duplicate-artifact-id": RunIdentityStatus.INVALID,
    "duplicate-current-resource": RunIdentityStatus.COMPLETE,
    "duplicate-historical-resource": RunIdentityStatus.INVALID,
    "duplicate-hybrid-component-id": RunIdentityStatus.INVALID,
    "duplicate-normalized-artifact-path": RunIdentityStatus.INVALID,
    "duplicate-singleton-role": RunIdentityStatus.INVALID,
    "empty-artifact-index": RunIdentityStatus.INVALID,
    "evaluator-alias-mismatch": RunIdentityStatus.INVALID,
    "expired-evidence": RunIdentityStatus.COMPLETE,
    "failed-run": RunIdentityStatus.COMPLETE,
    "freshness-unknown-missing-canonical-mirror": RunIdentityStatus.COMPLETE,
    "freshness-unknown-missing-current-candidate-artifact": RunIdentityStatus.COMPLETE,
    "freshness-unknown-missing-current-input": RunIdentityStatus.COMPLETE,
    "future-clock-skew": RunIdentityStatus.COMPLETE,
    "invalid-artifact-identity": RunIdentityStatus.INVALID,
    "invalid-artifact-trial-identity": RunIdentityStatus.INVALID,
    "invalid-dot-segment-path": RunIdentityStatus.INVALID,
    "invalid-input-digest": RunIdentityStatus.INVALID,
    "invalid-output-digest": RunIdentityStatus.INVALID,
    "invalid-review-context-schema": RunIdentityStatus.COMPLETE,
    "invalid-run-identity": RunIdentityStatus.INVALID,
    "invalid-timestamp-order": RunIdentityStatus.INVALID,
    "invalid-unsafe-path": RunIdentityStatus.INVALID,
    "missing-manifest-with-results": RunIdentityStatus.MISSING,
    "minimal-declared-human": RunIdentityStatus.COMPLETE,
    "missing-local-file": RunIdentityStatus.INVALID,
    "missing-required-candidate-id": RunIdentityStatus.INVALID,
    "recency-unknown-missing-completed-at": RunIdentityStatus.COMPLETE,
    "review-context-invalid-current-digest": RunIdentityStatus.COMPLETE,
    "stale-candidate": RunIdentityStatus.COMPLETE,
    "stale-eval-cases": RunIdentityStatus.COMPLETE,
    "stale-policy-input": RunIdentityStatus.COMPLETE,
    "stale-routing-policy": RunIdentityStatus.COMPLETE,
    "unsupported-schema-version": RunIdentityStatus.INVALID,
    "uri-only-results": RunIdentityStatus.INVALID,
    "valid-artifact-identity-omitted": RunIdentityStatus.COMPLETE,
    "valid-current-deterministic": RunIdentityStatus.COMPLETE,
    "valid-current-human": RunIdentityStatus.COMPLETE,
    "valid-current-hybrid": RunIdentityStatus.COMPLETE,
    "valid-current-model-judge": RunIdentityStatus.COMPLETE,
    "verified-freshness-unknown": RunIdentityStatus.COMPLETE,
}

def fixture_dirs() -> list[Path]:
    return sorted(path for path in FIXTURE_ROOT.iterdir() if path.is_dir())


def test_runtime_projection_matrix_is_exhaustive() -> None:
    assert set(EXPECTED_STATUS) == {path.name for path in fixture_dirs()}


@pytest.mark.parametrize("fixture", fixture_dirs(), ids=lambda path: path.name)
def test_runtime_identity_fixture_projection(fixture: Path) -> None:
    inspection = inspect_run_identity(fixture)
    expected = yaml.safe_load((fixture / "expected.yaml").read_text(encoding="utf-8"))
    classification = inspection.classification

    assert inspection.status == EXPECTED_STATUS[fixture.name]
    assert {
        "validity": classification.validity.value,
        "freshness": classification.freshness.value,
        "recency": classification.recency.value,
        "assurance": classification.assurance.value,
    } == {
        key: expected["provenance"][key]
        for key in ("validity", "freshness", "recency", "assurance")
    }
    expected_findings = set(expected["findings"])
    finding_ids = {finding.id for finding in inspection.findings}
    if expected_findings & {
        "provenance_candidate_stale",
        "provenance_evidence_stale",
        "provenance_freshness_unknown",
        "provenance_recency_unknown",
        "provenance_evidence_expired",
        "provenance_review_context_schema_invalid",
        "provenance_review_context_digest_mismatch",
        "provenance_duplicate_current_resource",
        "provenance_future_timestamp_invalid",
    }:
        assert expected_findings <= finding_ids
