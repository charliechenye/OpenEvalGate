"""Review-policy parsing and deterministic behavioral-sufficiency evaluation."""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

import yaml

from openevalgate.eval_results import (
    classify_behavioral_evidence,
    summarize_selected_eval_results,
)
from openevalgate.schema import (
    ReviewMode,
    ValidationIssue,
    is_critical_eval_case,
    load_eval_cases,
    validate_eval_cases,
)


POLICY_KEYS = {"schema_version", "requested_mode", "evaluation_scope", "coverage", "thresholds"}
COVERAGE_KEYS = {
    "minimum_case_coverage",
    "minimum_critical_case_coverage",
    "minimum_trials_per_case",
}
THRESHOLD_METRICS = ("pass_rate", "route_match_rate")
OUTCOME_STATUSES = {"pass", "fail", "not_evaluated", "not_applicable"}


@dataclass(frozen=True)
class EvaluationScope:
    run_id: str
    candidate: str


@dataclass(frozen=True)
class CoveragePolicy:
    minimum_case_coverage: float
    minimum_critical_case_coverage: float
    minimum_trials_per_case: int


@dataclass(frozen=True)
class MetricThreshold:
    minimum: float


@dataclass(frozen=True)
class ReviewPolicy:
    schema_version: str
    requested_mode: ReviewMode
    evaluation_scope: EvaluationScope | None
    coverage: CoveragePolicy | None
    thresholds: tuple[tuple[str, MetricThreshold], ...]


@dataclass(frozen=True)
class ReviewPolicyResult:
    policy_present: bool
    policy_valid: bool
    declared_mode: ReviewMode | None
    effective_mode: ReviewMode | None
    source: str
    policy: ReviewPolicy | None
    issues: tuple[ValidationIssue, ...]


@dataclass(frozen=True)
class ThresholdOutcome:
    metric: str
    actual_value: float | None
    comparator: str
    configured_threshold: float
    status: str


@dataclass(frozen=True)
class InvariantOutcome:
    invariant_id: str
    status: str
    reason: str


@dataclass(frozen=True)
class BehavioralSufficiency:
    behavioral_evidence_state: str
    declared_mode: ReviewMode | None
    effective_mode: ReviewMode | None
    policy_present: bool
    policy_valid: bool
    selected_run_id: str | None
    selected_candidate: str | None
    selected_row_count: int
    expected_case_count: int
    observed_case_count: int
    case_coverage: float | None
    cases_meeting_trial_depth_count: int
    missing_case_ids: tuple[str, ...]
    observed_cases_below_trial_depth: tuple[str, ...]
    expected_critical_case_count: int
    observed_critical_case_count: int
    critical_case_coverage: float | None
    missing_critical_case_ids: tuple[str, ...]
    critical_cases_below_trial_depth: tuple[str, ...]
    failed_critical_case_ids: tuple[str, ...]
    coverage_sufficient: bool
    threshold_outcomes: tuple[ThresholdOutcome, ...]
    invariant_outcomes: tuple[InvariantOutcome, ...]
    thresholds_satisfied: bool
    behavioral_invariants_satisfied: bool
    sufficient_for_requested_mode: bool
    issues: tuple[ValidationIssue, ...]

    @property
    def selected_scope_configured(self) -> bool:
        """Whether a valid policy configures an exact run and candidate."""

        return (
            self.policy_valid
            and self.selected_run_id is not None
            and self.selected_candidate is not None
        )

    @property
    def sufficient_for_effective_mode(self) -> bool:
        """Whether prerequisites for the effective review mode are satisfied."""

        return self.sufficient_for_requested_mode


def load_review_policy(path: str | Path) -> Any:
    with Path(path).open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def validate_review_policy(project_dir: str | Path) -> ReviewPolicyResult:
    path = Path(project_dir) / "review_policy.yaml"
    if not path.is_file():
        return ReviewPolicyResult(
            False, True, None, ReviewMode.SHADOW_LAUNCH,
            "backward_compatible_default", None, (),
        )
    try:
        data = load_review_policy(path)
    except Exception as exc:  # noqa: BLE001
        return _invalid(path, [ValidationIssue(str(path), str(exc), "review_policy")])
    issues: list[ValidationIssue] = []
    if not isinstance(data, dict):
        return _invalid(path, [ValidationIssue(str(path), "Review policy must be an object.", "review_policy")])
    _unknown_keys(data, POLICY_KEYS, "review_policy", issues)
    version = data.get("schema_version")
    if version != "1" or not isinstance(version, str):
        issues.append(ValidationIssue("review_policy.schema_version", 'Must be exactly the string "1".', "review_policy"))
    mode_value = data.get("requested_mode")
    try:
        mode = ReviewMode(mode_value)
    except (ValueError, TypeError):
        mode = None
        issues.append(ValidationIssue("review_policy.requested_mode", "Must be one of: controlled_launch, documentation, shadow_launch.", "review_policy"))

    scope = _parse_scope(data.get("evaluation_scope"), mode, issues)
    coverage = _parse_coverage(data.get("coverage"), mode, issues)
    thresholds = _parse_thresholds(data.get("thresholds"), mode, issues)
    if issues or mode is None:
        return _invalid(path, issues)
    policy = ReviewPolicy("1", mode, scope, coverage, thresholds)
    return ReviewPolicyResult(True, True, mode, mode, "review_policy", policy, ())


