from __future__ import annotations

import csv
from dataclasses import replace
from pathlib import Path
from shutil import copytree

import pytest
import yaml

from openevalgate.eval_results import (
    classify_behavioral_evidence,
    summarize_selected_eval_results,
)
from openevalgate.report import generate_report
from openevalgate.review_policy import (
    evaluate_behavioral_sufficiency,
    validate_review_policy,
)
from openevalgate.schema import ReviewMode, is_critical_eval_case, validate_eval_cases


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "examples" / "customer_support_assistant"


def _project(tmp_path: Path) -> Path:
    target = tmp_path / "project"
    copytree(SOURCE, target)
    (target / "review_policy.yaml").unlink(missing_ok=True)
    return target


def _policy(**updates: object) -> dict[str, object]:
    policy: dict[str, object] = {
        "schema_version": "1",
        "requested_mode": "controlled_launch",
        "evaluation_scope": {"run_id": "run_002", "candidate": "gpt-4.1-mini"},
        "coverage": {
            "minimum_case_coverage": 0.3,
            "minimum_critical_case_coverage": 1.0,
            "minimum_trials_per_case": 1,
        },
        "thresholds": {
            "pass_rate": {"minimum": 0.3},
            "route_match_rate": {"minimum": 0.5},
        },
    }
    policy.update(updates)
    return policy


def _write_policy(project: Path, data: object) -> None:
    (project / "review_policy.yaml").write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def test_missing_policy_uses_exact_backward_compatible_state(tmp_path: Path) -> None:
    project = _project(tmp_path)
    result = validate_review_policy(project)
    assert (result.policy_present, result.policy_valid) == (False, True)
    assert result.declared_mode is None
    assert result.effective_mode == ReviewMode.SHADOW_LAUNCH
    sufficiency = evaluate_behavioral_sufficiency(project)
    assert not sufficiency.selected_scope_configured


def test_invalid_policy_cannot_configure_selected_scope(tmp_path: Path) -> None:
    project = _project(tmp_path)
    _write_policy(project, _policy(coverage=None))
    result = evaluate_behavioral_sufficiency(project)

    assert not result.policy_valid
    assert not result.selected_scope_configured
    assert not replace(
        result,
        selected_run_id="partially-parsed-run",
        selected_candidate="partially-parsed-candidate",
    ).selected_scope_configured


@pytest.mark.parametrize(
    "change",
    [
        {"schema_version": 1},
        {"schema_version": "2"},
        {"requested_mode": "unknown"},
        {"unknown": True},
        {"evaluation_scope": {"run_id": "", "candidate": "x"}},
        {"evaluation_scope": {"run_id": "x", "candidate": ""}},
        {"coverage": {"minimum_case_coverage": True, "minimum_critical_case_coverage": 1.0, "minimum_trials_per_case": 1}},
        {"coverage": {"minimum_case_coverage": 1.1, "minimum_critical_case_coverage": 1.0, "minimum_trials_per_case": 1}},
        {"coverage": {"minimum_case_coverage": 1.0, "minimum_critical_case_coverage": 0.9, "minimum_trials_per_case": 1}},
        {"thresholds": {"pass_rate": {"minimum": True}, "route_match_rate": {"minimum": 1.0}}},
        {"thresholds": {"pass_rate": {"maximum": 1.0}, "route_match_rate": {"minimum": 1.0}}},
        {"thresholds": {"other": {"minimum": 1.0}, "pass_rate": {"minimum": 1.0}, "route_match_rate": {"minimum": 1.0}}},
    ],
)
def test_invalid_present_policy_has_no_fallback(tmp_path: Path, change: dict[str, object]) -> None:
    project = _project(tmp_path)
    _write_policy(project, _policy(**change))
    result = validate_review_policy(project)
    assert result.policy_present and not result.policy_valid
    assert result.declared_mode is None and result.effective_mode is None


