from pathlib import Path
from shutil import copytree

import yaml
import pytest
import csv

from openevalgate.action_risk import (
    ActionRiskReview,
    ActionRiskRow,
    inspect_action_risk_matrix,
)
from openevalgate.cli import main
from openevalgate.launch_gate_review import NON_EVIDENCE_VALUES
from openevalgate.project_inspection import inspect_project
from openevalgate.project_inspection import (
    _high_risk_actions_without_controls,
)
from openevalgate.validator import check_project


ROOT = Path(__file__).resolve().parents[1]
CUSTOMER_SUPPORT = ROOT / "examples" / "customer_support_assistant"

SCOPED_RUN_ID = "run_002"
SCOPED_CANDIDATE = "gpt-4.1-mini"
SCOPED_EVALUATOR = "human_review"
HIGH_RISK_HANDOFF_CASE_ID = "refund_abuse_history_002"

def _copy_project(tmp_path: Path) -> Path:
    project = tmp_path / "project"
    copytree(CUSTOMER_SUPPORT, project)
    return project


def _replace_gate_status(project: Path, gate: str, status: str) -> None:
    path = project / "launch_gate_review.md"
    lines = path.read_text(encoding="utf-8").splitlines()
    updated = []
    for line in lines:
        if line.startswith(f"| {gate} |"):
            cells = line.split("|")
            cells[2] = f" {status} "
            line = "|".join(cells)
        updated.append(line)
    path.write_text("\n".join(updated) + "\n", encoding="utf-8")


def _remove_gate(project: Path, gate: str) -> None:
    path = project / "launch_gate_review.md"
    lines = [
        line
        for line in path.read_text(encoding="utf-8").splitlines()
        if not line.startswith(f"| {gate} |")
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_handoff_result_variant(
    source: Path,
    target: Path,
    *,
    failing_case_id: str | None,
    clear_output_paths: bool,
) -> None:
    with source.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        headers = list(reader.fieldnames or [])
        rows = list(reader)

        found_failure_row = False

        for row in rows:
            # Normalize core route evidence to a passing baseline.
            row["actual_route"] = row["expected_route"]
            row["route_match"] = "true"
            row["passed"] = "true"
            row["score"] = "1"
            row["failure_category"] = ""
            row["failure_reason"] = ""

            # Normalize every field inspected by # project_inspection._critical_escalation_failures().
            row["workflow_route_match"] = "true"
            row["destination_match"] = ""
            row["payload_complete"] = ""
            row["resume_success"] = ""

            # Scoped result output references are relative to the run directory.
            # Blank them so this test isolates result-source selection rather than output-artifact path validation.
            if clear_output_paths:
                row["observed_output_path"] = ""

            if row["case_id"] == failing_case_id:
                found_failure_row = True
                row["workflow_route_match"] = "false"
                row["passed"] = "false"
                row["score"] = "0"
                row["failure_category"] = "under_escalation"
                row["failure_reason"] = (
                    "Intentional high-risk handoff regression for source-selection "
                    "testing."
                )

        if failing_case_id is not None and not found_failure_row:
            raise AssertionError(f"Expected result row was not found: {failing_case_id}")

        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=headers, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)

def _prepare_scoped_handoff_results(
    project: Path,
    *,
    root_fails: bool,
    scoped_fails: bool,
) -> Path:
    root_results = project / "eval_results.csv"

    _write_handoff_result_variant(
        root_results,
        root_results,
        failing_case_id=(HIGH_RISK_HANDOFF_CASE_ID if root_fails else None),
        clear_output_paths=False,
    )

    root_manifest = project / "run_manifest.yaml"
    if root_manifest.exists():
        root_manifest.unlink()

    run_dir = project / "eval_runs" / SCOPED_RUN_ID
    scoped_results = run_dir / "eval_results.csv"
    _write_handoff_result_variant(
        root_results,
        scoped_results,
        failing_case_id=(HIGH_RISK_HANDOFF_CASE_ID if scoped_fails else None),
        clear_output_paths=True,
    )
    manifest = {
        "schema_version": "1",
        "run": {"id": SCOPED_RUN_ID, "status": "complete",},
        "candidate": {"id": SCOPED_CANDIDATE, "version": "project-inspection-test-v1",},
        "evaluation": {"kind": "human", "evaluator": {"id": SCOPED_EVALUATOR,}, },
        "outputs": { "results": { "path": "eval_results.csv", }, },
    }

    (run_dir / "run_manifest.yaml").write_text(
        yaml.safe_dump(manifest, sort_keys=False),
        encoding="utf-8",
    )

    return scoped_results.resolve(strict=False)

