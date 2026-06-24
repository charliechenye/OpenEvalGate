import csv
import random
from pathlib import Path
from shutil import copytree

import pytest
import yaml

import openevalgate.eval_results as eval_results
from openevalgate.eval_results import (
    NONEMPTY_EVAL_RESULT_FIELDS,
    classify_behavioral_evidence,
    summarize_eval_results,
    summarize_selected_eval_results,
    validate_eval_results,
)
from openevalgate.report import generate_report
from openevalgate.validator import check_project


ROOT = Path(__file__).resolve().parents[1]
CUSTOMER_SUPPORT = ROOT / "examples" / "customer_support_assistant"


def _project(tmp_path: Path) -> Path:
    project = tmp_path / "project"
    copytree(CUSTOMER_SUPPORT, project)
    return project


def _read_result_table(project: Path) -> tuple[list[str], list[dict[str, str]]]:
    with (project / "eval_results.csv").open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def _write_result_table(
    project: Path,
    headers: list[str],
    rows: list[dict[str, str]],
) -> None:
    with (project / "eval_results.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _single_result_project(tmp_path: Path) -> tuple[Path, list[str], dict[str, str]]:
    project = _project(tmp_path)
    headers, rows = _read_result_table(project)
    return project, headers, rows[0]


def _project_with_run_timestamps(
    tmp_path: Path,
    values: list[tuple[str, str]],
) -> Path:
    project = _project(tmp_path)
    headers, canonical_rows = _read_result_table(project)
    rows: list[dict[str, str]] = []
    for index, (run_id, reviewed_at) in enumerate(values):
        row = canonical_rows[index % len(canonical_rows)].copy()
        row["run_id"] = run_id
        row["reviewed_at"] = reviewed_at
        row["trial_id"] = f"trial_{index:03d}"
        rows.append(row)
    _write_result_table(project, headers, rows)
    return project


def test_valid_eval_results_pass() -> None:
    result = validate_eval_results(CUSTOMER_SUPPORT)

    assert result.valid
    assert result.row_count == 6
    assert classify_behavioral_evidence(CUSTOMER_SUPPORT).state == "available"


def test_missing_eval_results_are_not_provided(tmp_path: Path) -> None:
    project = tmp_path / "project"
    copytree(CUSTOMER_SUPPORT, project)
    (project / "eval_results.csv").unlink()

    evidence = classify_behavioral_evidence(project)

    assert evidence.state == "not_provided"
    assert evidence.summary is None


def test_header_only_eval_results_are_empty(tmp_path: Path) -> None:
    project = tmp_path / "project"
    copytree(CUSTOMER_SUPPORT, project)
    header = (project / "eval_results.csv").read_text(encoding="utf-8").splitlines()[0]
    (project / "eval_results.csv").write_text(header + "\n", encoding="utf-8")

    evidence = classify_behavioral_evidence(project)

    assert evidence.state == "empty"
    assert evidence.summary is None


def test_invalid_eval_results_fail(tmp_path: Path) -> None:
    project = tmp_path / "project"
    copytree(CUSTOMER_SUPPORT, project)
    (project / "eval_results.csv").write_text(
        "\n".join(
            [
                "run_id,case_id,candidate,evaluator,actual_route,expected_route,route_match,passed,score,failure_category,failure_reason,observed_output_path,reviewed_by,reviewed_at,notes",
                "run_001,refund_boundary_case_001,gpt-4.1-mini,human_review,send,escalate,maybe,true,1.4,,,,ai_quality,2026-05-23,bad row",
            ]
        ),
        encoding="utf-8",
    )

    result = validate_eval_results(project)
    evidence = classify_behavioral_evidence(project)

    assert not result.valid
    assert result.issues
    assert all(issue.source == "eval_results" for issue in result.issues)
    assert evidence.state == "invalid"
    assert evidence.summary is None
    assert any("actual_route" in issue.path for issue in result.issues)
    assert any("route_match" in issue.path for issue in result.issues)
    assert any("score" in issue.path for issue in result.issues)


def test_unknown_case_id_in_results_fails_project_check(tmp_path: Path) -> None:
    project = tmp_path / "project"
    copytree(CUSTOMER_SUPPORT, project)
    text = (project / "eval_results.csv").read_text(encoding="utf-8")
    text = text.replace("refund_boundary_case_001", "unknown_case_999", 1)
    (project / "eval_results.csv").write_text(text, encoding="utf-8")

    result = check_project(project)

    assert not result.valid
    assert any("Unknown eval case id" in issue.message for issue in result.issues)


def test_enriched_eval_results_validate_and_calculate_boundary_metrics(tmp_path: Path) -> None:
    project = tmp_path / "project"
    copytree(CUSTOMER_SUPPORT, project)
    cases = yaml.safe_load((project / "eval_cases.yaml").read_text(encoding="utf-8"))["eval_cases"]
    anchor = cases[0]
    variant = cases[1]
    anchor["boundary"] = {
        "family_id": "refund_family",
        "anchor_case_id": anchor["id"],
        "controlling_fact": "wording",
        "variation_type": "anchor",
        "before_value": "base",
        "after_value": "base",
    }
    variant["boundary"] = {
        "family_id": "refund_family",
        "anchor_case_id": anchor["id"],
        "controlling_fact": "wording",
        "variation_type": "semantic_invariance",
        "before_value": "base",
        "after_value": "paraphrase",
    }
    (project / "eval_cases.yaml").write_text(
        yaml.safe_dump({"eval_cases": [anchor, variant]}, sort_keys=False),
        encoding="utf-8",
    )

    headers = [
        "run_id", "case_id", "candidate", "evaluator", "actual_route", "expected_route",
        "route_match", "passed", "score", "failure_category", "failure_reason",
        "observed_output_path", "reviewed_by", "reviewed_at", "notes", "trial_id",
        "actual_workflow_route", "workflow_route_match", "trajectory_pass",
        "end_state_pass", "prohibited_action_occurred",
    ]
    anchor_route = anchor["expected_route"]
    variant_route = variant["expected_route"]
    variant_mismatch_route = "show" if variant_route != "show" else "escalate"
    rows = [
        ["run_002", anchor["id"], "candidate", "harness", anchor_route, anchor_route, "true", "true", "1", "", "", "", "qa", "2026-06-18", "", "trial_1", "act", "true", "true", "true", "false"],
        ["run_002", variant["id"], "candidate", "harness", variant_route, variant_route, "true", "true", "1", "", "", "", "qa", "2026-06-18", "", "trial_1", "act", "true", "true", "true", "false"],
        ["run_002", anchor["id"], "candidate", "harness", anchor_route, anchor_route, "true", "true", "1", "", "", "", "qa", "2026-06-18", "", "trial_2", "act", "true", "true", "true", "false"],
        ["run_002", variant["id"], "candidate", "harness", variant_mismatch_route, variant_route, "false", "false", "0", "route", "unstable", "", "qa", "2026-06-18", "", "trial_2", "answer", "false", "false", "false", "true"],
    ]
    with (project / "eval_results.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)
        writer.writerows(rows)

    validation = validate_eval_results(project)
    summary = summarize_eval_results(project)

    assert validation.valid
    assert summary is not None
    assert summary.workflow_route_accuracy == 0.75
    assert summary.prohibited_action_rate == 0.25
    assert summary.boundary_family_count == 1
    assert summary.complete_boundary_family_count == 1
    assert summary.contrast_family_reliability == 0.0
    assert summary.semantic_stability == 0.5
    assert summary.repeated_case_count == 2
    assert summary.repeated_run_reliability == 0.5
    report = generate_report(project)
    assert "Workflow-route accuracy: 75%" in report
    assert "Prohibited-action rate: 25%" in report
    assert "Contrast-family reliability: 0%" in report
    assert "Semantic stability: 50%" in report
    assert "Repeated-run reliability: 50%" in report


def test_escalation_metrics_are_calculated_from_enriched_results() -> None:
    summary = summarize_eval_results(CUSTOMER_SUPPORT)

    assert summary is not None
    assert summary.required_escalation_recall == 2 / 3
    assert summary.over_escalation_rate == 2 / 3
    assert summary.destination_accuracy == 1 / 3
    assert summary.context_preservation_rate == 2 / 3
    assert summary.fallback_success_rate == 1.0
    assert summary.resume_success_rate == 1 / 3
    assert summary.late_escalation_rate == 1 / 3
    assert summary.workflow_assignment_accuracy == 0.5
    assert summary.model_policy_compliance == 2 / 3
    assert summary.routing_policy_version_match_rate == 1.0
    assert summary.deterministic_path_compliance == 1 / 3


def test_invalid_enriched_result_values_fail(tmp_path: Path) -> None:
    project = tmp_path / "project"
    copytree(CUSTOMER_SUPPORT, project)
    path = project / "eval_results.csv"
    path.write_text(
        "\n".join(
            [
                "run_id,case_id,candidate,evaluator,actual_route,expected_route,route_match,passed,score,failure_category,failure_reason,observed_output_path,reviewed_by,reviewed_at,notes,trial_id,actual_workflow_route,workflow_route_match,trajectory_pass,end_state_pass,prohibited_action_occurred,destination_match,payload_complete",
                "run_1,refund_boundary_case_001,candidate,harness,escalate,escalate,true,true,1,,,,qa,2026-06-18,,trial_1,execute,maybe,true,true,false,maybe,nope",
            ]
        ),
        encoding="utf-8",
    )

    result = validate_eval_results(project)

    assert not result.valid
    assert any("actual_workflow_route" in issue.path for issue in result.issues)
    assert any("workflow_route_match" in issue.path for issue in result.issues)
    assert any("destination_match" in issue.path for issue in result.issues)
    assert any("payload_complete" in issue.path for issue in result.issues)


def test_truncated_result_row_fails_closed(tmp_path: Path) -> None:
    project = _project(tmp_path)
    headers, _ = _read_result_table(project)
    (project / "eval_results.csv").write_text(
        ",".join(headers) + "\nrun_001,refund_boundary_case_001\n",
        encoding="utf-8",
    )

    result = validate_eval_results(project)
    evidence = classify_behavioral_evidence(project)

    assert not result.valid
    assert any(
        issue.path.endswith("row[2].candidate")
        and issue.message == "Must be a non-empty value."
        for issue in result.issues
    )
    assert evidence.state == "invalid"
    assert evidence.summary is None


@pytest.mark.parametrize("field", NONEMPTY_EVAL_RESULT_FIELDS)
@pytest.mark.parametrize("blank", ["", "   "])
def test_required_result_values_must_be_nonempty(
    tmp_path: Path,
    field: str,
    blank: str,
) -> None:
    project, headers, row = _single_result_project(tmp_path)
    row[field] = blank
    _write_result_table(project, headers, [row])

    result = validate_eval_results(project)

    assert not result.valid
    assert any(
        issue.path.endswith(f"row[2].{field}")
        and issue.message == "Must be a non-empty value."
        for issue in result.issues
    )


def test_blank_optional_result_values_remain_valid(tmp_path: Path) -> None:
    project, headers, row = _single_result_project(tmp_path)
    for field in (
        "trial_id",
        "failure_category",
        "failure_reason",
        "observed_output_path",
        "notes",
        "actual_workflow_route",
        "workflow_route_match",
        "trajectory_pass",
        "end_state_pass",
        "prohibited_action_occurred",
        "actual_destination",
        "destination_match",
        "payload_complete",
        "fallback_success",
        "resume_success",
        "late_escalation",
        "actual_workflow_id",
        "actual_model_id",
        "routing_policy_version",
        "routing_reason",
    ):
        if field in row:
            row[field] = ""
    _write_result_table(project, headers, [row])

    assert validate_eval_results(project).valid


@pytest.mark.parametrize(
    "timestamp",
    [
        "2026-06-22",
        "2026-06-22T09:30:00-07:00",
        "2026-06-22T12:30:00+04:00",
        "2026-06-22T16:30:00Z",
        "2026-06-22T09:30:00.123456-07:00",
        "2026-06-22T16:30:00.123456Z",
    ],
)
def test_valid_review_timestamps_pass(tmp_path: Path, timestamp: str) -> None:
    project, headers, row = _single_result_project(tmp_path)
    row["reviewed_at"] = timestamp
    _write_result_table(project, headers, [row])

    assert validate_eval_results(project).valid


@pytest.mark.parametrize(
    "timestamp",
    [
        "2026-06-22T09:30:00",
        "2026-06-22T09:30:00.123456",
    ],
)
def test_timezone_naive_review_timestamps_fail(
    tmp_path: Path,
    timestamp: str,
) -> None:
    project, headers, row = _single_result_project(tmp_path)
    row["reviewed_at"] = timestamp
    _write_result_table(project, headers, [row])

    result = validate_eval_results(project)

    assert any(
        issue.path.endswith("row[2].reviewed_at")
        and issue.message
        == "Datetime values must include an explicit UTC offset or Z timezone designator."
        and issue.source == "eval_results"
        for issue in result.issues
    )


@pytest.mark.parametrize(
    "timestamp",
    [
        "2026-06-22 09:30:00",
        "06/22/2026",
        "June 22 2026",
        "2026-13-40",
        "2026-02-30",
        "2026-W26-1",
        "2026-173",
        "2026-06-22T09:30:00+0700",
        "not-a-date",
    ],
)
def test_malformed_or_unsupported_review_timestamps_fail(
    tmp_path: Path,
    timestamp: str,
) -> None:
    project, headers, row = _single_result_project(tmp_path)
    row["reviewed_at"] = timestamp
    _write_result_table(project, headers, [row])

    result = validate_eval_results(project)

    assert any(
        issue.path.endswith("row[2].reviewed_at")
        and issue.message
        == "Must be an ISO 8601 date or an ISO 8601 datetime with an explicit timezone."
        and issue.source == "eval_results"
        for issue in result.issues
    )


def test_duplicate_identity_with_trial_id_fails(tmp_path: Path) -> None:
    project, headers, row = _single_result_project(tmp_path)
    duplicate = row.copy()
    _write_result_table(project, headers, [row, duplicate])

    result = validate_eval_results(project)

    assert not result.valid
    assert any(
        issue.path.endswith("row[3].case_id")
        and "trial_id=trial_001" in issue.message
        and "first declared on row 2" in issue.message
        for issue in result.issues
    )


def test_duplicate_identity_with_blank_trial_ids_fails(tmp_path: Path) -> None:
    project, headers, row = _single_result_project(tmp_path)
    row["trial_id"] = ""
    duplicate = row.copy()
    _write_result_table(project, headers, [row, duplicate])

    result = validate_eval_results(project)

    assert any(
        "trial_id=<blank>" in issue.message
        and "first declared on row 2" in issue.message
        for issue in result.issues
    )


def test_repeated_case_with_distinct_trial_ids_passes(tmp_path: Path) -> None:
    project, headers, row = _single_result_project(tmp_path)
    duplicate = row.copy()
    duplicate["trial_id"] = "trial_002"
    _write_result_table(project, headers, [row, duplicate])

    assert validate_eval_results(project).valid


@pytest.mark.parametrize("field", ["run_id", "candidate"])
def test_same_case_and_trial_in_different_identity_scope_passes(
    tmp_path: Path,
    field: str,
) -> None:
    project, headers, row = _single_result_project(tmp_path)
    duplicate = row.copy()
    duplicate[field] = f"different_{field}"
    _write_result_table(project, headers, [row, duplicate])

    assert validate_eval_results(project).valid


@pytest.mark.parametrize("field", ["run_id", "candidate", "case_id"])
def test_duplicate_check_skips_missing_required_identity_fields(
    tmp_path: Path,
    field: str,
) -> None:
    project, headers, row = _single_result_project(tmp_path)
    row[field] = ""
    _write_result_table(project, headers, [row, row.copy()])

    result = validate_eval_results(project)

    assert not any("Duplicate eval result identity" in issue.message for issue in result.issues)


def test_blank_output_reference_passes(tmp_path: Path) -> None:
    project, headers, row = _single_result_project(tmp_path)
    row["observed_output_path"] = ""
    _write_result_table(project, headers, [row])

    assert validate_eval_results(project).valid


def test_existing_regular_output_reference_passes(tmp_path: Path) -> None:
    project, headers, row = _single_result_project(tmp_path)
    row["observed_output_path"] = "eval_runs/run_001/refund_boundary_case_001.md"
    _write_result_table(project, headers, [row])

    assert validate_eval_results(project).valid


@pytest.mark.parametrize(
    ("reference", "message"),
    [
        ("missing/output.md", "Referenced output file does not exist or is not a regular file."),
        ("eval_runs/", "Must be a project-relative filesystem path."),
        ("/etc/passwd", "Must be a project-relative filesystem path."),
        (r"C:\private\output.md", "Must be a project-relative filesystem path."),
        ("C:/private/output.md", "Must be a project-relative filesystem path."),
        (r"\\server\share\output.md", "Must be a project-relative filesystem path."),
        (r"\eval_runs\run_001\refund_boundary_case_001.md", "Must be a project-relative filesystem path."),
        (r"eval_runs\run_001\refund_boundary_case_001.md", "Must be a project-relative filesystem path."),
        ("https://example.com/output.md", "Must be a project-relative filesystem path."),
        ("file:///tmp/output.md", "Must be a project-relative filesystem path."),
        ("../outside.md", "Parent-directory traversal is not allowed."),
        (r"..\outside.md", "Must be a project-relative filesystem path."),
        ("eval_runs/../../outside.md", "Parent-directory traversal is not allowed."),
        (r"eval_runs\..\..\outside.md", "Must be a project-relative filesystem path."),
        (".", "Parent-directory traversal is not allowed."),
        ("./output.md", "Parent-directory traversal is not allowed."),
        ("eval_runs/./output.md", "Parent-directory traversal is not allowed."),
    ],
)
def test_unsafe_or_invalid_output_reference_fails(
    tmp_path: Path,
    reference: str,
    message: str,
) -> None:
    project, headers, row = _single_result_project(tmp_path)
    row["observed_output_path"] = reference
    _write_result_table(project, headers, [row])

    result = validate_eval_results(project)

    assert any(
        issue.path.endswith("row[2].observed_output_path")
        and issue.message == message
        for issue in result.issues
    )


def test_embedded_nul_output_reference_is_rejected(tmp_path: Path) -> None:
    project = _project(tmp_path)

    issue = eval_results._validate_output_reference(
        project,
        "eval_runs/\0output.md",
    )

    assert (
        issue
        == "Referenced output file does not exist or is not a regular file."
    )


def test_output_reference_final_symlink_fails(tmp_path: Path) -> None:
    project, headers, row = _single_result_project(tmp_path)
    outside = tmp_path / "outside.md"
    outside.write_text("outside\n", encoding="utf-8")
    link = project / "eval_runs" / "outside-link.md"
    try:
        link.symlink_to(outside)
    except (NotImplementedError, OSError) as exc:
        pytest.skip(f"Symlink creation is unavailable: {exc}")
    row["observed_output_path"] = "eval_runs/outside-link.md"
    _write_result_table(project, headers, [row])

    result = validate_eval_results(project)

    assert any(
        issue.message == "Referenced output file does not exist or is not a regular file."
        for issue in result.issues
    )


def test_output_reference_internal_symlink_fails(tmp_path: Path) -> None:
    project, headers, row = _single_result_project(tmp_path)
    target = project / "eval_runs" / "run_001" / "refund_boundary_case_001.md"
    link = project / "eval_runs" / "internal-link.md"
    try:
        link.symlink_to(target)
    except (NotImplementedError, OSError) as exc:
        pytest.skip(f"Symlink creation is unavailable: {exc}")
    row["observed_output_path"] = "eval_runs/internal-link.md"
    _write_result_table(project, headers, [row])

    result = validate_eval_results(project)

    assert any(
        issue.message == "Referenced output file does not exist or is not a regular file."
        for issue in result.issues
    )


def test_result_expected_route_must_match_eval_case(tmp_path: Path) -> None:
    project, headers, row = _single_result_project(tmp_path)
    row["expected_route"] = "escalate"
    _write_result_table(project, headers, [row])

    result = validate_eval_results(project)

    assert any(
        issue.path.endswith("row[2].expected_route")
        and issue.message == "Does not match eval case expected_route: show."
        for issue in result.issues
    )


def test_declared_true_route_match_must_match_derived_false(tmp_path: Path) -> None:
    project, headers, row = _single_result_project(tmp_path)
    row["route_match"] = "true"
    _write_result_table(project, headers, [row])

    result = validate_eval_results(project)

    assert any(
        issue.path.endswith("row[2].route_match")
        and issue.message
        == "Does not match the value derived from actual_route and the referenced eval case."
        for issue in result.issues
    )


def test_declared_false_route_match_must_match_derived_true(tmp_path: Path) -> None:
    project = _project(tmp_path)
    headers, rows = _read_result_table(project)
    row = rows[2]
    row["route_match"] = "false"
    _write_result_table(project, headers, [row])

    result = validate_eval_results(project)

    assert any(
        issue.path.endswith("row[2].route_match")
        and issue.message
        == "Does not match the value derived from actual_route and the referenced eval case."
        for issue in result.issues
    )


def test_matching_route_evidence_remains_valid(tmp_path: Path) -> None:
    project = _project(tmp_path)

    assert validate_eval_results(project).valid


def test_route_match_rates_are_derived_for_whole_and_selected_scope(
    tmp_path: Path,
) -> None:
    project = _project(tmp_path)

    whole = summarize_eval_results(project)
    selected = summarize_selected_eval_results(
        project,
        run_id="run_002",
        candidate="gpt-4.1-mini",
    )

    assert whole is not None
    assert whole.route_match_rate == 0.5
    assert selected.route_match_rate == 0.5


def test_selected_scope_normalizes_surrounding_whitespace(tmp_path: Path) -> None:
    project = _project(tmp_path)
    headers, rows = _read_result_table(project)
    for row in rows:
        row["run_id"] = f"  {row['run_id']}  "
        row["candidate"] = f"  {row['candidate']}  "
    _write_result_table(project, headers, rows)

    summary = summarize_selected_eval_results(
        project,
        run_id=" run_002 ",
        candidate=" gpt-4.1-mini ",
    )

    assert summary.row_count == 6
    assert summary.route_match_rate == 0.5


def test_direct_summaries_reject_invalid_results(tmp_path: Path) -> None:
    project, headers, row = _single_result_project(tmp_path)
    row["route_match"] = "true"
    _write_result_table(project, headers, [row])

    with pytest.raises(ValueError, match=r"^Cannot summarize invalid eval results\.$"):
        summarize_eval_results(project)
    with pytest.raises(ValueError, match=r"^Cannot summarize invalid eval results\.$"):
        summarize_selected_eval_results(
            project,
            run_id=row["run_id"],
            candidate=row["candidate"],
        )


@pytest.mark.parametrize("case_state", ["missing", "invalid"])
def test_direct_summaries_require_valid_eval_cases(
    tmp_path: Path,
    case_state: str,
) -> None:
    project = _project(tmp_path)
    cases_path = project / "eval_cases.yaml"
    if case_state == "missing":
        cases_path.unlink()
    else:
        cases_path.write_text("eval_cases: invalid\n", encoding="utf-8")

    with pytest.raises(
        ValueError,
        match=r"^Cannot summarize eval results without valid eval cases\.$",
    ):
        summarize_eval_results(project)
    with pytest.raises(
        ValueError,
        match=r"^Cannot summarize eval results without valid eval cases\.$",
    ):
        summarize_selected_eval_results(
            project,
            run_id="run_002",
            candidate="gpt-4.1-mini",
        )


def test_invalid_route_evidence_classifies_as_invalid(tmp_path: Path) -> None:
    project, headers, row = _single_result_project(tmp_path)
    row["route_match"] = "true"
    _write_result_table(project, headers, [row])

    evidence = classify_behavioral_evidence(project)

    assert evidence.state == "invalid"
    assert evidence.summary is None


def test_pass_rate_remains_based_on_declared_passed(tmp_path: Path) -> None:
    project = _project(tmp_path)
    headers, rows = _read_result_table(project)
    matching_row = rows[2]
    assert matching_row["route_match"] == "true"
    matching_row["passed"] = "false"
    _write_result_table(project, headers, [matching_row])

    summary = summarize_eval_results(project)

    assert summary is not None
    assert summary.route_match_rate == 1.0
    assert summary.pass_rate == 0.0


@pytest.mark.parametrize("score", ["nan", "NaN", "inf", "-inf"])
def test_nonfinite_scores_fail_validation(tmp_path: Path, score: str) -> None:
    project, headers, row = _single_result_project(tmp_path)
    row["score"] = score
    _write_result_table(project, headers, [row])

    result = validate_eval_results(project)

    assert not result.valid
    assert any(
        issue.path.endswith("row[2].score")
        and issue.message == "Must be numeric from 0 to 1."
        for issue in result.issues
    )


def test_latest_run_uses_newest_timestamp_not_last_row(tmp_path: Path) -> None:
    project = _project_with_run_timestamps(
        tmp_path,
        [
            ("run_new", "2026-06-23"),
            ("run_old", "2026-06-22"),
        ],
    )

    summary = summarize_eval_results(project)

    assert summary is not None
    assert summary.latest_run_id == "run_new"


def test_latest_run_uses_greatest_timestamp_within_each_run(
    tmp_path: Path,
) -> None:
    project = _project_with_run_timestamps(
        tmp_path,
        [
            ("run_a", "2026-06-20"),
            ("run_b", "2026-06-21"),
            ("run_a", "2026-06-22"),
        ],
    )

    summary = summarize_eval_results(project)

    assert summary is not None
    assert summary.latest_run_id == "run_a"


def test_later_recorded_date_beats_earlier_late_night_instant(
    tmp_path: Path,
) -> None:
    project = _project_with_run_timestamps(
        tmp_path,
        [
            ("run_date", "2026-06-23"),
            ("run_instant", "2026-06-22T23:59:59-07:00"),
        ],
    )

    summary = summarize_eval_results(project)

    assert summary is not None
    assert summary.latest_run_id == "run_date"


def test_same_date_datetime_orders_by_utc_instant(tmp_path: Path) -> None:
    project = _project_with_run_timestamps(
        tmp_path,
        [
            ("run_early", "2026-06-22T09:00:00-07:00"),
            ("run_late", "2026-06-22T10:00:00-07:00"),
        ],
    )

    summary = summarize_eval_results(project)

    assert summary is not None
    assert summary.latest_run_id == "run_late"


def test_same_date_datetime_is_more_precise_than_date_only(
    tmp_path: Path,
) -> None:
    project = _project_with_run_timestamps(
        tmp_path,
        [
            ("run_date", "2026-06-22"),
            ("run_datetime", "2026-06-22T00:00:00+00:00"),
        ],
    )

    summary = summarize_eval_results(project)

    assert summary is not None
    assert summary.latest_run_id == "run_datetime"


def test_date_only_tie_uses_lexical_run_id(tmp_path: Path) -> None:
    project = _project_with_run_timestamps(
        tmp_path,
        [
            ("run_a", "2026-06-22"),
            ("run_z", "2026-06-22"),
        ],
    )

    summary = summarize_eval_results(project)

    assert summary is not None
    assert summary.latest_run_id == "run_z"


def test_equivalent_datetime_instants_use_lexical_run_id(
    tmp_path: Path,
) -> None:
    project = _project_with_run_timestamps(
        tmp_path,
        [
            ("run_a", "2026-06-22T09:30:00-07:00"),
            ("run_z", "2026-06-22T12:30:00-04:00"),
        ],
    )

    summary = summarize_eval_results(project)

    assert summary is not None
    assert summary.latest_run_id == "run_z"


def test_latest_run_is_independent_of_row_order(tmp_path: Path) -> None:
    values = [
        ("run_a", "2026-06-20"),
        ("run_b", "2026-06-22T10:00:00-07:00"),
        ("run_c", "2026-06-21"),
        ("run_b", "2026-06-22T09:00:00-07:00"),
    ]
    project = _project_with_run_timestamps(tmp_path, values)
    first = summarize_eval_results(project)
    headers, rows = _read_result_table(project)
    random.Random(42).shuffle(rows)
    _write_result_table(project, headers, rows)
    second = summarize_eval_results(project)

    assert first is not None
    assert second is not None
    assert first.latest_run_id == second.latest_run_id == "run_b"


def test_canonical_latest_run_remains_deterministic() -> None:
    summary = summarize_eval_results(CUSTOMER_SUPPORT)

    assert summary is not None
    assert summary.latest_run_id == "run_002"