@pytest.mark.parametrize("mode", ["documentation", "shadow_launch", "controlled_launch"])
def test_valid_modes(tmp_path: Path, mode: str) -> None:
    project = _project(tmp_path)
    data = _policy(requested_mode=mode)
    if mode != "controlled_launch":
        data.pop("evaluation_scope")
        data.pop("coverage")
        data.pop("thresholds")
    _write_policy(project, data)
    assert validate_review_policy(project).policy_valid


def test_critical_field_and_inference(tmp_path: Path) -> None:
    project = _project(tmp_path)
    data = yaml.safe_load((project / "eval_cases.yaml").read_text(encoding="utf-8"))
    data["eval_cases"][0]["critical"] = "true"
    (project / "eval_cases.yaml").write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    assert not validate_eval_cases(project / "eval_cases.yaml").valid
    assert is_critical_eval_case({"critical": True, "risk_tier": "low", "expected_route": "show"})
    assert is_critical_eval_case({"critical": False, "risk_tier": "high", "expected_route": "show"})
    assert is_critical_eval_case({"critical": False, "risk_tier": "low", "expected_route": "block"})


def test_selected_scope_is_exact_and_empty_rates_stay_none(tmp_path: Path) -> None:
    project = _project(tmp_path)
    summary = summarize_selected_eval_results(project, run_id="run_002", candidate="gpt-4.1-mini")
    assert summary.row_count == 6
    assert summarize_selected_eval_results(project, run_id="other", candidate="gpt-4.1-mini").row_count == 0
    empty = summarize_selected_eval_results(project, run_id="run_002", candidate="other")
    assert empty.pass_rate is None and empty.route_match_rate is None


def test_controlled_scope_normalizes_result_identity_whitespace(
    tmp_path: Path,
) -> None:
    project = _project(tmp_path)
    _write_policy(project, _policy())
    results_path = project / "eval_results.csv"
    with results_path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        headers = list(reader.fieldnames or [])
        rows = list(reader)
    for row in rows:
        row["run_id"] = f"  {row['run_id']}  "
        row["candidate"] = f"  {row['candidate']}  "
    with results_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    result = evaluate_behavioral_sufficiency(project)

    assert result.selected_row_count == 6
    assert "refund_abuse_history_002" in result.failed_critical_case_ids
    assert "wrong_destination_fraud_012" in result.failed_critical_case_ids


def test_coverage_distinguishes_missing_from_below_depth(tmp_path: Path) -> None:
    project = _project(tmp_path)
    data = _policy()
    data["coverage"]["minimum_trials_per_case"] = 2  # type: ignore[index]
    _write_policy(project, data)
    result = evaluate_behavioral_sufficiency(project)
    assert result.missing_case_ids
    assert result.observed_cases_below_trial_depth
    assert not set(result.missing_case_ids) & set(result.observed_cases_below_trial_depth)


def test_thresholds_invariants_and_order_are_deterministic(tmp_path: Path) -> None:
    project = _project(tmp_path)
    _write_policy(project, _policy())
    first = evaluate_behavioral_sufficiency(project)
    second = evaluate_behavioral_sufficiency(project)
    assert first == second
    assert [item.metric for item in first.threshold_outcomes] == ["pass_rate", "route_match_rate"]
    assert [item.invariant_id for item in first.invariant_outcomes] == [
        "no_prohibited_actions", "all_critical_cases_pass", "required_escalations_pass"
    ]


def test_zero_matching_rows_fail_closed_without_zero_rates(tmp_path: Path) -> None:
    project = _project(tmp_path)
    _write_policy(project, _policy(evaluation_scope={"run_id": "missing", "candidate": "missing"}))
    result = evaluate_behavioral_sufficiency(project)
    assert result.selected_row_count == 0
    assert all(item.actual_value is None and item.status == "not_evaluated" for item in result.threshold_outcomes)
    assert not result.sufficient_for_requested_mode


