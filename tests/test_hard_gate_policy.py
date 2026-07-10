from pathlib import Path

import pytest

from openevalgate.hard_gate_policy import (
    HARD_GATE_RULES,
    HardGateContext,
    HardGateEvidence,
    evaluate_hard_gate_policy,
)
from openevalgate.launch_gate_review import (
    NON_EVIDENCE_VALUES,
    STANDARD_GATE_NAMES,
    GateRow,
    LaunchGateReview,
    canonicalize_gate_name,
    is_meaningful_evidence,
    parse_launch_gate_review,
)
from openevalgate.scorer import gate_statuses, score_gates


VALID_EVIDENCE = HardGateEvidence(True, True, True, True, True)
HARD_GATE_NAMES = tuple(rule.gate for rule in HARD_GATE_RULES)


def _review(*rows: GateRow) -> LaunchGateReview:
    normalized = [
        GateRow(
            row.gate,
            row.status,
            row.evidence,
            row.mitigation,
            row.owner,
            canonical_gate=canonicalize_gate_name(row.gate),
            source_line=row.source_line,
        )
        for row in rows
    ]
    return LaunchGateReview(normalized, normalized, frozenset(), [])


def _row(
    gate: str,
    status: str = "pass",
    evidence: str = "evidence",
) -> GateRow:
    return GateRow(gate, status, evidence, "None", "owner")


def test_standard_gate_registry_contains_all_documented_gates() -> None:
    assert len(STANDARD_GATE_NAMES) == 23
    assert len(set(STANDARD_GATE_NAMES)) == 23
    assert "rollback gate" in STANDARD_GATE_NAMES
    assert "owner signoff gate" in STANDARD_GATE_NAMES


@pytest.mark.parametrize(
    ("alias", "canonical"),
    [
        (
            "Tail-risk/P0 failure mode gate",
            "tail-risk / p0 failure mode gate",
        ),
        (
            "Routing/capability allocation gate",
            "routing / capability allocation gate",
        ),
    ],
)
def test_recognized_aliases_canonicalize(alias: str, canonical: str) -> None:
    assert canonicalize_gate_name(alias) == canonical


def test_hard_gate_order_and_blocker_ids_are_stable() -> None:
    assert HARD_GATE_NAMES == (
        "scope gate",
        "golden eval gate",
        "tail-risk / p0 failure mode gate",
        "tool/action safety gate",
        "human escalation gate",
        "observability gate",
        "rollback gate",
        "owner signoff gate",
    )
    assert tuple(rule.blocker_id for rule in HARD_GATE_RULES) == (
        "missing_scope",
        "missing_golden_eval",
        "missing_tail_risk_review",
        "missing_tool_action_safety",
        "missing_escalation_path",
        "missing_monitoring",
        "missing_rollback",
        "missing_owner_signoff",
    )


@pytest.mark.parametrize("gate", HARD_GATE_NAMES)
@pytest.mark.parametrize(
    ("status", "outcome"),
    [
        ("pass", "Satisfied"),
        ("partial", "Blocked"),
        ("fail", "Blocked"),
        ("not_applicable", "Blocked"),
        ("warning", "Invalid"),
    ],
)
def test_always_required_gate_status_matrix(
    gate: str,
    status: str,
    outcome: str,
) -> None:
    evaluation = next(
        item
        for item in evaluate_hard_gate_policy(
            _review(_row(gate, status)),
            HardGateContext(True, True),
            VALID_EVIDENCE,
        )
        if item.gate == gate
    )

    assert evaluation.outcome == outcome
    assert (evaluation.blocker is None) == (outcome == "Satisfied")
    assert (evaluation.policy_issue is not None) == (status == "not_applicable")


@pytest.mark.parametrize("gate", HARD_GATE_NAMES)
def test_missing_applicable_hard_gate_is_blocked(gate: str) -> None:
    evaluation = next(
        item
        for item in evaluate_hard_gate_policy(
            _review(),
            HardGateContext(True, True),
            VALID_EVIDENCE,
        )
        if item.gate == gate
    )

    assert evaluation.actual_status == "missing"
    assert evaluation.outcome == "Blocked"


