from pathlib import Path

import yaml

from openevalgate.provenance import RunIdentityStatus, inspect_run_identity


CSV_HEADER = (
    "run_id,case_id,candidate,evaluator,actual_route,expected_route,"
    "route_match,passed,score,failure_category,failure_reason,"
    "observed_output_path,reviewed_by,reviewed_at,notes\n"
)


def _write_results(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(CSV_HEADER, encoding="utf-8")


def _base_manifest(**overrides):
    manifest = {
        "schema_version": "1",
        "run": {"id": "run_001", "status": "complete"},
        "candidate": {"id": "candidate", "version": "1", "accepted_aliases": ["candidate-alias"]},
        "evaluation": {
            "kind": "human",
            "evaluator": {"id": "human-review", "accepted_aliases": ["reviewer"]},
        },
        "outputs": {"results": {"path": "eval_results.csv"}},
    }
    for key, value in overrides.items():
        manifest[key] = value
    return manifest


def _write_manifest(path: Path, manifest: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")


def _finding_ids(inspection):
    return [finding.id for finding in inspection.findings]


def test_no_manifest_with_results_is_legacy(tmp_path: Path) -> None:
    _write_results(tmp_path / "eval_results.csv")

    inspection = inspect_run_identity(tmp_path)

    assert inspection.status == RunIdentityStatus.LEGACY
    assert inspection.results_present is True
    assert inspection.identity is None


def test_no_manifest_without_results_is_legacy_not_provided(tmp_path: Path) -> None:
    inspection = inspect_run_identity(tmp_path)

    assert inspection.status == RunIdentityStatus.LEGACY
    assert inspection.results_present is False
    assert _finding_ids(inspection) == ["provenance_manifest_absent"]


def test_valid_root_manifest_is_complete(tmp_path: Path) -> None:
    _write_results(tmp_path / "eval_results.csv")
    _write_manifest(tmp_path / "run_manifest.yaml", _base_manifest())

    inspection = inspect_run_identity(tmp_path)

    assert inspection.status == RunIdentityStatus.COMPLETE
    assert inspection.identity is not None
    assert inspection.identity.run_id == "run_001"
    assert inspection.identity.candidate_id == "candidate"
    assert inspection.identity.evaluator.evaluator_id == "human-review"


def test_valid_selected_run_manifest_is_authoritative(tmp_path: Path) -> None:
    run_dir = tmp_path / "eval_runs" / "run_001"
    _write_results(run_dir / "eval_results.csv")
    _write_manifest(run_dir / "run_manifest.yaml", _base_manifest())

    inspection = inspect_run_identity(tmp_path, selected_run_id="run_001")

    assert inspection.status == RunIdentityStatus.COMPLETE
    assert inspection.manifest_path == run_dir / "run_manifest.yaml"
    assert inspection.identity is not None
    assert inspection.identity.results_path == (run_dir / "eval_results.csv").resolve(strict=False)


def test_root_manifest_fallback_must_declare_selected_run(tmp_path: Path) -> None:
    _write_results(tmp_path / "eval_results.csv")
    _write_manifest(tmp_path / "run_manifest.yaml", _base_manifest(run={"id": "other_run", "status": "complete"}))

    inspection = inspect_run_identity(tmp_path, selected_run_id="run_001")

    assert inspection.status == RunIdentityStatus.LEGACY
    assert inspection.identity is None


def test_malformed_yaml_is_invalid(tmp_path: Path) -> None:
    (tmp_path / "run_manifest.yaml").write_text("schema_version: ['1'\n", encoding="utf-8")

    inspection = inspect_run_identity(tmp_path)

    assert inspection.status == RunIdentityStatus.INVALID
    assert _finding_ids(inspection) == ["provenance_manifest_schema_invalid"]
    assert "Could not parse" in inspection.findings[0].message


def test_unsupported_version_takes_precedence(tmp_path: Path) -> None:
    _write_manifest(tmp_path / "run_manifest.yaml", {**_base_manifest(), "schema_version": "2"})

    inspection = inspect_run_identity(tmp_path)

    assert inspection.status == RunIdentityStatus.INVALID
    assert _finding_ids(inspection) == ["provenance_unsupported_schema_version"]


def test_schema_invalid_manifest_is_invalid(tmp_path: Path) -> None:
    manifest = _base_manifest()
    del manifest["candidate"]["id"]
    _write_manifest(tmp_path / "run_manifest.yaml", manifest)

    inspection = inspect_run_identity(tmp_path)

    assert inspection.status == RunIdentityStatus.INVALID
    assert _finding_ids(inspection) == ["provenance_manifest_schema_invalid"]


def test_uri_only_results_uses_specific_finding(tmp_path: Path) -> None:
    manifest = _base_manifest(outputs={"results": {"uri": "https://example.com/results.csv"}})
    _write_manifest(tmp_path / "run_manifest.yaml", manifest)

    inspection = inspect_run_identity(tmp_path)

    assert inspection.status == RunIdentityStatus.INVALID
    assert _finding_ids(inspection) == ["provenance_results_path_required"]


def test_valid_deterministic_evaluator(tmp_path: Path) -> None:
    _write_results(tmp_path / "eval_results.csv")
    manifest = _base_manifest(
        evaluation={
            "kind": "deterministic",
            "evaluator": {"id": "det-checker", "version": "1"},
        }
    )
    _write_manifest(tmp_path / "run_manifest.yaml", manifest)

    inspection = inspect_run_identity(tmp_path)

    assert inspection.status == RunIdentityStatus.COMPLETE
    assert inspection.identity is not None
    assert inspection.identity.evaluator.evaluator_version == "1"


def test_deterministic_evaluator_without_version_is_invalid(tmp_path: Path) -> None:
    manifest = _base_manifest(evaluation={"kind": "deterministic", "evaluator": {"id": "det-checker"}})
    _write_manifest(tmp_path / "run_manifest.yaml", manifest)

    inspection = inspect_run_identity(tmp_path)

    assert inspection.status == RunIdentityStatus.INVALID
    assert _finding_ids(inspection) == ["provenance_manifest_schema_invalid"]


def test_valid_model_judge_evaluator(tmp_path: Path) -> None:
    _write_results(tmp_path / "eval_results.csv")
    manifest = _base_manifest(
        evaluation={
            "kind": "model_judge",
            "evaluator": {"id": "judge", "version": "2026-06"},
        }
    )
    _write_manifest(tmp_path / "run_manifest.yaml", manifest)

    inspection = inspect_run_identity(tmp_path)

    assert inspection.status == RunIdentityStatus.COMPLETE
    assert inspection.identity is not None
    assert inspection.identity.evaluator.kind == "model_judge"


def test_model_judge_without_version_is_invalid(tmp_path: Path) -> None:
    manifest = _base_manifest(evaluation={"kind": "model_judge", "evaluator": {"id": "judge"}})
    _write_manifest(tmp_path / "run_manifest.yaml", manifest)

    inspection = inspect_run_identity(tmp_path)

    assert inspection.status == RunIdentityStatus.INVALID
    assert _finding_ids(inspection) == ["provenance_manifest_schema_invalid"]


def test_valid_hybrid_evaluator(tmp_path: Path) -> None:
    _write_results(tmp_path / "eval_results.csv")
    (tmp_path / "policy.yaml").write_text("policy: hybrid\n", encoding="utf-8")
    manifest = _base_manifest(
        evaluation={
            "kind": "hybrid",
            "evaluator": {
                "id": "hybrid",
                "components": [
                    {"id": "human", "kind": "human"},
                    {"id": "det", "kind": "deterministic", "version": "1"},
                ],
                "decision_policy": {"path": "policy.yaml"},
            },
        }
    )
    _write_manifest(tmp_path / "run_manifest.yaml", manifest)

    inspection = inspect_run_identity(tmp_path)

    assert inspection.status == RunIdentityStatus.COMPLETE
    assert inspection.identity is not None
    assert inspection.identity.evaluator.component_ids == ("human", "det")


def test_duplicate_hybrid_component_ids_are_invalid(tmp_path: Path) -> None:
    _write_results(tmp_path / "eval_results.csv")
    (tmp_path / "policy.yaml").write_text("policy: hybrid\n", encoding="utf-8")
    manifest = _base_manifest(
        evaluation={
            "kind": "hybrid",
            "evaluator": {
                "id": "hybrid",
                "components": [
                    {"id": "dup", "kind": "human"},
                    {"id": "dup", "kind": "deterministic", "version": "1"},
                ],
                "decision_policy": {"path": "policy.yaml"},
            },
        }
    )
    _write_manifest(tmp_path / "run_manifest.yaml", manifest)

    inspection = inspect_run_identity(tmp_path)

    assert inspection.status == RunIdentityStatus.INVALID
    assert _finding_ids(inspection) == ["provenance_duplicate_hybrid_component_id"]


def test_hybrid_without_decision_policy_is_invalid(tmp_path: Path) -> None:
    manifest = _base_manifest(
        evaluation={
            "kind": "hybrid",
            "evaluator": {
                "id": "hybrid",
                "components": [{"id": "human", "kind": "human"}],
            },
        }
    )
    _write_manifest(tmp_path / "run_manifest.yaml", manifest)

    inspection = inspect_run_identity(tmp_path)

    assert inspection.status == RunIdentityStatus.INVALID
    assert _finding_ids(inspection) == ["provenance_manifest_schema_invalid"]


def test_conflicting_root_and_run_scoped_manifests_are_invalid(tmp_path: Path) -> None:
    run_dir = tmp_path / "eval_runs" / "run_001"
    _write_results(run_dir / "eval_results.csv")
    _write_results(tmp_path / "eval_results.csv")
    _write_manifest(run_dir / "run_manifest.yaml", _base_manifest())
    _write_manifest(
        tmp_path / "run_manifest.yaml",
        _base_manifest(candidate={"id": "other", "version": "1"}),
    )

    inspection = inspect_run_identity(tmp_path, selected_run_id="run_001")

    assert inspection.status == RunIdentityStatus.INVALID
    assert _finding_ids(inspection) == ["provenance_run_id_mismatch"]


def test_lifecycle_failed_remains_identity_complete(tmp_path: Path) -> None:
    _write_results(tmp_path / "eval_results.csv")
    _write_manifest(tmp_path / "run_manifest.yaml", _base_manifest(run={"id": "run_001", "status": "failed"}))

    inspection = inspect_run_identity(tmp_path)

    assert inspection.status == RunIdentityStatus.COMPLETE
    assert inspection.identity is not None
    assert inspection.identity.run_status == "failed"
    assert _finding_ids(inspection) == ["provenance_lifecycle_failed"]


def test_lifecycle_aborted_remains_identity_complete(tmp_path: Path) -> None:
    _write_results(tmp_path / "eval_results.csv")
    _write_manifest(tmp_path / "run_manifest.yaml", _base_manifest(run={"id": "run_001", "status": "aborted"}))

    inspection = inspect_run_identity(tmp_path)

    assert inspection.status == RunIdentityStatus.COMPLETE
    assert _finding_ids(inspection) == ["provenance_lifecycle_incomplete"]