def test_invalid_row_outside_selected_scope_invalidates_whole_file(
    tmp_path: Path,
) -> None:
    project = _project(tmp_path)
    _write_policy(project, _policy())
    results_path = project / "eval_results.csv"
    with results_path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        headers = list(reader.fieldnames or [])
        rows = list(reader)
    invalid_row = rows[0].copy()
    invalid_row["run_id"] = "other_run"
    invalid_row["candidate"] = "other_candidate"
    invalid_row["observed_output_path"] = ""
    invalid_row["route_match"] = "true"
    rows.append(invalid_row)
    with results_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    with pytest.raises(ValueError, match=r"^Cannot summarize invalid eval results\.$"):
        summarize_selected_eval_results(
            project,
            run_id="run_002",
            candidate="gpt-4.1-mini",
        )
    evidence = classify_behavioral_evidence(project)
    sufficiency = evaluate_behavioral_sufficiency(project)
    report = generate_report(project)

    assert evidence.state == "invalid"
    assert evidence.summary is None
    assert not sufficiency.sufficient_for_requested_mode
    assert "Unavailable due to invalid behavioral evidence" in report


@pytest.mark.parametrize(
    ("change", "expected_path", "expected_message"),
    [
        (
            {"coverage": None},
            "review_policy.coverage",
            "Required for controlled-launch review.",
        ),
        (
            {"thresholds": None},
            "review_policy.thresholds",
            "Required for controlled-launch review.",
        ),
        (
            {"thresholds": {"route_match_rate": {"minimum": 1.0}}},
            "review_policy.thresholds.pass_rate",
            "Required for controlled-launch review.",
        ),
        (
            {"thresholds": {"pass_rate": {"minimum": 1.0}}},
            "review_policy.thresholds.route_match_rate",
            "Required for controlled-launch review.",
        ),
        (
            {"evaluation_scope": {"run_id": "run", "candidate": "candidate", "extra": "x"}},
            "review_policy.evaluation_scope.extra",
            "Unknown field.",
        ),
        (
            {"coverage": {
                "minimum_case_coverage": 1.0,
                "minimum_critical_case_coverage": 1.0,
                "minimum_trials_per_case": 1,
                "extra": 1,
            }},
            "review_policy.coverage.extra",
            "Unknown field.",
        ),
        (
            {"coverage": {
                "minimum_case_coverage": 1.0,
                "minimum_critical_case_coverage": 1.0,
                "minimum_trials_per_case": 0,
            }},
            "review_policy.coverage.minimum_trials_per_case",
            "Must be an integer of at least 1.",
        ),
        (
            {"thresholds": {
                "pass_rate": "invalid",
                "route_match_rate": {"minimum": 1.0},
            }},
            "review_policy.thresholds.pass_rate",
            "Must be an object.",
        ),
        (
            {"coverage": {
                "minimum_case_coverage": 1.0,
                "minimum_critical_case_coverage": 0.9,
                "minimum_trials_per_case": 1,
            }},
            "review_policy.coverage.minimum_critical_case_coverage",
            "Controlled-launch review requires minimum_critical_case_coverage to be exactly 1.0.",
        ),
        (
            {"coverage": {
                "minimum_case_coverage": 1.0,
                "minimum_critical_case_coverage": 1.1,
                "minimum_trials_per_case": 1,
            }},
            "review_policy.coverage.minimum_critical_case_coverage",
            "Controlled-launch review requires minimum_critical_case_coverage to be exactly 1.0.",
        ),
    ],
)
def test_controlled_policy_validation_paths(
    tmp_path: Path,
    change: dict[str, object],
    expected_path: str,
    expected_message: str,
) -> None:
    project = _project(tmp_path)
    _write_policy(project, _policy(**change))

    issues = validate_review_policy(project).issues

    assert any(
        issue.path == expected_path and issue.message == expected_message
        for issue in issues
    )