def evaluate_behavioral_sufficiency(project_dir: str | Path) -> BehavioralSufficiency:
    root = Path(project_dir)
    policy_result = validate_review_policy(root)
    evidence = classify_behavioral_evidence(root)
    cases: list[dict[str, Any]] = []
    eval_path = root / "eval_cases.yaml"
    if eval_path.is_file() and validate_eval_cases(eval_path).valid:
        cases = load_eval_cases(eval_path)
    expected_ids = tuple(sorted({str(case["id"]).strip() for case in cases}))
    critical_ids = tuple(sorted(
        str(case["id"]).strip() for case in cases if is_critical_eval_case(case)
    ))
    scope = policy_result.policy.evaluation_scope if policy_result.policy else None
    coverage_policy = policy_result.policy.coverage if policy_result.policy else None
    selected = (
        summarize_selected_eval_results(
            root, run_id=scope.run_id, candidate=scope.candidate
        )
        if scope and evidence.state == "available"
        else None
    )
    counts = dict(selected.case_trial_counts) if selected else {}
    observed = tuple(sorted(set(expected_ids) & set(selected.observed_case_ids if selected else ())))
    missing = tuple(sorted(set(expected_ids) - set(observed)))
    minimum_trials = coverage_policy.minimum_trials_per_case if coverage_policy else 1
    below_depth = tuple(sorted(
        case_id for case_id in observed if counts.get(case_id, 0) < minimum_trials
    ))
    meeting_depth = sum(1 for case_id in observed if counts.get(case_id, 0) >= minimum_trials)
    observed_critical = tuple(sorted(set(critical_ids) & set(observed)))
    missing_critical = tuple(sorted(set(critical_ids) - set(observed_critical)))
    critical_below = tuple(sorted(
        case_id for case_id in observed_critical if counts.get(case_id, 0) < minimum_trials
    ))
    failed_critical = _failed_critical_ids(root, scope, critical_ids, evidence.state)
    case_coverage = len(observed) / len(expected_ids) if expected_ids else None
    critical_coverage = (
        len(observed_critical) / len(critical_ids) if critical_ids else None
    )
    coverage_sufficient = bool(
        coverage_policy
        and case_coverage is not None
        and case_coverage >= coverage_policy.minimum_case_coverage
        and not below_depth
        and not missing_critical
        and not critical_below
    )
    thresholds = _threshold_outcomes(policy_result.policy, selected)
    invariants = _invariant_outcomes(
        policy_result.effective_mode, selected, critical_ids, missing_critical,
        critical_below, failed_critical, cases,
    )
    thresholds_satisfied = all(item.status in {"pass", "not_applicable"} for item in thresholds)
    invariants_satisfied = all(item.status in {"pass", "not_applicable"} for item in invariants)
    mode = policy_result.effective_mode
    if mode == ReviewMode.CONTROLLED_LAUNCH:
        sufficient = bool(
            policy_result.policy_valid
            and evidence.state == "available"
            and selected
            and selected.row_count
            and coverage_sufficient
            and thresholds_satisfied
            and invariants_satisfied
        )
    elif mode == ReviewMode.SHADOW_LAUNCH:
        sufficient = policy_result.policy_valid and evidence.state != "invalid"
    elif mode == ReviewMode.DOCUMENTATION:
        sufficient = policy_result.policy_valid
    else:
        sufficient = False
    return BehavioralSufficiency(
        evidence.state, policy_result.declared_mode, mode,
        policy_result.policy_present, policy_result.policy_valid,
        scope.run_id if scope else None, scope.candidate if scope else None,
        selected.row_count if selected else 0,
        len(expected_ids), len(observed), case_coverage, meeting_depth, missing,
        below_depth, len(critical_ids), len(observed_critical), critical_coverage,
        missing_critical, critical_below, failed_critical, coverage_sufficient,
        thresholds, invariants, thresholds_satisfied, invariants_satisfied,
        sufficient, tuple(sorted(policy_result.issues, key=lambda item: (item.path, item.message))),
    )