@pytest.mark.parametrize(
    ("applicable", "status", "outcome"),
    [
        (True, "pass", "Satisfied"),
        (True, "partial", "Blocked"),
        (True, "fail", "Blocked"),
        (True, "not_applicable", "Blocked"),
        (False, "pass", "Not applicable"),
        (False, "partial", "Blocked"),
        (False, "fail", "Blocked"),
        (False, "not_applicable", "Not applicable"),
        (None, "pass", "Blocked"),
        (None, "partial", "Blocked"),
        (None, "fail", "Blocked"),
        (None, "not_applicable", "Blocked"),
    ],
)
def test_conditional_gate_status_and_applicability_matrix(
    applicable: bool | None,
    status: str,
    outcome: str,
) -> None:
    evaluation = next(
        item
        for item in evaluate_hard_gate_policy(
            _review(_row("tail-risk / p0 failure mode gate", status)),
            HardGateContext(applicable, False),
            VALID_EVIDENCE,
        )
        if item.gate == "tail-risk / p0 failure mode gate"
    )

    assert evaluation.applicable is applicable
    assert evaluation.outcome == outcome


@pytest.mark.parametrize("applicable", [False, None])
def test_missing_conditional_gate_distinguishes_not_applicable_from_unknown(
    applicable: bool | None,
) -> None:
    evaluation = next(
        item
        for item in evaluate_hard_gate_policy(
            _review(),
            HardGateContext(applicable, False),
            VALID_EVIDENCE,
        )
        if item.gate == "tail-risk / p0 failure mode gate"
    )

    assert evaluation.outcome == ("Not applicable" if applicable is False else "Blocked")


@pytest.mark.parametrize("placeholder", sorted(NON_EVIDENCE_VALUES))
def test_placeholders_do_not_satisfy_applicable_hard_gate(
    placeholder: str,
) -> None:
    assert not is_meaningful_evidence(placeholder.upper())
    evaluation = next(
        item
        for item in evaluate_hard_gate_policy(
            _review(_row("rollback gate", evidence=placeholder)),
            HardGateContext(False, False),
            VALID_EVIDENCE,
        )
        if item.gate == "rollback gate"
    )

    assert evaluation.outcome == "Blocked"


def test_structured_artifact_is_required_in_addition_to_pass_declaration() -> None:
    evidence = HardGateEvidence(False, True, True, True, True)
    evaluation = evaluate_hard_gate_policy(
        _review(_row("scope gate")),
        HardGateContext(False, False),
        evidence,
    )[0]

    assert evaluation.outcome == "Blocked"
    assert "assistant_prd.md" in evaluation.reason


def test_one_policy_blocker_reports_status_and_artifact_failures() -> None:
    evidence = HardGateEvidence(False, True, True, True, True)
    evaluation = evaluate_hard_gate_policy(
        _review(_row("scope gate", "partial")),
        HardGateContext(False, False),
        evidence,
    )[0]

    assert evaluation.blocker is not None
    assert evaluation.blocker.id == "missing_scope"
    assert (
        evaluation.reason == "Scope gate requires `pass`; actual status is `partial`. "
        "Required evidence is missing or invalid: assistant_prd.md."
    )
    assert "assistant_prd.md" in evaluation.reason


def test_duplicate_alias_rows_are_invalid_and_receive_no_score(
    tmp_path: Path,
) -> None:
    path = tmp_path / "launch_gate_review.md"
    path.write_text(
        "\n".join(
            [
                "| Gate | Status | Evidence | Required mitigation | Owner |",
                "| --- | --- | --- | --- | --- |",
                "| Tail-risk/P0 failure mode gate | pass | first | None | owner |",
                "| Tail-risk / P0 failure mode gate | pass | second | None | owner |",
            ]
        ),
        encoding="utf-8",
    )
    review = parse_launch_gate_review(path)
    evaluation = evaluate_hard_gate_policy(
        review,
        HardGateContext(True, False),
        VALID_EVIDENCE,
    )[2]

    assert review.invalid_canonical_gates == frozenset({"tail-risk / p0 failure mode gate"})
    assert not review.valid_rows
    assert evaluation.actual_status == "invalid: duplicate rows"
    assert evaluation.outcome == "Invalid"
    assert score_gates(review).score == 0


def test_unsupported_custom_gate_status_is_invalid_but_unscored(
    tmp_path: Path,
) -> None:
    path = tmp_path / "launch_gate_review.md"
    path.write_text(
        "\n".join(
            [
                "| Gate | Status | Evidence | Required mitigation | Owner |",
                "| --- | --- | --- | --- | --- |",
                "| Custom review gate | warning | evidence | None | owner |",
            ]
        ),
        encoding="utf-8",
    )
    review = parse_launch_gate_review(path)

    assert len(review.issues) == 1
    assert review.rows[0].canonical_gate is None
    assert score_gates(review).score == 0


def test_valid_custom_gate_is_allowed_but_unscored() -> None:
    result = score_gates(_review(_row("Custom review gate")))

    assert result.score == 0
    assert result.passed_gates == []
    assert result.weak_gates == []
    assert result.not_applicable_gates == []


