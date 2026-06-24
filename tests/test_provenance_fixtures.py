from pathlib import Path

import pytest

from openevalgate.provenance import RunIdentityStatus, inspect_run_identity


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / "spec" / "fixtures" / "provenance" / "v1"

EXPECTED_STATUS = {
    "aborted-run": RunIdentityStatus.COMPLETE,
    "candidate-alias-mismatch": RunIdentityStatus.INVALID,
    "contradictory-duplicate-resource": RunIdentityStatus.COMPLETE,
    "duplicate-artifact-id": RunIdentityStatus.INVALID,
    "duplicate-current-resource": RunIdentityStatus.COMPLETE,
    "duplicate-historical-resource": RunIdentityStatus.COMPLETE,
    "duplicate-hybrid-component-id": RunIdentityStatus.INVALID,
    "duplicate-normalized-artifact-path": RunIdentityStatus.INVALID,
    "duplicate-singleton-role": RunIdentityStatus.COMPLETE,
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
    "invalid-input-digest": RunIdentityStatus.COMPLETE,
    "invalid-output-digest": RunIdentityStatus.COMPLETE,
    "invalid-review-context-schema": RunIdentityStatus.COMPLETE,
    "invalid-run-identity": RunIdentityStatus.INVALID,
    "invalid-timestamp-order": RunIdentityStatus.COMPLETE,
    "invalid-unsafe-path": RunIdentityStatus.INVALID,
    "legacy-no-manifest": RunIdentityStatus.MISSING,
    "minimal-declared-human": RunIdentityStatus.COMPLETE,
    "missing-local-file": RunIdentityStatus.COMPLETE,
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

DEFERRED_FINDING_FRAGMENTS = (
    "digest",
    "stale",
    "freshness",
    "recency",
    "expired",
)


def fixture_dirs() -> list[Path]:
    return sorted(path for path in FIXTURE_ROOT.iterdir() if path.is_dir())


def test_runtime_projection_matrix_is_exhaustive() -> None:
    assert set(EXPECTED_STATUS) == {path.name for path in fixture_dirs()}


@pytest.mark.parametrize("fixture", fixture_dirs(), ids=lambda path: path.name)
def test_runtime_identity_fixture_projection(fixture: Path) -> None:
    inspection = inspect_run_identity(fixture)

    assert inspection.status == EXPECTED_STATUS[fixture.name]
    finding_ids = [finding.id for finding in inspection.findings]
    for fragment in DEFERRED_FINDING_FRAGMENTS:
        assert not any(fragment in finding_id for finding_id in finding_ids), fixture.name