def test_valid_partial_declaration_passes_check_but_blocks_launch() -> None:
    inspection = inspect_project(CUSTOMER_SUPPORT)

    assert inspection.check.valid
    assert inspection.valid
    assert inspection.launch_blocked
    assert "missing_monitoring" in {
        blocker.id for blocker in inspection.hard_blockers
    }


def test_valid_fail_declaration_passes_check_but_blocks_launch(
    tmp_path: Path,
) -> None:
    project = _copy_project(tmp_path)
    _replace_gate_status(project, "Rollback gate", "fail")

    inspection = inspect_project(project)

    assert inspection.check.valid
    assert inspection.valid
    assert inspection.launch_blocked
    assert "missing_rollback" in {
        blocker.id for blocker in inspection.hard_blockers
    }


def test_missing_applicable_gate_is_launch_blocked_not_malformed(
    tmp_path: Path,
) -> None:
    project = _copy_project(tmp_path)
    _remove_gate(project, "Rollback gate")

    inspection = inspect_project(project)

    assert inspection.check.valid
    assert inspection.valid
    assert inspection.launch_blocked
    evaluation = next(
        item
        for item in inspection.evaluations
        if item.gate == "rollback gate"
    )
    assert evaluation.actual_status == "missing"
    assert evaluation.outcome == "Blocked"


def test_unsupported_status_fails_structural_check(
    tmp_path: Path,
    capsys,
) -> None:
    project = _copy_project(tmp_path)
    _replace_gate_status(project, "Rollback gate", "warning")

    inspection = inspect_project(project)

    assert not inspection.check.valid
    assert not inspection.valid
    assert main(["check", str(project)]) == 1
    assert "Unsupported launch-gate status" in capsys.readouterr().out


def test_duplicate_standard_gate_fails_structural_check(
    tmp_path: Path,
) -> None:
    project = _copy_project(tmp_path)
    path = project / "launch_gate_review.md"
    path.write_text(
        path.read_text(encoding="utf-8")
        + "| Tail-risk/P0 failure mode gate | pass | duplicate | None | owner |\n",
        encoding="utf-8",
    )

    result = check_project(project)

    assert not result.valid
    assert any(
        "Duplicate standard launch-gate declaration" in issue.message
        for issue in result.issues
    )


def test_disallowed_not_applicable_is_policy_issue_and_check_failure(
    tmp_path: Path,
) -> None:
    project = _copy_project(tmp_path)
    _replace_gate_status(project, "Scope gate", "not_applicable")

    inspection = inspect_project(project)

    assert inspection.check.valid
    assert not inspection.valid
    assert inspection.policy_issues
    assert inspection.launch_blocked


@pytest.mark.parametrize(
    ("state", "expected_has_tool_actions", "expected_check_valid"),
    [
        ("populated", True, True),
        ("empty", False, True),
        ("missing", None, False),
        ("malformed", None, False),
    ],
    ids=["populated", "empty", "missing", "malformed"],
)
def test_action_matrix_context_is_true_false_or_unknown(
    tmp_path: Path,
    state: str,
    expected_has_tool_actions: bool | None,
    expected_check_valid: bool,
) -> None:
    project = _copy_project(tmp_path)
    matrix = project / "action_risk_matrix.csv"
    if state == "empty":
        header = matrix.read_text(encoding="utf-8").splitlines()[0]
        matrix.write_text(header + "\n", encoding="utf-8")
    elif state == "missing":
        matrix.unlink()
    elif state == "malformed":
        matrix.write_text(
            "action,risk_tier\nlookup,low\n",
            encoding="utf-8",
        )

    inspection = inspect_project(project)

    assert inspection.context.has_tool_actions is expected_has_tool_actions
    assert inspection.check.valid is expected_check_valid