def _invalid(path: Path, issues: list[ValidationIssue]) -> ReviewPolicyResult:
    normalized = tuple(sorted(
        (replace(issue, source="review_policy") for issue in issues),
        key=lambda item: (item.path, item.message),
    ))
    return ReviewPolicyResult(True, False, None, None, "invalid", None, normalized)


def _parse_scope(value: Any, mode: ReviewMode | None, issues: list[ValidationIssue]) -> EvaluationScope | None:
    if value is None:
        if mode == ReviewMode.CONTROLLED_LAUNCH:
            issues.append(ValidationIssue("review_policy.evaluation_scope", "Required for controlled-launch review.", "review_policy"))
        return None
    if not isinstance(value, dict):
        issues.append(ValidationIssue("review_policy.evaluation_scope", "Must be an object.", "review_policy"))
        return None
    _unknown_keys(value, {"run_id", "candidate"}, "review_policy.evaluation_scope", issues)
    valid = True
    for field in ("run_id", "candidate"):
        if not isinstance(value.get(field), str) or not value[field].strip():
            valid = False
            issues.append(ValidationIssue(f"review_policy.evaluation_scope.{field}", "Must be a non-empty string.", "review_policy"))
    return EvaluationScope(value["run_id"].strip(), value["candidate"].strip()) if valid else None


def _parse_coverage(value: Any, mode: ReviewMode | None, issues: list[ValidationIssue]) -> CoveragePolicy | None:
    if value is None:
        if mode == ReviewMode.CONTROLLED_LAUNCH:
            issues.append(ValidationIssue("review_policy.coverage", "Required for controlled-launch review.", "review_policy"))
        return None
    if not isinstance(value, dict):
        issues.append(ValidationIssue("review_policy.coverage", "Must be an object.", "review_policy"))
        return None
    _unknown_keys(value, COVERAGE_KEYS, "review_policy.coverage", issues)
    values: dict[str, float | int] = {}
    for field in ("minimum_case_coverage", "minimum_critical_case_coverage"):
        raw = value.get(field)
        if isinstance(raw, bool) or not isinstance(raw, (int, float)) or not 0 <= raw <= 1:
            issues.append(ValidationIssue(f"review_policy.coverage.{field}", "Must be numeric from 0 through 1.", "review_policy"))
        else:
            values[field] = float(raw)
    trials = value.get("minimum_trials_per_case")
    if isinstance(trials, bool) or not isinstance(trials, int) or trials < 1:
        issues.append(ValidationIssue("review_policy.coverage.minimum_trials_per_case", "Must be an integer of at least 1.", "review_policy"))
    else:
        values["minimum_trials_per_case"] = trials
    if mode == ReviewMode.CONTROLLED_LAUNCH and values.get("minimum_critical_case_coverage") != 1.0:
        issues.append(ValidationIssue(
            "review_policy.coverage.minimum_critical_case_coverage",
            "Controlled-launch review requires minimum_critical_case_coverage to be exactly 1.0.",
            "review_policy",
        ))
    return CoveragePolicy(
        float(values["minimum_case_coverage"]),
        float(values["minimum_critical_case_coverage"]),
        int(values["minimum_trials_per_case"]),
    ) if len(values) == 3 else None


def _parse_thresholds(value: Any, mode: ReviewMode | None, issues: list[ValidationIssue]) -> tuple[tuple[str, MetricThreshold], ...]:
    if value is None:
        if mode == ReviewMode.CONTROLLED_LAUNCH:
            issues.append(ValidationIssue("review_policy.thresholds", "Required for controlled-launch review.", "review_policy"))
        return ()
    if not isinstance(value, dict):
        issues.append(ValidationIssue("review_policy.thresholds", "Must be an object.", "review_policy"))
        return ()
    _unknown_keys(value, set(THRESHOLD_METRICS), "review_policy.thresholds", issues)
    outcomes: list[tuple[str, MetricThreshold]] = []
    for metric in THRESHOLD_METRICS:
        nested = value.get(metric)
        if nested is None:
            if mode == ReviewMode.CONTROLLED_LAUNCH:
                issues.append(ValidationIssue(f"review_policy.thresholds.{metric}", "Required for controlled-launch review.", "review_policy"))
            continue
        if not isinstance(nested, dict):
            issues.append(ValidationIssue(f"review_policy.thresholds.{metric}", "Must be an object.", "review_policy"))
            continue
        _unknown_keys(nested, {"minimum"}, f"review_policy.thresholds.{metric}", issues)
        raw = nested.get("minimum")
        if isinstance(raw, bool) or not isinstance(raw, (int, float)) or not 0 <= raw <= 1:
            issues.append(ValidationIssue(f"review_policy.thresholds.{metric}.minimum", "Must be numeric from 0 through 1.", "review_policy"))
        else:
            outcomes.append((metric, MetricThreshold(float(raw))))
    return tuple(outcomes)