def test_recognized_alias_receives_canonical_scoring_credit() -> None:
    result = score_gates([_row("Tail-risk/P0 failure mode gate", "pass")])

    assert result.score == 10


def test_unsupported_standard_status_receives_no_scoring_credit() -> None:
    result = score_gates([_row("Scope gate", "complete")])

    assert result.score == 0


def test_parser_preserves_raw_values_and_source_line(tmp_path: Path) -> None:
    path = tmp_path / "launch_gate_review.md"
    path.write_text(
        "\n".join(
            [
                "| Gate | Status | Evidence | Required mitigation | Owner |",
                "| --- | --- | --- | --- | --- |",
                "| Rollback gate | WARNING | evidence | mitigation | owner |",
            ]
        ),
        encoding="utf-8",
    )

    review = parse_launch_gate_review(path)

    assert review.rows[0].gate == "Rollback gate"
    assert review.rows[0].status == "WARNING"
    assert review.rows[0].source_line == 3
    assert "WARNING" in review.issues[0].message


def test_malformed_markdown_row_is_structural_issue(tmp_path: Path) -> None:
    path = tmp_path / "launch_gate_review.md"
    path.write_text(
        "| Gate | Status | Evidence | Required mitigation | Owner |\n"
        "| --- | --- | --- | --- | --- |\n"
        "| Scope gate | pass | too few cells |\n",
        encoding="utf-8",
    )

    review = parse_launch_gate_review(path)

    assert not review.rows
    assert len(review.issues) == 1


def test_non_scored_standard_gates_remain_visible_without_score_credit() -> None:
    review = _review(
        _row("Rollback gate", "partial"),
        _row("Owner signoff gate", "partial"),
    )

    result = score_gates(review)
    statuses = gate_statuses(review.valid_rows)

    assert result.score == 0
    assert [row.canonical_gate for row in result.weak_gates] == [
        "rollback gate",
        "owner signoff gate",
    ]
    assert statuses["rollback gate"] == "partial"
    assert statuses["owner signoff gate"] == "partial"


def test_duplicate_and_unsupported_rows_enter_neither_classification_path(
    tmp_path: Path,
) -> None:
    path = tmp_path / "launch_gate_review.md"
    path.write_text(
        "\n".join(
            [
                "| Gate | Status | Evidence | Required mitigation | Owner |",
                "| --- | --- | --- | --- | --- |",
                "| Rollback gate | pass | first | None | owner |",
                "| Rollback gate | partial | second | Fix it | owner |",
                "| Owner signoff gate | warning | evidence | Fix it | owner |",
            ]
        ),
        encoding="utf-8",
    )
    review = parse_launch_gate_review(path)
    result = score_gates(review)

    assert result.passed_gates == []
    assert result.weak_gates == []
    assert result.not_applicable_gates == []
    assert gate_statuses(review.valid_rows) == {}


def test_conditional_required_status_is_stable_across_outcomes() -> None:
    satisfied = evaluate_hard_gate_policy(
        _review(_row("tail-risk / p0 failure mode gate")),
        HardGateContext(True, False),
        VALID_EVIDENCE,
    )[2]
    not_applicable = evaluate_hard_gate_policy(
        _review(_row("tail-risk / p0 failure mode gate")),
        HardGateContext(False, False),
        VALID_EVIDENCE,
    )[2]
    blocked = evaluate_hard_gate_policy(
        _review(_row("tail-risk / p0 failure mode gate", "partial")),
        HardGateContext(True, False),
        VALID_EVIDENCE,
    )[2]

    assert {
        satisfied.required_status,
        not_applicable.required_status,
        blocked.required_status,
    } == {"pass when applicable"}


def test_gate_specific_reasons_distinguish_status_missing_and_evidence() -> None:
    partial = evaluate_hard_gate_policy(
        _review(_row("rollback gate", "partial")),
        HardGateContext(False, False),
        VALID_EVIDENCE,
    )[-2]
    missing = evaluate_hard_gate_policy(
        _review(),
        HardGateContext(True, False),
        HardGateEvidence(True, True, False, True, True),
    )[2]
    no_evidence = evaluate_hard_gate_policy(
        _review(_row("owner signoff gate", evidence="TBD")),
        HardGateContext(False, False),
        VALID_EVIDENCE,
    )[-1]

    assert partial.reason == "Rollback gate requires `pass`; actual status is `partial`."
    assert missing.reason == (
        "Tail-risk / P0 failure mode gate requires `pass` for high-impact "
        "projects; the gate is missing. Required evidence is missing or "
        "invalid: p0_failure_mode_checklist.md."
    )
    assert no_evidence.reason == (
        "Owner signoff gate is declared `pass` but does not contain meaningful evidence."
    )
