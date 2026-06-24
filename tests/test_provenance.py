from pathlib import Path

import yaml

from openevalgate.eval_results import classify_behavioral_evidence
from openevalgate.provenance import RunIdentityStatus, inspect_run_identity


CSV_HEADER = (
    "run_id,case_id,candidate,evaluator,actual_route,expected_route,"
    "route_match,passed,score,failure_category,failure_reason,"
    "observed_output_path,reviewed_by,reviewed_at,notes,trial_id\n"
)


def _write_results(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(CSV_HEADER, encoding="utf-8")


def _write_result_rows(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = []
    for row in rows:
        body.append(
            ",".join(
                [
                    row.get("run_id", "run_001"),
                    row.get("case_id", "case_001"),
                    row.get("candidate", "candidate"),
                    row.get("evaluator", "human-review"),
                    "show",
                    "show",
                    "true",
                    "true",
                    "1",
                    "",
                    "",
                    row.get("observed_output_path", ""),
                    "qa",
                    "2026-06-18",
                    "",
                    row.get("trial_id", ""),
                ]
            )
        )
    path.write_text(CSV_HEADER + "\n".join(body) + "\n", encoding="utf-8")


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
    assert inspection.results_path == tmp_path / "eval_results.csv"
    assert inspection.results_present is True
    assert inspection.identity is None


def test_no_manifest_without_results_is_legacy_not_provided(tmp_path: Path) -> None:
    inspection = inspect_run_identity(tmp_path)

    assert inspection.status == RunIdentityStatus.LEGACY
    assert inspection.results_path is None
    assert inspection.results_present is False
    assert _finding_ids(inspection) == ["provenance_manifest_absent"]


def test_valid_root_manifest_is_complete(tmp_path: Path) -> None:
    _write_results(tmp_path / "eval_results.csv")
    _write_manifest(tmp_path / "run_manifest.yaml", _base_manifest())

    inspection = inspect_run_identity(tmp_path)

    assert inspection.status == RunIdentityStatus.COMPLETE
    assert inspection.results_path == (tmp_path / "eval_results.csv").resolve(strict=False)
    assert inspection.results_present is True
    assert inspection.identity is not None
    assert inspection.identity.run_id == "run_001"
    assert inspection.identity.candidate_id == "candidate"
    assert inspection.identity.evaluator.evaluator_id == "human-review"


def test_results_present_is_inspection_snapshot(tmp_path: Path) -> None:
    _write_results(tmp_path / "eval_results.csv")
    _write_manifest(tmp_path / "run_manifest.yaml", _base_manifest())
    inspection = inspect_run_identity(tmp_path)

    assert inspection.results_path == (tmp_path / "eval_results.csv").resolve(strict=False)
    assert inspection.results_present is True

    inspection.results_path.unlink()

    assert inspection.results_present is True


def test_valid_selected_run_manifest_is_authoritative(tmp_path: Path) -> None:
    run_dir = tmp_path / "eval_runs" / "run_001"
    _write_results(run_dir / "eval_results.csv")
    _write_manifest(run_dir / "run_manifest.yaml", _base_manifest())

    inspection = inspect_run_identity(tmp_path, selected_run_id="run_001")

    assert inspection.status == RunIdentityStatus.COMPLETE
    assert inspection.manifest_path == run_dir / "run_manifest.yaml"
    assert inspection.results_path == (run_dir / "eval_results.csv").resolve(strict=False)
    assert inspection.results_present is True
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
    assert inspection.results_path is None
    assert inspection.results_present is False
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


def test_csv_rows_match_manifest_identity_exactly(tmp_path: Path) -> None:
    _write_result_rows(tmp_path / "eval_results.csv", [{"case_id": "case_001"}])
    _write_manifest(tmp_path / "run_manifest.yaml", _base_manifest())

    inspection = inspect_run_identity(tmp_path)

    assert inspection.status == RunIdentityStatus.COMPLETE
    assert inspection.identity is not None
    assert inspection.identity.candidate_id == "candidate"


def test_csv_rows_accept_candidate_and_evaluator_aliases(tmp_path: Path) -> None:
    _write_result_rows(
        tmp_path / "eval_results.csv",
        [{"candidate": "candidate-alias", "evaluator": "reviewer"}],
    )
    _write_manifest(tmp_path / "run_manifest.yaml", _base_manifest())

    inspection = inspect_run_identity(tmp_path)

    assert inspection.status == RunIdentityStatus.COMPLETE
    assert inspection.identity is not None
    assert inspection.identity.candidate_id == "candidate"
    assert inspection.identity.evaluator.evaluator_id == "human-review"


def test_csv_row_identity_is_trimmed(tmp_path: Path) -> None:
    _write_result_rows(
        tmp_path / "eval_results.csv",
        [{"run_id": " run_001 ", "candidate": " candidate ", "evaluator": " human-review "}],
    )
    _write_manifest(tmp_path / "run_manifest.yaml", _base_manifest())

    inspection = inspect_run_identity(tmp_path)

    assert inspection.status == RunIdentityStatus.COMPLETE


def test_csv_row_identity_is_case_sensitive(tmp_path: Path) -> None:
    _write_result_rows(tmp_path / "eval_results.csv", [{"candidate": "Candidate"}])
    _write_manifest(tmp_path / "run_manifest.yaml", _base_manifest())

    inspection = inspect_run_identity(tmp_path)

    assert inspection.status == RunIdentityStatus.INVALID
    assert _finding_ids(inspection) == ["provenance_candidate_alias_mismatch"]


def test_manifest_backed_csv_rejects_mixed_runs(tmp_path: Path) -> None:
    _write_result_rows(tmp_path / "eval_results.csv", [{"run_id": "run_001"}, {"run_id": "run_002"}])
    _write_manifest(tmp_path / "run_manifest.yaml", _base_manifest())

    inspection = inspect_run_identity(tmp_path)

    assert inspection.status == RunIdentityStatus.INVALID
    assert inspection.results_path == (tmp_path / "eval_results.csv").resolve(strict=False)
    assert inspection.results_present is True
    assert _finding_ids(inspection) == ["provenance_run_id_mismatch"]
    evidence = classify_behavioral_evidence(tmp_path, identity_inspection=inspection)
    assert evidence.state == "invalid"
    assert evidence.summary is None


def test_manifest_backed_csv_rejects_mixed_candidates(tmp_path: Path) -> None:
    _write_result_rows(tmp_path / "eval_results.csv", [{"candidate": "candidate"}, {"candidate": "other"}])
    _write_manifest(tmp_path / "run_manifest.yaml", _base_manifest())

    inspection = inspect_run_identity(tmp_path)

    assert inspection.status == RunIdentityStatus.INVALID
    assert _finding_ids(inspection) == ["provenance_candidate_alias_mismatch"]


def test_manifest_backed_csv_rejects_mixed_evaluators(tmp_path: Path) -> None:
    _write_result_rows(tmp_path / "eval_results.csv", [{"evaluator": "human-review"}, {"evaluator": "other"}])
    _write_manifest(tmp_path / "run_manifest.yaml", _base_manifest())

    inspection = inspect_run_identity(tmp_path)

    assert inspection.status == RunIdentityStatus.INVALID
    assert _finding_ids(inspection) == ["provenance_evaluator_alias_mismatch"]


def test_selected_run_mismatch_is_invalid(tmp_path: Path) -> None:
    run_dir = tmp_path / "eval_runs" / "other_run"
    _write_result_rows(run_dir / "eval_results.csv", [{"run_id": "run_001"}])
    _write_manifest(run_dir / "run_manifest.yaml", _base_manifest())

    inspection = inspect_run_identity(tmp_path, selected_run_id="other_run")

    assert inspection.status == RunIdentityStatus.INVALID
    assert _finding_ids(inspection) == ["provenance_run_id_mismatch"]


def test_selected_candidate_mismatch_is_invalid(tmp_path: Path) -> None:
    _write_result_rows(tmp_path / "eval_results.csv", [{"candidate": "candidate"}])
    _write_manifest(tmp_path / "run_manifest.yaml", _base_manifest())

    inspection = inspect_run_identity(tmp_path, selected_run_id="run_001", selected_candidate="other")

    assert inspection.status == RunIdentityStatus.INVALID
    assert _finding_ids(inspection) == ["provenance_candidate_alias_mismatch"]


def _write_output(path: Path, text: str = "output\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _manifest_with_artifact_index() -> dict:
    return _base_manifest(
        outputs={
            "results": {"path": "eval_results.csv"},
            "artifact_index": {"path": "artifact_index.yaml"},
        }
    )


def _write_artifact_index(path: Path, artifacts: list[dict], *, run_id: str = "run_001") -> None:
    path.write_text(
        yaml.safe_dump(
            {"schema_version": "1", "run_id": run_id, "artifacts": artifacts},
            sort_keys=False,
        ),
        encoding="utf-8",
    )


def test_matching_conventional_output_directory_is_complete(tmp_path: Path) -> None:
    output = tmp_path / "eval_runs" / "run_001" / "case_001.md"
    _write_output(output)
    _write_result_rows(tmp_path / "eval_results.csv", [{"observed_output_path": "eval_runs/run_001/case_001.md"}])
    _write_manifest(tmp_path / "run_manifest.yaml", _base_manifest())

    inspection = inspect_run_identity(tmp_path)

    assert inspection.status == RunIdentityStatus.COMPLETE


def test_mismatching_conventional_output_directory_is_invalid(tmp_path: Path) -> None:
    output = tmp_path / "eval_runs" / "run_002" / "case_001.md"
    _write_output(output)
    _write_result_rows(tmp_path / "eval_results.csv", [{"observed_output_path": "eval_runs/run_002/case_001.md"}])
    _write_manifest(tmp_path / "run_manifest.yaml", _base_manifest())

    inspection = inspect_run_identity(tmp_path)

    assert inspection.status == RunIdentityStatus.INVALID
    assert _finding_ids(inspection) == ["provenance_run_id_mismatch"]


def test_safe_nonconventional_output_path_is_allowed(tmp_path: Path) -> None:
    _write_output(tmp_path / "outputs" / "case_001.md")
    _write_result_rows(tmp_path / "eval_results.csv", [{"observed_output_path": "outputs/case_001.md"}])
    _write_manifest(tmp_path / "run_manifest.yaml", _base_manifest())

    inspection = inspect_run_identity(tmp_path)

    assert inspection.status == RunIdentityStatus.COMPLETE


def test_matching_markdown_metadata_styles_are_complete(tmp_path: Path) -> None:
    _write_output(
        tmp_path / "outputs" / "case_001.md",
        "**Run ID:** run_001  \n**Case ID:** case_001  \n- **Candidate:** candidate\n- **Evaluator:** human-review\n",
    )
    _write_result_rows(tmp_path / "eval_results.csv", [{"observed_output_path": "outputs/case_001.md"}])
    _write_manifest(tmp_path / "run_manifest.yaml", _base_manifest())

    inspection = inspect_run_identity(tmp_path)

    assert inspection.status == RunIdentityStatus.COMPLETE


def test_missing_markdown_metadata_is_allowed(tmp_path: Path) -> None:
    _write_output(tmp_path / "outputs" / "case_001.md", "plain output\n")
    _write_result_rows(tmp_path / "eval_results.csv", [{"observed_output_path": "outputs/case_001.md"}])
    _write_manifest(tmp_path / "run_manifest.yaml", _base_manifest())

    assert inspect_run_identity(tmp_path).status == RunIdentityStatus.COMPLETE


def test_mismatching_markdown_run_metadata_is_invalid(tmp_path: Path) -> None:
    _write_output(tmp_path / "outputs" / "case_001.md", "Run ID: run_002\n")
    _write_result_rows(tmp_path / "eval_results.csv", [{"observed_output_path": "outputs/case_001.md"}])
    _write_manifest(tmp_path / "run_manifest.yaml", _base_manifest())

    inspection = inspect_run_identity(tmp_path)

    assert inspection.status == RunIdentityStatus.INVALID
    assert _finding_ids(inspection) == ["provenance_run_id_mismatch"]


def test_mismatching_markdown_case_metadata_is_invalid(tmp_path: Path) -> None:
    _write_output(tmp_path / "outputs" / "case_001.md", "Case ID: other_case\n")
    _write_result_rows(tmp_path / "eval_results.csv", [{"observed_output_path": "outputs/case_001.md"}])
    _write_manifest(tmp_path / "run_manifest.yaml", _base_manifest())

    inspection = inspect_run_identity(tmp_path)

    assert inspection.status == RunIdentityStatus.INVALID
    assert _finding_ids(inspection) == ["provenance_artifact_identity_mismatch"]


def test_mismatching_markdown_candidate_metadata_is_invalid(tmp_path: Path) -> None:
    _write_output(tmp_path / "outputs" / "case_001.md", "Candidate: other\n")
    _write_result_rows(tmp_path / "eval_results.csv", [{"observed_output_path": "outputs/case_001.md"}])
    _write_manifest(tmp_path / "run_manifest.yaml", _base_manifest())

    inspection = inspect_run_identity(tmp_path)

    assert inspection.status == RunIdentityStatus.INVALID
    assert _finding_ids(inspection) == ["provenance_candidate_alias_mismatch"]


def test_mismatching_markdown_evaluator_metadata_is_invalid(tmp_path: Path) -> None:
    _write_output(tmp_path / "outputs" / "case_001.md", "Evaluator: other\n")
    _write_result_rows(tmp_path / "eval_results.csv", [{"observed_output_path": "outputs/case_001.md"}])
    _write_manifest(tmp_path / "run_manifest.yaml", _base_manifest())

    inspection = inspect_run_identity(tmp_path)

    assert inspection.status == RunIdentityStatus.INVALID
    assert _finding_ids(inspection) == ["provenance_evaluator_alias_mismatch"]


def test_conflicting_duplicate_markdown_metadata_is_invalid(tmp_path: Path) -> None:
    _write_output(tmp_path / "outputs" / "case_001.md", "Case ID: case_001\nCase ID: other\n")
    _write_result_rows(tmp_path / "eval_results.csv", [{"observed_output_path": "outputs/case_001.md"}])
    _write_manifest(tmp_path / "run_manifest.yaml", _base_manifest())

    inspection = inspect_run_identity(tmp_path)

    assert inspection.status == RunIdentityStatus.INVALID
    assert _finding_ids(inspection) == ["provenance_artifact_identity_mismatch"]


def test_undecodable_optional_markdown_metadata_is_unavailable(tmp_path: Path) -> None:
    output = tmp_path / "outputs" / "case_001.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(b"\xff\xfe\xfd")
    _write_result_rows(tmp_path / "eval_results.csv", [{"observed_output_path": "outputs/case_001.md"}])
    _write_manifest(tmp_path / "run_manifest.yaml", _base_manifest())

    assert inspect_run_identity(tmp_path).status == RunIdentityStatus.COMPLETE


def test_legacy_output_identity_contradiction_is_invalid(tmp_path: Path) -> None:
    _write_output(tmp_path / "eval_runs" / "run_002" / "case_001.md")
    _write_result_rows(tmp_path / "eval_results.csv", [{"observed_output_path": "eval_runs/run_002/case_001.md"}])

    inspection = inspect_run_identity(tmp_path)

    assert inspection.status == RunIdentityStatus.INVALID
    assert inspection.results_path == tmp_path / "eval_results.csv"
    assert inspection.results_present is True
    assert _finding_ids(inspection) == ["provenance_run_id_mismatch"]
    evidence = classify_behavioral_evidence(tmp_path, identity_inspection=inspection)
    assert evidence.state == "invalid"
    assert evidence.summary is None


def test_no_artifact_index_remains_complete(tmp_path: Path) -> None:
    _write_result_rows(tmp_path / "eval_results.csv", [{"case_id": "case_001"}])
    _write_manifest(tmp_path / "run_manifest.yaml", _base_manifest())

    assert inspect_run_identity(tmp_path).status == RunIdentityStatus.COMPLETE


def test_valid_artifact_index_is_complete(tmp_path: Path) -> None:
    _write_output(tmp_path / "artifacts" / "case_001.md")
    _write_result_rows(
        tmp_path / "eval_results.csv",
        [{"case_id": "case_001", "trial_id": "trial_001", "observed_output_path": "artifacts/case_001.md"}],
    )
    _write_artifact_index(
        tmp_path / "artifact_index.yaml",
        [
            {
                "artifact_id": "artifact-001",
                "artifact_type": "markdown",
                "path": "artifacts/case_001.md",
                "case_id": "case_001",
                "trial_id": "trial_001",
                "evaluator_ref": "human-review",
            }
        ],
    )
    _write_manifest(tmp_path / "run_manifest.yaml", _manifest_with_artifact_index())

    inspection = inspect_run_identity(tmp_path)

    assert inspection.status == RunIdentityStatus.COMPLETE


def test_schema_invalid_artifact_index_is_invalid(tmp_path: Path) -> None:
    _write_result_rows(tmp_path / "eval_results.csv", [{"observed_output_path": ""}])
    (tmp_path / "artifact_index.yaml").write_text(
        yaml.safe_dump({"schema_version": "1", "run_id": "run_001", "artifacts": []}),
        encoding="utf-8",
    )
    _write_manifest(tmp_path / "run_manifest.yaml", _manifest_with_artifact_index())

    inspection = inspect_run_identity(tmp_path)

    assert inspection.status == RunIdentityStatus.INVALID
    assert _finding_ids(inspection) == ["provenance_artifact_index_schema_invalid"]


def test_artifact_index_run_mismatch_is_invalid(tmp_path: Path) -> None:
    _write_output(tmp_path / "artifacts" / "case_001.md")
    _write_result_rows(tmp_path / "eval_results.csv", [{"observed_output_path": "artifacts/case_001.md"}])
    _write_artifact_index(
        tmp_path / "artifact_index.yaml",
        [{"artifact_id": "artifact-001", "artifact_type": "markdown", "path": "artifacts/case_001.md"}],
        run_id="run_002",
    )
    _write_manifest(tmp_path / "run_manifest.yaml", _manifest_with_artifact_index())

    inspection = inspect_run_identity(tmp_path)

    assert inspection.status == RunIdentityStatus.INVALID
    assert "provenance_artifact_identity_mismatch" in _finding_ids(inspection)


def test_duplicate_artifact_id_is_invalid(tmp_path: Path) -> None:
    _write_output(tmp_path / "artifacts" / "case_001.md")
    _write_output(tmp_path / "artifacts" / "case_002.md")
    _write_result_rows(tmp_path / "eval_results.csv", [{"observed_output_path": "artifacts/case_001.md"}])
    _write_artifact_index(
        tmp_path / "artifact_index.yaml",
        [
            {"artifact_id": "dup", "artifact_type": "markdown", "path": "artifacts/case_001.md"},
            {"artifact_id": "dup", "artifact_type": "markdown", "path": "artifacts/case_002.md"},
        ],
    )
    _write_manifest(tmp_path / "run_manifest.yaml", _manifest_with_artifact_index())

    assert "provenance_duplicate_artifact_id" in _finding_ids(inspect_run_identity(tmp_path))


def test_duplicate_normalized_artifact_path_is_invalid(tmp_path: Path) -> None:
    _write_output(tmp_path / "artifacts" / "case_001.md")
    _write_result_rows(tmp_path / "eval_results.csv", [{"observed_output_path": "artifacts/case_001.md"}])
    _write_artifact_index(
        tmp_path / "artifact_index.yaml",
        [
            {"artifact_id": "a", "artifact_type": "markdown", "path": "artifacts/case_001.md"},
            {"artifact_id": "b", "artifact_type": "markdown", "path": "artifacts/case_001.md"},
        ],
    )
    _write_manifest(tmp_path / "run_manifest.yaml", _manifest_with_artifact_index())

    assert "provenance_duplicate_artifact_path" in _finding_ids(inspect_run_identity(tmp_path))


def test_artifact_index_allows_omitted_case_and_trial_identity(tmp_path: Path) -> None:
    _write_output(tmp_path / "artifacts" / "case_001.md")
    _write_result_rows(tmp_path / "eval_results.csv", [{"case_id": "case_001", "trial_id": "", "observed_output_path": "artifacts/case_001.md"}])
    _write_artifact_index(
        tmp_path / "artifact_index.yaml",
        [{"artifact_id": "artifact-001", "artifact_type": "markdown", "path": "artifacts/case_001.md"}],
    )
    _write_manifest(tmp_path / "run_manifest.yaml", _manifest_with_artifact_index())

    assert inspect_run_identity(tmp_path).status == RunIdentityStatus.COMPLETE


def test_artifact_index_case_mismatch_is_invalid(tmp_path: Path) -> None:
    _write_output(tmp_path / "artifacts" / "case_001.md")
    _write_result_rows(tmp_path / "eval_results.csv", [{"case_id": "case_001", "observed_output_path": "artifacts/case_001.md"}])
    _write_artifact_index(
        tmp_path / "artifact_index.yaml",
        [{"artifact_id": "artifact-001", "artifact_type": "markdown", "path": "artifacts/case_001.md", "case_id": "other"}],
    )
    _write_manifest(tmp_path / "run_manifest.yaml", _manifest_with_artifact_index())

    assert "provenance_artifact_identity_mismatch" in _finding_ids(inspect_run_identity(tmp_path))


def test_artifact_index_trial_mismatch_is_invalid(tmp_path: Path) -> None:
    _write_output(tmp_path / "artifacts" / "case_001.md")
    _write_result_rows(tmp_path / "eval_results.csv", [{"case_id": "case_001", "trial_id": "trial_001", "observed_output_path": "artifacts/case_001.md"}])
    _write_artifact_index(
        tmp_path / "artifact_index.yaml",
        [{"artifact_id": "artifact-001", "artifact_type": "markdown", "path": "artifacts/case_001.md", "case_id": "case_001", "trial_id": "trial_002"}],
    )
    _write_manifest(tmp_path / "run_manifest.yaml", _manifest_with_artifact_index())

    assert "provenance_artifact_identity_mismatch" in _finding_ids(inspect_run_identity(tmp_path))


def test_valid_hybrid_component_evaluator_ref_is_complete(tmp_path: Path) -> None:
    _write_output(tmp_path / "artifacts" / "case_001.md")
    _write_output(tmp_path / "policy.yaml")
    _write_result_rows(
        tmp_path / "eval_results.csv",
        [{"observed_output_path": "artifacts/case_001.md", "evaluator": "hybrid"}],
    )
    _write_artifact_index(
        tmp_path / "artifact_index.yaml",
        [{"artifact_id": "artifact-001", "artifact_type": "markdown", "path": "artifacts/case_001.md", "evaluator_ref": "det"}],
    )
    manifest = _manifest_with_artifact_index()
    manifest["evaluation"] = {
        "kind": "hybrid",
        "evaluator": {
            "id": "hybrid",
            "components": [{"id": "det", "kind": "deterministic", "version": "1"}],
            "decision_policy": {"path": "policy.yaml"},
        },
    }
    _write_manifest(tmp_path / "run_manifest.yaml", manifest)

    assert inspect_run_identity(tmp_path).status == RunIdentityStatus.COMPLETE


def test_invalid_artifact_evaluator_ref_is_invalid(tmp_path: Path) -> None:
    _write_output(tmp_path / "artifacts" / "case_001.md")
    _write_result_rows(tmp_path / "eval_results.csv", [{"observed_output_path": "artifacts/case_001.md"}])
    _write_artifact_index(
        tmp_path / "artifact_index.yaml",
        [{"artifact_id": "artifact-001", "artifact_type": "markdown", "path": "artifacts/case_001.md", "evaluator_ref": "other"}],
    )
    _write_manifest(tmp_path / "run_manifest.yaml", _manifest_with_artifact_index())

    assert "provenance_artifact_identity_mismatch" in _finding_ids(inspect_run_identity(tmp_path))


def test_artifact_mapping_must_be_unambiguous(tmp_path: Path) -> None:
    _write_output(tmp_path / "artifacts" / "case_001.md")
    _write_output(tmp_path / "artifacts" / "other.md")
    _write_result_rows(tmp_path / "eval_results.csv", [{"observed_output_path": "artifacts/case_001.md"}])
    _write_artifact_index(
        tmp_path / "artifact_index.yaml",
        [{"artifact_id": "artifact-001", "artifact_type": "markdown", "path": "artifacts/other.md"}],
    )
    _write_manifest(tmp_path / "run_manifest.yaml", _manifest_with_artifact_index())

    assert "provenance_artifact_identity_mismatch" in _finding_ids(inspect_run_identity(tmp_path))


def test_unsafe_artifact_path_is_invalid(tmp_path: Path) -> None:
    _write_output(tmp_path / "artifacts" / "target.md")
    link = tmp_path / "artifacts" / "link.md"
    try:
        link.symlink_to(tmp_path / "artifacts" / "target.md")
    except (NotImplementedError, OSError):
        return
    _write_result_rows(tmp_path / "eval_results.csv", [{"observed_output_path": "artifacts/target.md"}])
    _write_artifact_index(
        tmp_path / "artifact_index.yaml",
        [{"artifact_id": "artifact-001", "artifact_type": "markdown", "path": "artifacts/link.md"}],
    )
    _write_manifest(tmp_path / "run_manifest.yaml", _manifest_with_artifact_index())

    assert "provenance_local_file_missing" in _finding_ids(inspect_run_identity(tmp_path))


def test_missing_artifact_file_is_invalid(tmp_path: Path) -> None:
    _write_result_rows(tmp_path / "eval_results.csv", [{"observed_output_path": ""}])
    _write_artifact_index(
        tmp_path / "artifact_index.yaml",
        [{"artifact_id": "artifact-001", "artifact_type": "markdown", "path": "artifacts/missing.md"}],
    )
    _write_manifest(tmp_path / "run_manifest.yaml", _manifest_with_artifact_index())

    assert "provenance_local_file_missing" in _finding_ids(inspect_run_identity(tmp_path))


def test_digest_mismatch_is_deferred_for_identity(tmp_path: Path) -> None:
    _write_output(tmp_path / "artifacts" / "case_001.md")
    _write_result_rows(tmp_path / "eval_results.csv", [{"observed_output_path": "artifacts/case_001.md"}])
    _write_artifact_index(
        tmp_path / "artifact_index.yaml",
        [
            {
                "artifact_id": "artifact-001",
                "artifact_type": "markdown",
                "path": "artifacts/case_001.md",
                "digest": {"sha256": "0" * 64},
            }
        ],
    )
    _write_manifest(tmp_path / "run_manifest.yaml", _manifest_with_artifact_index())

    inspection = inspect_run_identity(tmp_path)

    assert inspection.status == RunIdentityStatus.COMPLETE
    assert not any("digest" in finding.id for finding in inspection.findings)