def _unknown_keys(value: dict[str, Any], allowed: set[str], path: str, issues: list[ValidationIssue]) -> None:
    for key in sorted(set(value) - allowed):
        issues.append(ValidationIssue(f"{path}.{key}", "Unknown field.", "review_policy"))


def _threshold_outcomes(policy: ReviewPolicy | None, selected: Any) -> tuple[ThresholdOutcome, ...]:
    values = {
        "pass_rate": selected.pass_rate if selected else None,
        "route_match_rate": selected.route_match_rate if selected else None,
    }
    return tuple(
        ThresholdOutcome(
            metric, values[metric], "minimum", threshold.minimum,
            "not_evaluated" if values[metric] is None else (
                "pass" if values[metric] >= threshold.minimum else "fail"
            ),
        )
        for metric, threshold in (policy.thresholds if policy else ())
    )


def _invariant_outcomes(
    mode: ReviewMode | None,
    selected: Any,
    critical_ids: tuple[str, ...],
    missing_critical: tuple[str, ...],
    critical_below: tuple[str, ...],
    failed_critical: tuple[str, ...],
    cases: list[dict[str, Any]],
) -> tuple[InvariantOutcome, ...]:
    if selected and selected.prohibited_action_rate is not None:
        prohibited = InvariantOutcome(
            "no_prohibited_actions",
            "pass" if selected.prohibited_action_rate == 0 else "fail",
            "No prohibited actions occurred." if selected.prohibited_action_rate == 0 else "A prohibited action occurred.",
        )
    else:
        status = "not_evaluated" if mode == ReviewMode.CONTROLLED_LAUNCH else "not_applicable"
        prohibited = InvariantOutcome("no_prohibited_actions", status, "Prohibited-action evidence is unavailable.")
    if mode != ReviewMode.CONTROLLED_LAUNCH and not selected:
        critical = InvariantOutcome("all_critical_cases_pass", "not_applicable", "No selected controlled-launch scope is configured.")
    elif not critical_ids:
        critical = InvariantOutcome("all_critical_cases_pass", "not_applicable", "No critical eval cases are defined.")
    elif missing_critical or critical_below or failed_critical:
        critical = InvariantOutcome("all_critical_cases_pass", "fail", "Critical cases are missing, under depth, or failing.")
    else:
        critical = InvariantOutcome("all_critical_cases_pass", "pass", "Every critical case is covered at depth and passing.")
    escalation_ids = {
        str(case.get("id", "")).strip() for case in cases if case.get("expected_route") == "escalate"
    }
    if mode != ReviewMode.CONTROLLED_LAUNCH and not selected:
        escalation = InvariantOutcome("required_escalations_pass", "not_applicable", "No selected controlled-launch scope is configured.")
    elif not escalation_ids:
        escalation = InvariantOutcome("required_escalations_pass", "not_applicable", "No eval cases require escalation.")
    elif not selected or selected.required_escalation_recall is None:
        escalation = InvariantOutcome("required_escalations_pass", "not_evaluated", "Required-escalation evidence is unavailable.")
    else:
        passed = selected.required_escalation_recall == 1.0
        escalation = InvariantOutcome("required_escalations_pass", "pass" if passed else "fail", "All required escalations passed." if passed else "At least one required escalation failed.")
    return (prohibited, critical, escalation)


def _failed_critical_ids(
    root: Path,
    scope: EvaluationScope | None,
    critical_ids: tuple[str, ...],
    evidence_state: str,
) -> tuple[str, ...]:
    if not scope or evidence_state != "available":
        return ()
    from openevalgate.eval_results import _cell, read_eval_results
    return tuple(sorted({
        _cell(row, "case_id")
        for row in read_eval_results(root / "eval_results.csv")
        if _cell(row, "run_id") == scope.run_id.strip()
        and _cell(row, "candidate") == scope.candidate.strip()
        and _cell(row, "case_id") in critical_ids
        and _cell(row, "passed").lower() == "false"
    }))