def test_unreadable_action_matrix_makes_tool_scope_unknown(
    tmp_path: Path,
    monkeypatch,
) -> None:
    path = tmp_path / "action_risk_matrix.csv"
    path.write_text(
        "action,risk_tier,deterministic_gate,human_review_required\n",
        encoding="utf-8",
    )

    def _raise_os_error(*args, **kwargs):
        raise OSError("permission denied")

    monkeypatch.setattr(Path, "open", _raise_os_error)
    review = inspect_action_risk_matrix(path)

    assert review.present
    assert not review.valid
    assert "permission denied" in review.issues[0].message


def test_invalid_eval_and_low_risk_action_leave_high_impact_unknown(
    tmp_path: Path,
) -> None:
    project = _copy_project(tmp_path)
    (project / "eval_cases.yaml").write_text(
        "eval_cases: []",
        encoding="utf-8",
    )
    (project / "action_risk_matrix.csv").write_text(
        "\n".join(
            [
                "action,risk_tier,deterministic_gate,human_review_required",
                "lookup,low,authorization,false",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    inspection = inspect_project(project)

    assert inspection.context.high_impact is None
    assert not inspection.check.valid


def test_low_impact_missing_human_gate_is_nonblocking_but_design_is_required(
    tmp_path: Path,
) -> None:
    project = _copy_project(tmp_path)
    eval_path = project / "eval_cases.yaml"
    document = yaml.safe_load(eval_path.read_text(encoding="utf-8"))
    for case in document["eval_cases"]:
        case["risk_tier"] = "low"
    eval_path.write_text(
        yaml.safe_dump(document, sort_keys=False),
        encoding="utf-8",
    )
    matrix = project / "action_risk_matrix.csv"
    header = matrix.read_text(encoding="utf-8").splitlines()[0]
    matrix.write_text(header + "\n", encoding="utf-8")
    _remove_gate(project, "Human escalation gate")
    (project / "human_escalation_design.md").unlink()

    inspection = inspect_project(project)
    evaluation = next(
        item
        for item in inspection.evaluations
        if item.gate == "human escalation gate"
    )

    assert inspection.context.high_impact is False
    assert evaluation.outcome == "Not applicable"
    assert evaluation.blocker is None
    assert not inspection.check.valid
    assert "human_escalation_design.md" in inspection.check.missing_required


def test_unsafe_action_blocker_remains_independent_of_gate_pass(
    tmp_path: Path,
) -> None:
    project = _copy_project(tmp_path)
    (project / "action_risk_matrix.csv").write_text(
        "\n".join(
            [
                "action,risk_tier,deterministic_gate,human_review_required",
                "issue_refund,high,,false",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    inspection = inspect_project(project)

    assert next(
        item
        for item in inspection.evaluations
        if item.gate == "tool/action safety gate"
    ).outcome == "Satisfied"
    assert "ungated_high_risk_action" in {
        blocker.id for blocker in inspection.hard_blockers
    }


def test_missing_policy_preserves_legacy_full_file_behavioral_blocker() -> None:
    inspection = inspect_project(CUSTOMER_SUPPORT)

    assert "critical_escalation_regression" in {
        blocker.id for blocker in inspection.hard_blockers
    }


def test_invalid_policy_skips_scope_dependent_behavioral_blocker(
    tmp_path: Path,
) -> None:
    project = _copy_project(tmp_path)
    (project / "review_policy.yaml").write_text(
        "\n".join(
            [
                'schema_version: "1"',
                "requested_mode: controlled_launch",
                "evaluation_scope:",
                "  run_id: run_002",
                "  candidate: gpt-4.1-mini",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    inspection = inspect_project(project)

    assert not inspection.check.valid
    assert "critical_escalation_regression" not in {
        blocker.id for blocker in inspection.hard_blockers
    }


@pytest.mark.parametrize("placeholder", sorted(NON_EVIDENCE_VALUES))
def test_placeholder_deterministic_gate_does_not_control_high_risk_action(
    placeholder: str,
) -> None:
    row = ActionRiskRow(
        raw_values={
            "action": "issue_refund",
            "risk_tier": "high",
            "deterministic_gate": placeholder,
            "human_review_required": "false",
        },
        normalized_values={
            "action": "issue_refund",
            "risk_tier": "high",
            "deterministic_gate": placeholder.lower(),
            "human_review_required": "false",
        },
        source_line=2,
    )

    assert _high_risk_actions_without_controls([row]) == ["issue_refund"]


def test_placeholder_deterministic_gate_is_blocked_end_to_end(
    tmp_path: Path,
) -> None:
    project = _copy_project(tmp_path)
    (project / "action_risk_matrix.csv").write_text(
        "\n".join(
            [
                "action,risk_tier,deterministic_gate,human_review_required",
                "issue_refund,high,N/A,false",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    inspection = inspect_project(project)

    assert inspection.check.action_risk_review.valid
    assert "ungated_high_risk_action" in {
        blocker.id for blocker in inspection.hard_blockers
    }


def test_action_matrix_rejects_blank_and_raw_unsupported_semantic_values(
    tmp_path: Path,
) -> None:
    path = tmp_path / "action_risk_matrix.csv"
    path.write_text(
        "\n".join(
            [
                "action,risk_tier,deterministic_gate,human_review_required",
                "lookup,,,",
                "refund,Critical,authorization,YES",
                ",low,authorization,false",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    review = inspect_action_risk_matrix(path)
    messages = [issue.message for issue in review.issues]

    assert not review.valid
    assert len(review.rows) == 3
    assert review.rows[1].raw_values["risk_tier"] == "Critical"
    assert review.rows[1].normalized_values["risk_tier"] == "critical"
    assert review.rows[1].raw_values["human_review_required"] == "YES"
    assert review.rows[1].normalized_values["human_review_required"] == "yes"
    assert "Risk tier must be nonblank for a populated row." in messages
    assert (
        "Human-review requirement must be nonblank for a populated row."
        in messages
    )
    assert (
        "Unsupported risk tier `Critical`; expected one of: high, low, "
        "medium, prohibited."
    ) in messages
    assert (
        "Unsupported human-review requirement `YES`; expected one of: "
        "false, true."
    ) in messages
    assert "Action must be nonblank for a populated row." in messages


def test_action_risk_dataclass_positional_construction_remains_compatible() -> None:
    row = ActionRiskRow({"action": "lookup"}, {"action": "lookup"}, 2)
    review = ActionRiskReview(True, True, [row], [])

    assert row.raw_cells == ()
    assert review.normalized_headers == ()
    assert review.header_positions == {}


def test_action_matrix_accepts_trimmed_headers_and_preserves_raw_cells(
    tmp_path: Path,
) -> None:
    path = tmp_path / "action_risk_matrix.csv"
    path.write_text(
        (
            " action , risk_tier ,deterministic_gate,"
            "human_review_required\n"
            " lookup , Medium , authorization , FALSE \n"
        ),
        encoding="utf-8",
    )

    review = inspect_action_risk_matrix(path)

    assert review.valid
    assert review.normalized_headers == (
        "action",
        "risk_tier",
        "deterministic_gate",
        "human_review_required",
    )
    assert review.rows[0].raw_cells == (
        " lookup ",
        " Medium ",
        " authorization ",
        " FALSE ",
    )
    assert review.rows[0].raw_values["risk_tier"] == "Medium"
    assert review.rows[0].normalized_values["risk_tier"] == "medium"
    assert review.rows[0].normalized_values["human_review_required"] == "false"


def test_action_matrix_file_edge_cases_are_deterministic(
    tmp_path: Path,
) -> None:
    empty = tmp_path / "empty.csv"
    empty.write_text("", encoding="utf-8")
    empty_review = inspect_action_risk_matrix(empty)
    assert empty_review.present
    assert not empty_review.valid
    assert empty_review.rows == []
    assert [issue.path.rsplit(":", 1)[-1] for issue in empty_review.issues] == [
        "action",
        "risk_tier",
        "deterministic_gate",
        "human_review_required",
    ]

    blank_header = tmp_path / "blank-header.csv"
    blank_header.write_text("\n", encoding="utf-8")
    blank_review = inspect_action_risk_matrix(blank_header)
    assert [issue.path.rsplit(":", 1)[-1] for issue in blank_review.issues] == [
        "header[1]",
        "action",
        "risk_tier",
        "deterministic_gate",
        "human_review_required",
    ]

    header_only = tmp_path / "header-only.csv"
    header_only.write_text(
        "action,risk_tier,deterministic_gate,human_review_required\n",
        encoding="utf-8",
    )
    header_review = inspect_action_risk_matrix(header_only)
    assert header_review.valid
    assert header_review.rows == []

    malformed = tmp_path / "malformed.csv"
    malformed.write_text(
        'action,risk_tier,deterministic_gate,human_review_required\n"x,high,,false\n',
        encoding="utf-8",
    )
    malformed_review = inspect_action_risk_matrix(malformed)
    assert not malformed_review.valid
    assert malformed_review.rows == []
    assert "Could not read action-risk matrix" in malformed_review.issues[0].message


def test_action_matrix_header_ambiguity_and_issue_order(
    tmp_path: Path,
) -> None:
    path = tmp_path / "action_risk_matrix.csv"
    path.write_text(
        "\n".join(
            [
                (
                    "action,,risk_tier,risk_tier,extra,extra,"
                    "human_review_required"
                ),
                ",,low,high,value,value,maybe,unexpected",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    review = inspect_action_risk_matrix(path)

    assert not review.valid
    assert [issue.message for issue in review.issues] == [
        "Action-risk header name must be nonblank.",
        "Duplicate action-risk header: risk_tier.",
        "Duplicate action-risk header: extra.",
        "Required action-risk column is missing.",
        "Action-risk row contains more cells than the header.",
        "Action must be nonblank for a populated row.",
        (
            "Unsupported human-review requirement `maybe`; expected one of: "
            "false, true."
        ),
    ]
    assert "risk_tier" not in review.rows[0].raw_values
    assert "extra" not in review.rows[0].raw_values


@pytest.mark.parametrize(
    ("header", "row", "duplicate_field", "expected_risk_tier"),
    [
        (
            (
                "action,risk_tier,risk_tier,deterministic_gate,"
                "human_review_required"
            ),
            "refund,low,high,,false",
            "risk_tier",
            None,
        ),
        (
            (
                "action,risk_tier,extra,extra,deterministic_gate,"
                "human_review_required"
            ),
            "refund,high,a,b,,false",
            "extra",
            "high",
        ),
    ],
    ids=["duplicate-risk-tier", "duplicate-unrelated-header"],
)
def test_duplicate_action_risk_headers_preserve_only_unambiguous_values(
    tmp_path: Path,
    header: str,
    row: str,
    duplicate_field: str,
    expected_risk_tier: str | None,
) -> None:
    path = tmp_path / "action_risk_matrix.csv"
    path.write_text(f"{header}\n{row}\n", encoding="utf-8")

    review = inspect_action_risk_matrix(path)

    assert not review.valid
    assert any(
        issue.message == f"Duplicate action-risk header: {duplicate_field}."
        for issue in review.issues
    )
    if expected_risk_tier is None:
        assert "risk_tier" not in review.rows[0].raw_values
        assert "risk_tier" not in review.rows[0].normalized_values
    else:
        assert review.rows[0].raw_values["risk_tier"] == expected_risk_tier
        assert (
            review.rows[0].normalized_values["risk_tier"]
            == expected_risk_tier
        )


def test_triplicate_header_emits_one_duplicate_issue_and_unique_extra_is_valid(
    tmp_path: Path,
) -> None:
    triplicate = tmp_path / "triplicate.csv"
    triplicate.write_text(
        (
            "action,risk_tier,extra,extra,extra,deterministic_gate,"
            "human_review_required\nlookup,low,a,b,c,gate,false\n"
        ),
        encoding="utf-8",
    )
    triplicate_review = inspect_action_risk_matrix(triplicate)
    assert sum(
        issue.message == "Duplicate action-risk header: extra."
        for issue in triplicate_review.issues
    ) == 1

    unique = tmp_path / "unique.csv"
    unique.write_text(
        (
            "action,risk_tier,extra,deterministic_gate,"
            "human_review_required\nlookup,low,value,gate,false\n"
        ),
        encoding="utf-8",
    )
    unique_review = inspect_action_risk_matrix(unique)
    assert unique_review.valid
    assert unique_review.rows[0].raw_values["extra"] == "value"


def test_case_mismatched_header_is_missing_and_short_rows_are_padded(
    tmp_path: Path,
) -> None:
    path = tmp_path / "action_risk_matrix.csv"
    path.write_text(
        (
            "Action,risk_tier,deterministic_gate,human_review_required\n"
            "lookup,low\n"
        ),
        encoding="utf-8",
    )

    review = inspect_action_risk_matrix(path)

    assert not review.valid
    assert review.rows[0].raw_cells == ("lookup", "low")
    assert "action" not in review.rows[0].raw_values
    assert review.rows[0].raw_values["deterministic_gate"] == ""
    assert review.rows[0].raw_values["human_review_required"] == ""
    assert review.issues[0].path.endswith(":action")
    assert review.issues[1].path.endswith(".human_review_required")


def test_excess_only_row_is_populated_and_blank_rows_are_ignored(
    tmp_path: Path,
) -> None:
    path = tmp_path / "action_risk_matrix.csv"
    path.write_text(
        "\n".join(
            [
                "action,risk_tier,deterministic_gate,human_review_required",
                "   ,   ,   ,   ",
                ",,,,unexpected",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    review = inspect_action_risk_matrix(path)

    assert len(review.rows) == 1
    assert review.rows[0].raw_cells == ("", "", "", "", "unexpected")
    assert review.issues[0].message == (
        "Action-risk row contains more cells than the header."
    )
    assert [issue.path.rsplit(".", 1)[-1] for issue in review.issues[1:]] == [
        "action",
        "risk_tier",
        "human_review_required",
    ]


def test_invalid_mixed_action_matrix_is_untrusted_with_low_risk_evals(
    tmp_path: Path,
) -> None:
    project = _copy_project(tmp_path)
    eval_path = project / "eval_cases.yaml"
    document = yaml.safe_load(eval_path.read_text(encoding="utf-8"))
    for case in document["eval_cases"]:
        case["risk_tier"] = "low"
    eval_path.write_text(
        yaml.safe_dump(document, sort_keys=False),
        encoding="utf-8",
    )
    _write_mixed_invalid_action_matrix(project)

    inspection = inspect_project(project)

    assert not inspection.check.action_risk_review.valid
    assert inspection.context.has_tool_actions is None
    assert inspection.context.high_impact is None
    assert not inspection.check.valid
    tool_evaluation = next(
        item
        for item in inspection.evaluations
        if item.gate == "tool/action safety gate"
    )
    assert tool_evaluation.applicable is None
    assert tool_evaluation.outcome == "Blocked"
    assert "ungated_high_risk_action" not in {
        blocker.id for blocker in inspection.hard_blockers
    }


def test_invalid_mixed_action_matrix_does_not_override_high_risk_evals(
    tmp_path: Path,
) -> None:
    project = _copy_project(tmp_path)
    _write_mixed_invalid_action_matrix(project)

    inspection = inspect_project(project)

    assert not inspection.check.action_risk_review.valid
    assert inspection.context.has_tool_actions is None
    assert inspection.context.high_impact is True
    assert not inspection.check.valid
    tool_evaluation = next(
        item
        for item in inspection.evaluations
        if item.gate == "tool/action safety gate"
    )
    assert tool_evaluation.applicable is None
    assert tool_evaluation.outcome == "Blocked"
    assert "ungated_high_risk_action" not in {
        blocker.id for blocker in inspection.hard_blockers
    }


def _write_mixed_invalid_action_matrix(project: Path) -> None:
    (project / "action_risk_matrix.csv").write_text(
        "\n".join(
            [
                "action,risk_tier,deterministic_gate,human_review_required",
                "unsafe_refund,high,,false",
                "unclear_action,Critical,,false",
            ]
        )
        + "\n",
        encoding="utf-8",
    )



def test_invalid_run_identity_fails_project_validation(tmp_path: Path) -> None:
    project = _copy_project(tmp_path)
    (project / "eval_runs" / "run_002" / "run_manifest.yaml").write_text("schema_version: ['1'\n", encoding="utf-8")

    inspection = inspect_project(project)

    assert not inspection.check.valid
    assert not inspection.valid
    assert inspection.run_identity_inspection.status == "invalid"
    assert any(issue.source == "provenance" for issue in inspection.check.issues)


def test_invalid_run_identity_makes_behavioral_evidence_unavailable(tmp_path: Path) -> None:
    project = _copy_project(tmp_path)
    (project / "eval_runs" / "run_002" / "run_manifest.yaml").write_text("schema_version: ['1'\n", encoding="utf-8")

    inspection = inspect_project(project)

    assert inspection.run_identity_inspection.status == "invalid"
    assert "critical_escalation_regression" not in {blocker.id for blocker in inspection.hard_blockers}


def test_present_invalid_manifest_never_becomes_legacy(tmp_path: Path) -> None:
    project = _copy_project(tmp_path)
    (project / "eval_runs" / "run_002" / "run_manifest.yaml").write_text("schema_version: ['1'\n", encoding="utf-8")

    inspection = inspect_project(project)

    assert inspection.run_identity_inspection.status == "invalid"
    assert inspection.run_identity_inspection.results_present is False


def test_manifestless_identity_remains_structurally_usable(tmp_path: Path) -> None:
    project = _copy_project(tmp_path)
    (project / "run_manifest.yaml").unlink()

    inspection = inspect_project(project)

    assert inspection.check.valid
    assert inspection.run_identity_inspection.status == "legacy"


def test_complete_identity_does_not_remove_existing_blockers(tmp_path: Path) -> None:
    project = _copy_project(tmp_path)
    (project / "run_manifest.yaml").write_text(
        """
schema_version: "1"
run:
  id: run_002
  status: complete
candidate:
  id: gpt-4.1-mini
  version: "1"
evaluation:
  kind: human
  evaluator:
    id: human_review
outputs:
  results:
    path: eval_results.csv
""".lstrip(),
        encoding="utf-8",
    )

    inspection = inspect_project(project)

    assert inspection.run_identity_inspection.status == "complete"
    assert inspection.launch_blocked
    assert "missing_monitoring" in {blocker.id for blocker in inspection.hard_blockers}



def test_manifestless_controlled_launch_is_blocked_by_unversioned_eval_run(tmp_path: Path) -> None:
    project = _copy_project(tmp_path)
    (project / "run_manifest.yaml").unlink()

    inspection = inspect_project(project)

    assert "unversioned_eval_run" in {blocker.id for blocker in inspection.hard_blockers}

@pytest.mark.parametrize(
    ("root_fails", "scoped_fails", "expect_escalation_blocker",),
    [pytest.param( True, False, False, id="root-fails-scoped-passes", ),
     pytest.param( False, True, True, id="root-passes-scoped-fails", ), ],
)
def test_scoped_manifest_results_control_escalation_blocker(
    tmp_path: Path,
    root_fails: bool,
    scoped_fails: bool,
    expect_escalation_blocker: bool,
) -> None:
    project = _copy_project(tmp_path)
    scoped_results = _prepare_scoped_handoff_results( project, root_fails=root_fails, scoped_fails=scoped_fails, )

    inspection = inspect_project(project)
    assert inspection.run_identity_inspection.status == "complete"
    assert inspection.run_identity_inspection.results_path == scoped_results

    blockers = {blocker.id: blocker for blocker in inspection.hard_blockers}
    assert ("critical_escalation_regression" in blockers) is expect_escalation_blocker
    if expect_escalation_blocker:
        assert ( blockers["critical_escalation_regression"].evidence == HIGH_RISK_HANDOFF_CASE_ID )
