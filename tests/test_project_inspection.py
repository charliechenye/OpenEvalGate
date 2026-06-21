from pathlib import Path
from shutil import copytree

import yaml
import pytest

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


def test_action_matrix_context_is_true_false_or_unknown(
    tmp_path: Path,
) -> None:
    populated = _copy_project(tmp_path / "populated")
    assert inspect_project(populated).context.has_tool_actions is True

    empty = _copy_project(tmp_path / "empty")
    matrix = empty / "action_risk_matrix.csv"
    header = matrix.read_text(encoding="utf-8").splitlines()[0]
    matrix.write_text(header + "\n", encoding="utf-8")
    assert inspect_project(empty).context.has_tool_actions is False

    missing = _copy_project(tmp_path / "missing")
    (missing / "action_risk_matrix.csv").unlink()
    missing_inspection = inspect_project(missing)
    assert missing_inspection.context.has_tool_actions is None
    assert not missing_inspection.check.valid

    malformed = _copy_project(tmp_path / "malformed")
    (malformed / "action_risk_matrix.csv").write_text(
        "action,risk_tier\nlookup,low\n",
        encoding="utf-8",
    )
    malformed_inspection = inspect_project(malformed)
    assert malformed_inspection.context.has_tool_actions is None
    assert not malformed_inspection.check.valid


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
