"""Eval result ingestion for externally run candidate assistant evaluations."""

from __future__ import annotations

import csv
import re
from collections import Counter
from dataclasses import dataclass, replace
from datetime import date, datetime, timezone
from math import isfinite
from pathlib import Path

from openevalgate.local_paths import resolve_local_evidence_path
from openevalgate.provenance import RunIdentityInspection, RunIdentityStatus, inspect_run_identity
from openevalgate.routing import load_routing_policy, routing_expectations
from openevalgate.schema import (
    EXPECTED_ROUTES,
    WORKFLOW_ROUTES,
    ValidationIssue,
    load_eval_cases,
    validate_eval_cases,
)


REQUIRED_EVAL_RESULT_COLUMNS = [
    "run_id",
    "case_id",
    "candidate",
    "evaluator",
    "actual_route",
    "expected_route",
    "route_match",
    "passed",
    "score",
    "failure_category",
    "failure_reason",
    "observed_output_path",
    "reviewed_by",
    "reviewed_at",
    "notes",
]

OPTIONAL_EVAL_RESULT_COLUMNS = [
    "trial_id",
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
]

NONEMPTY_EVAL_RESULT_FIELDS = (
    "run_id",
    "case_id",
    "candidate",
    "evaluator",
    "actual_route",
    "expected_route",
    "route_match",
    "passed",
    "score",
    "reviewed_by",
    "reviewed_at",
)

_DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_AWARE_DATETIME_PATTERN = re.compile(
    r"^(?P<date>\d{4}-\d{2}-\d{2})T"
    r"\d{2}:\d{2}:\d{2}(?:\.\d+)?"
    r"(?:Z|[+-]\d{2}:\d{2})$"
)
_NAIVE_DATETIME_PATTERN = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?$"
)
_EvalResultRow = dict[str, str | None]


@dataclass(frozen=True)
class EvalResultsValidationResult:
    valid: bool
    issues: list[ValidationIssue]
    row_count: int


@dataclass(frozen=True)
class EvalResultsSummary:
    row_count: int
    latest_run_id: str | None
    candidates: list[str]
    pass_rate: float | None
    route_match_rate: float | None
    failed_case_ids: list[str]
    failure_categories: Counter[str]
    observed_output_paths: list[str]
    workflow_route_accuracy: float | None
    trajectory_pass_rate: float | None
    end_state_pass_rate: float | None
    prohibited_action_rate: float | None
    boundary_family_count: int
    complete_boundary_family_count: int
    contrast_family_reliability: float | None
    semantic_stability: float | None
    repeated_case_count: int
    repeated_run_reliability: float | None
    required_escalation_recall: float | None
    over_escalation_rate: float | None
    destination_accuracy: float | None
    context_preservation_rate: float | None
    fallback_success_rate: float | None
    resume_success_rate: float | None
    late_escalation_rate: float | None
    workflow_assignment_accuracy: float | None = None
    model_policy_compliance: float | None = None
    routing_policy_version_match_rate: float | None = None
    deterministic_path_compliance: float | None = None


@dataclass(frozen=True)
class SelectedEvalResultsSummary:
    row_count: int
    observed_case_ids: tuple[str, ...]
    case_trial_counts: tuple[tuple[str, int], ...]
    pass_rate: float | None
    route_match_rate: float | None
    prohibited_action_rate: float | None
    required_escalation_recall: float | None


@dataclass(frozen=True)
class BehavioralEvidence:
    state: str
    summary: EvalResultsSummary | None
    issues: list[ValidationIssue]


@dataclass(frozen=True)
class _ParsedReviewTimestamp:
    kind: str
    calendar_date: date
    utc_instant: datetime | None
    original_value: str


class _NaiveReviewTimestampError(ValueError):
    pass


def read_eval_results(path: str | Path) -> list[_EvalResultRow]:
    """Read eval result CSV rows."""

    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _cell(row: _EvalResultRow, field: str) -> str:
    value = row.get(field)
    return value.strip() if isinstance(value, str) else ""


def validate_eval_results(
    project_dir: str | Path,
    *,
    identity_inspection: RunIdentityInspection | None = None,
) -> EvalResultsValidationResult:
    """Validate optional eval_results.csv against eval cases and the result contract."""

    root = Path(project_dir)
    inspection = identity_inspection or inspect_run_identity(root)
    if inspection.status == RunIdentityStatus.INVALID or _has_unbound_results(inspection):
        issues = _provenance_issues(inspection)
        return EvalResultsValidationResult(False, issues, 0)
    results_path = _usable_results_path(inspection)
    if results_path is None or not results_path.is_file():
        return EvalResultsValidationResult(True, [], 0)

    issues: list[ValidationIssue] = []

    try:
        with results_path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            fieldnames = reader.fieldnames or []
            missing_headers = [column for column in REQUIRED_EVAL_RESULT_COLUMNS if column not in fieldnames]
            for header in missing_headers:
                issues.append(ValidationIssue(f"{results_path}:{header}", "Required eval result column is missing."))
            rows = list(reader)
    except (csv.Error, OSError, UnicodeError) as exc:
        return EvalResultsValidationResult(
            False,
            [
                ValidationIssue(
                    str(results_path),
                    f"Could not read eval results: {exc}",
                    source="eval_results",
                )
            ],
            0,
        )

    cases_by_id = _valid_case_map(root / "eval_cases.yaml")
    case_ids = set(cases_by_id or {})
    policy_path = root / "routing_policy.yaml"
    policy_workflows: dict[str, dict[str, object]] = {}
    policy_models: set[str] = set()
    if policy_path.is_file():
        try:
            _, policy_workflows, _ = routing_expectations(policy_path)
            policy_models = {
                str(model.get("id", "")).strip()
                for model in load_routing_policy(policy_path).get("models", [])
                if isinstance(model, dict) and str(model.get("id", "")).strip()
            }
        except Exception:  # noqa: BLE001 - routing policy validation reports the source error.
            policy_workflows = {}
            policy_models = set()
    first_identity_rows: dict[tuple[str, str, str, str], int] = {}
    for index, row in enumerate(rows, start=2):
        prefix = f"{results_path}:row[{index}]"
        for field in NONEMPTY_EVAL_RESULT_FIELDS:
            if not _cell(row, field):
                issues.append(
                    ValidationIssue(
                        f"{prefix}.{field}",
                        "Must be a non-empty value.",
                    )
                )

        reviewed_at = _cell(row, "reviewed_at")
        if reviewed_at:
            try:
                _parse_review_timestamp(reviewed_at)
            except _NaiveReviewTimestampError:
                issues.append(
                    ValidationIssue(
                        f"{prefix}.reviewed_at",
                        "Datetime values must include an explicit UTC offset or Z timezone designator.",
                    )
                )
            except ValueError:
                issues.append(
                    ValidationIssue(
                        f"{prefix}.reviewed_at",
                        "Must be an ISO 8601 date or an ISO 8601 datetime with an explicit timezone.",
                    )
                )

        run_id = _cell(row, "run_id")
        case_id = _cell(row, "case_id")
        candidate = _cell(row, "candidate")
        trial_id = _cell(row, "trial_id")
        if run_id and candidate and case_id:
            identity = (run_id, candidate, trial_id, case_id)
            first_row = first_identity_rows.get(identity)
            if first_row is None:
                first_identity_rows[identity] = index
            else:
                rendered_trial = trial_id or "<blank>"
                issues.append(
                    ValidationIssue(
                        f"{prefix}.case_id",
                        "Duplicate eval result identity "
                        f"(run_id={run_id}, candidate={candidate}, "
                        f"trial_id={rendered_trial}, case_id={case_id}); "
                        f"first declared on row {first_row}.",
                    )
                )

        if case_id and case_ids and case_id not in case_ids:
            issues.append(ValidationIssue(f"{prefix}.case_id", f"Unknown eval case id: {case_id}."))

        for route_field in ("actual_route", "expected_route"):
            route = _cell(row, route_field)
            if route not in EXPECTED_ROUTES:
                issues.append(ValidationIssue(f"{prefix}.{route_field}", "Must be one of: block, escalate, revise, show."))

        for bool_field in ("route_match", "passed"):
            value = _cell(row, bool_field).lower()
            if value not in {"true", "false"}:
                issues.append(ValidationIssue(f"{prefix}.{bool_field}", "Must be true or false."))

        case = cases_by_id.get(case_id) if cases_by_id is not None else None
        case_expected_route = (
            str(case.get("expected_route", "")).strip()
            if case is not None
            else ""
        )
        result_expected_route = _cell(row, "expected_route")
        actual_route = _cell(row, "actual_route")
        declared_route_match = _cell(row, "route_match").lower()
        if (
            case is not None
            and case_expected_route in EXPECTED_ROUTES
            and result_expected_route in EXPECTED_ROUTES
            and result_expected_route != case_expected_route
        ):
            issues.append(
                ValidationIssue(
                    f"{prefix}.expected_route",
                    f"Does not match eval case expected_route: {case_expected_route}.",
                )
            )
        if (
            case is not None
            and case_expected_route in EXPECTED_ROUTES
            and actual_route in EXPECTED_ROUTES
            and declared_route_match in {"true", "false"}
            and (declared_route_match == "true")
            != (actual_route == case_expected_route)
        ):
            issues.append(
                ValidationIssue(
                    f"{prefix}.route_match",
                    "Does not match the value derived from actual_route and the referenced eval case.",
                )
            )

        score = _cell(row, "score")
        try:
            numeric_score = float(score)
        except ValueError:
            issues.append(ValidationIssue(f"{prefix}.score", "Must be numeric from 0 to 1."))
        else:
            if not isfinite(numeric_score) or not 0 <= numeric_score <= 1:
                issues.append(ValidationIssue(f"{prefix}.score", "Must be numeric from 0 to 1."))

        workflow_route = _cell(row, "actual_workflow_route")
        if workflow_route and workflow_route not in WORKFLOW_ROUTES:
            issues.append(
                ValidationIssue(
                    f"{prefix}.actual_workflow_route",
                    f"Must be one of: {', '.join(sorted(WORKFLOW_ROUTES))}.",
                )
            )

        for bool_field in (
            "workflow_route_match",
            "trajectory_pass",
            "end_state_pass",
            "prohibited_action_occurred",
            "destination_match",
            "payload_complete",
            "fallback_success",
            "resume_success",
            "late_escalation",
        ):
            if bool_field not in fieldnames:
                continue
            value = _cell(row, bool_field).lower()
            if value and value not in {"true", "false"}:
                issues.append(ValidationIssue(f"{prefix}.{bool_field}", "Must be true, false, or blank."))

        if (
            "destination_match" in fieldnames
            and _cell(row, "destination_match").lower() == "true"
            and not _cell(row, "actual_destination")
        ):
            issues.append(
                ValidationIssue(
                    f"{prefix}.actual_destination",
                    "Must be provided when destination_match is true.",
                )
            )

        actual_workflow_id = _cell(row, "actual_workflow_id")
        if actual_workflow_id and policy_workflows and actual_workflow_id not in policy_workflows:
            issues.append(
                ValidationIssue(
                    f"{prefix}.actual_workflow_id",
                    f"Unknown routing workflow id: {actual_workflow_id}.",
                )
            )
        actual_model_id = _cell(row, "actual_model_id")
        if actual_model_id and policy_models and actual_model_id not in policy_models:
            issues.append(
                ValidationIssue(
                    f"{prefix}.actual_model_id",
                    f"Unknown routing model id: {actual_model_id}.",
                )
            )

        output_path = _cell(row, "observed_output_path")
        if output_path:
            output_issue = _validate_output_reference(
                results_path.parent,
                output_path,
                allowed_root=_output_allowed_root(root, inspection),
            )
            if output_issue:
                issues.append(
                    ValidationIssue(
                        f"{prefix}.observed_output_path",
                        output_issue,
                    )
                )

    issues = [replace(issue, source="eval_results") for issue in issues]
    return EvalResultsValidationResult(not issues, issues, len(rows))


def classify_behavioral_evidence(
    project_dir: str | Path,
    *,
    identity_inspection: RunIdentityInspection | None = None,
) -> BehavioralEvidence:
    """Classify eval results before any behavioral metrics are summarized."""

    root = Path(project_dir)
    inspection = identity_inspection or inspect_run_identity(root)
    if inspection.status == RunIdentityStatus.INVALID or _has_unbound_results(inspection):
        return BehavioralEvidence("invalid", None, _provenance_issues(inspection))
    path = _usable_results_path(inspection)
    if path is None or not path.is_file():
        return BehavioralEvidence("not_provided", None, [])

    validation = validate_eval_results(root, identity_inspection=inspection)
    if not validation.valid:
        return BehavioralEvidence("invalid", None, validation.issues)
    if validation.row_count == 0:
        return BehavioralEvidence("empty", None, [])

    try:
        summary = summarize_eval_results(root, identity_inspection=inspection)
    except (csv.Error, OSError, UnicodeError, ValueError) as exc:
        return BehavioralEvidence(
            "invalid",
            None,
            [
                ValidationIssue(
                    str(path),
                    f"Could not summarize eval results: {exc}",
                    source="eval_results",
                )
            ],
        )
    return BehavioralEvidence("available", summary, [])


def summarize_eval_results(
    project_dir: str | Path,
    *,
    identity_inspection: RunIdentityInspection | None = None,
) -> EvalResultsSummary | None:
    """Summarize optional eval_results.csv for launch reports."""

    root = Path(project_dir)
    inspection = identity_inspection or inspect_run_identity(root)
    if inspection.status == RunIdentityStatus.INVALID or _has_unbound_results(inspection):
        raise ValueError("Cannot summarize invalid eval results.")
    path = _usable_results_path(inspection)
    if path is None or not path.is_file():
        return None

    validation = validate_eval_results(root, identity_inspection=inspection)
    if not validation.valid:
        raise ValueError("Cannot summarize invalid eval results.")
    cases_by_id = _valid_case_map(root / "eval_cases.yaml")
    if cases_by_id is None:
        raise ValueError("Cannot summarize eval results without valid eval cases.")

    rows = read_eval_results(path)
    if not rows:
        return EvalResultsSummary(
            0,
            None,
            [],
            None,
            None,
            [],
            Counter(),
            [],
            None,
            None,
            None,
            None,
            0,
            0,
            None,
            None,
            0,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        )

    cases = list(cases_by_id.values())
    candidates = sorted({_cell(row, "candidate") for row in rows if _cell(row, "candidate")})
    failed_case_ids = sorted({
        _cell(row, "case_id")
        for row in rows
        if _cell(row, "passed").lower() == "false" and _cell(row, "case_id")
    })
    failure_categories = Counter(
        _cell(row, "failure_category")
        for row in rows
        if _cell(row, "failure_category")
    )
    observed_output_paths = [
        _cell(row, "observed_output_path")
        for row in rows
        if _cell(row, "observed_output_path")
    ]

    passed_values = [_cell(row, "passed").lower() for row in rows]
    boundary_metrics = _boundary_metrics(cases, rows)
    escalation_metrics = _escalation_metrics(cases, rows)
    routing_metrics = _routing_metrics(root, rows)

    return EvalResultsSummary(
        row_count=len(rows),
        latest_run_id=_latest_run_id(rows),
        candidates=candidates,
        pass_rate=_true_rate(passed_values),
        route_match_rate=_derived_route_match_rate(rows, cases_by_id),
        failed_case_ids=failed_case_ids,
        failure_categories=failure_categories,
        observed_output_paths=observed_output_paths,
        workflow_route_accuracy=_optional_true_rate(rows, "workflow_route_match"),
        trajectory_pass_rate=_optional_true_rate(rows, "trajectory_pass"),
        end_state_pass_rate=_optional_true_rate(rows, "end_state_pass"),
        prohibited_action_rate=_optional_true_rate(rows, "prohibited_action_occurred"),
        boundary_family_count=boundary_metrics["family_count"],
        complete_boundary_family_count=boundary_metrics["complete_family_count"],
        contrast_family_reliability=boundary_metrics["contrast_family_reliability"],
        semantic_stability=boundary_metrics["semantic_stability"],
        repeated_case_count=boundary_metrics["repeated_case_count"],
        repeated_run_reliability=boundary_metrics["repeated_run_reliability"],
        required_escalation_recall=escalation_metrics["required_escalation_recall"],
        over_escalation_rate=escalation_metrics["over_escalation_rate"],
        destination_accuracy=_handoff_true_rate(cases, rows, "destination_match"),
        context_preservation_rate=_handoff_true_rate(cases, rows, "payload_complete"),
        fallback_success_rate=_handoff_true_rate(cases, rows, "fallback_success"),
        resume_success_rate=_handoff_true_rate(cases, rows, "resume_success"),
        late_escalation_rate=_handoff_true_rate(cases, rows, "late_escalation"),
        workflow_assignment_accuracy=routing_metrics["workflow_assignment_accuracy"],
        model_policy_compliance=routing_metrics["model_policy_compliance"],
        routing_policy_version_match_rate=routing_metrics["routing_policy_version_match_rate"],
        deterministic_path_compliance=routing_metrics["deterministic_path_compliance"],
    )


def summarize_selected_eval_results(
    project_dir: str | Path,
    *,
    run_id: str,
    candidate: str,
    identity_inspection: RunIdentityInspection | None = None,
) -> SelectedEvalResultsSummary:
    """Summarize only rows matching the selected run and candidate."""

    root = Path(project_dir)
    inspection = identity_inspection or inspect_run_identity(root)
    if inspection.status == RunIdentityStatus.INVALID or _has_unbound_results(inspection):
        raise ValueError("Cannot summarize invalid eval results.")
    path = _usable_results_path(inspection)
    if path is not None and path.is_file():
        validation = validate_eval_results(root, identity_inspection=inspection)
        if not validation.valid:
            raise ValueError("Cannot summarize invalid eval results.")
    cases_by_id = _valid_case_map(root / "eval_cases.yaml")
    if cases_by_id is None:
        raise ValueError("Cannot summarize eval results without valid eval cases.")
    rows = (
        [
            row
            for row in read_eval_results(path)
            if _cell(row, "run_id") == run_id.strip()
            and _cell(row, "candidate") == candidate.strip()
        ]
        if path is not None and path.is_file()
        else []
    )
    case_counts = Counter(
        _cell(row, "case_id")
        for row in rows
        if _cell(row, "case_id")
    )
    cases = list(cases_by_id.values())
    escalation_case_ids = {
        str(case.get("id", "")).strip()
        for case in cases
        if case.get("expected_route") == "escalate"
    }
    escalation_rows = [
        row for row in rows if _cell(row, "case_id") in escalation_case_ids
    ]
    return SelectedEvalResultsSummary(
        row_count=len(rows),
        observed_case_ids=tuple(sorted(case_counts)),
        case_trial_counts=tuple(sorted(case_counts.items())),
        pass_rate=_optional_true_rate(rows, "passed"),
        route_match_rate=_derived_route_match_rate(rows, cases_by_id),
        prohibited_action_rate=_optional_true_rate(rows, "prohibited_action_occurred"),
        required_escalation_recall=(
            _bool_rate([_row_escalated(row) for row in escalation_rows])
            if escalation_rows
            else None
        ),
    )


def _valid_case_map(path: Path) -> dict[str, dict[str, object]] | None:
    if not path.is_file() or not validate_eval_cases(path).valid:
        return None
    return {
        str(case.get("id", "")).strip(): case
        for case in load_eval_cases(path)
        if isinstance(case, dict) and str(case.get("id", "")).strip()
    }


def _parse_review_timestamp(value: str) -> _ParsedReviewTimestamp:
    if _DATE_PATTERN.fullmatch(value):
        parsed_date = date.fromisoformat(value)
        return _ParsedReviewTimestamp("date", parsed_date, None, value)

    if _NAIVE_DATETIME_PATTERN.fullmatch(value):
        try:
            datetime.fromisoformat(value)
        except ValueError:
            pass
        else:
            raise _NaiveReviewTimestampError(value)

    match = _AWARE_DATETIME_PATTERN.fullmatch(value)
    if not match:
        raise ValueError(value)

    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    parsed_datetime = datetime.fromisoformat(normalized)
    if parsed_datetime.tzinfo is None:
        raise ValueError(value)
    return _ParsedReviewTimestamp(
        "datetime",
        date.fromisoformat(match.group("date")),
        parsed_datetime.astimezone(timezone.utc),
        value,
    )


def _usable_results_path(inspection: RunIdentityInspection) -> Path | None:
    if inspection.status != RunIdentityStatus.COMPLETE:
        return None
    return inspection.results_path


def _has_unbound_results(inspection: RunIdentityInspection) -> bool:
    return any(finding.id == "provenance_results_unbound" for finding in inspection.findings)


def _output_allowed_root(root: Path, inspection: RunIdentityInspection) -> Path:
    if inspection.status == RunIdentityStatus.COMPLETE and inspection.identity is not None:
        return inspection.identity.evidence_root
    return root


def _provenance_issues(inspection: RunIdentityInspection) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for finding in inspection.findings:
        issues.append(ValidationIssue(finding.path, finding.message, source="provenance"))
        if (
            finding.id == "provenance_local_file_missing"
            and finding.path.endswith(".observed_output_path")
        ):
            issues.append(
                ValidationIssue(
                    finding.path,
                    "Referenced output file does not exist or is not a regular file.",
                    source="eval_results",
                )
            )
    return issues


def _validate_output_reference(
    base_dir: Path,
    value: str,
    *,
    allowed_root: Path,
) -> str | None:
    result = resolve_local_evidence_path(
        base_dir,
        value,
        allowed_root=allowed_root,
        require_file=True,
    )
    if result.error is None:
        return None
    if result.error == "traversal":
        return "Parent-directory traversal is not allowed."
    if result.error == "escape":
        return "Resolved path must remain inside the project directory."
    if result.error in {"missing", "symlink"}:
        return "Referenced output file does not exist or is not a regular file."
    return "Must be a project-relative filesystem path."


def _latest_run_id(rows: list[_EvalResultRow]) -> str | None:
    """Select the newest reviewed run, breaking timestamp ties by run ID."""

    latest_by_run: dict[str, tuple[date, int, datetime]] = {}
    for row in rows:
        run_id = _cell(row, "run_id")
        reviewed_at = _cell(row, "reviewed_at")
        if not run_id or not reviewed_at:
            continue
        parsed = _parse_review_timestamp(reviewed_at)
        comparison_key = (
            parsed.calendar_date,
            1 if parsed.kind == "datetime" else 0,
            parsed.utc_instant or datetime.min.replace(tzinfo=timezone.utc),
        )
        previous = latest_by_run.get(run_id)
        if previous is None or comparison_key > previous:
            latest_by_run[run_id] = comparison_key

    if not latest_by_run:
        return None
    # Lexically greatest run_id is the deliberate deterministic final tie-break.
    return max(latest_by_run, key=lambda run_id: (latest_by_run[run_id], run_id))


def _true_rate(values: list[str]) -> float | None:
    normalized = [value for value in values if value in {"true", "false"}]
    if not normalized:
        return None
    return sum(1 for value in normalized if value == "true") / len(normalized)


def _derived_route_match_rate(
    rows: list[_EvalResultRow],
    cases_by_id: dict[str, dict[str, object]],
) -> float | None:
    matches = [
        _cell(row, "actual_route")
        == str(cases_by_id[_cell(row, "case_id")].get("expected_route", "")).strip()
        for row in rows
        if _cell(row, "case_id") in cases_by_id
    ]
    return _bool_rate(matches)


def _optional_true_rate(rows: list[_EvalResultRow], field: str) -> float | None:
    return _true_rate([_cell(row, field).lower() for row in rows])


def _boundary_metrics(cases: list[dict[str, object]], rows: list[_EvalResultRow]) -> dict[str, object]:
    boundary_cases = {
        str(case.get("id", "")): case
        for case in cases
        if isinstance(case.get("boundary"), dict) and str(case.get("id", "")).strip()
    }
    families: dict[str, set[str]] = {}
    for case_id, case in boundary_cases.items():
        boundary = case["boundary"]
        assert isinstance(boundary, dict)
        family_id = str(boundary.get("family_id", "")).strip()
        if family_id:
            families.setdefault(family_id, set()).add(case_id)

    result_case_ids = {_cell(row, "case_id") for row in rows}
    complete_families = {
        family_id: members
        for family_id, members in families.items()
        if members and members.issubset(result_case_ids)
    }
    passing_families = 0
    for members in complete_families.values():
        family_rows = [row for row in rows if _cell(row, "case_id") in members]
        if family_rows and all(_cell(row, "passed").lower() == "true" for row in family_rows):
            passing_families += 1

    semantic_comparisons: list[bool] = []
    grouped_rows: dict[tuple[str, str, str], dict[str, _EvalResultRow]] = {}
    for row in rows:
        key = (
            _cell(row, "run_id"),
            _cell(row, "candidate"),
            _cell(row, "trial_id"),
        )
        grouped_rows.setdefault(key, {})[_cell(row, "case_id")] = row
    for case_id, case in boundary_cases.items():
        boundary = case["boundary"]
        assert isinstance(boundary, dict)
        if boundary.get("variation_type") != "semantic_invariance":
            continue
        anchor_case_id = str(boundary.get("anchor_case_id", "")).strip()
        for grouped in grouped_rows.values():
            variant_row = grouped.get(case_id)
            anchor_row = grouped.get(anchor_case_id)
            if not variant_row or not anchor_row:
                continue
            variant_route = _cell(variant_row, "actual_workflow_route")
            anchor_route = _cell(anchor_row, "actual_workflow_route")
            if variant_route and anchor_route:
                semantic_comparisons.append(variant_route == anchor_route)

    rows_by_case_run: dict[tuple[str, str, str], list[_EvalResultRow]] = {}
    for row in rows:
        case_id = _cell(row, "case_id")
        if case_id:
            key = (
                case_id,
                _cell(row, "run_id"),
                _cell(row, "candidate"),
            )
            rows_by_case_run.setdefault(key, []).append(row)
    repeated_cases = {
        key: case_rows
        for key, case_rows in rows_by_case_run.items()
        if len({_cell(row, "trial_id") for row in case_rows if _cell(row, "trial_id")}) >= 2
    }
    reliable_repeated_cases = sum(
        1
        for case_rows in repeated_cases.values()
        if all(_cell(row, "passed").lower() == "true" for row in case_rows)
    )

    return {
        "family_count": len(families),
        "complete_family_count": len(complete_families),
        "contrast_family_reliability": (
            passing_families / len(complete_families) if complete_families else None
        ),
        "semantic_stability": (
            sum(semantic_comparisons) / len(semantic_comparisons) if semantic_comparisons else None
        ),
        "repeated_case_count": len(repeated_cases),
        "repeated_run_reliability": (
            reliable_repeated_cases / len(repeated_cases) if repeated_cases else None
        ),
    }


def _escalation_metrics(
    cases: list[dict[str, object]],
    rows: list[_EvalResultRow],
) -> dict[str, float | None]:
    cases_by_id = {
        str(case.get("id", "")).strip(): case
        for case in cases
        if str(case.get("id", "")).strip()
    }
    required_rows: list[_EvalResultRow] = []
    routine_rows: list[_EvalResultRow] = []

    for row in rows:
        case = cases_by_id.get(_cell(row, "case_id"))
        if case is None:
            continue
        expected_workflow_route = str(case.get("expected_workflow_route", "")).strip()
        if expected_workflow_route:
            requires_handoff = expected_workflow_route in {"approval", "escalate"}
        else:
            requires_handoff = (
                isinstance(case.get("expected_handoff"), dict)
                or str(case.get("expected_route", "")).strip() == "escalate"
            )
        if requires_handoff:
            required_rows.append(row)
        else:
            routine_rows.append(row)

    required_successes = sum(1 for row in required_rows if _row_escalated(row))
    over_escalations = sum(1 for row in routine_rows if _row_escalated(row))
    return {
        "required_escalation_recall": (
            required_successes / len(required_rows) if required_rows else None
        ),
        "over_escalation_rate": (
            over_escalations / len(routine_rows) if routine_rows else None
        ),
    }


def _row_escalated(row: _EvalResultRow) -> bool:
    workflow_route = _cell(row, "actual_workflow_route")
    if workflow_route:
        return workflow_route in {"approval", "escalate"}
    return _cell(row, "actual_route") == "escalate"


def _handoff_true_rate(
    cases: list[dict[str, object]],
    rows: list[_EvalResultRow],
    field: str,
) -> float | None:
    handoff_case_ids = {
        str(case.get("id", "")).strip()
        for case in cases
        if isinstance(case.get("expected_handoff"), dict)
    }
    return _true_rate(
        [
            _cell(row, field).lower()
            for row in rows
            if _cell(row, "case_id") in handoff_case_ids
        ]
    )


def _routing_metrics(
    project_dir: Path,
    rows: list[_EvalResultRow],
) -> dict[str, float | None]:
    policy_path = project_dir / "routing_policy.yaml"
    if not policy_path.is_file():
        return {
            "workflow_assignment_accuracy": None,
            "model_policy_compliance": None,
            "routing_policy_version_match_rate": None,
            "deterministic_path_compliance": None,
        }
    try:
        version, workflows, case_workflows = routing_expectations(policy_path)
    except Exception:  # noqa: BLE001 - invalid policies are reported by project validation.
        return {
            "workflow_assignment_accuracy": None,
            "model_policy_compliance": None,
            "routing_policy_version_match_rate": None,
            "deterministic_path_compliance": None,
        }

    assignment_matches: list[bool] = []
    model_compliance: list[bool] = []
    version_matches: list[bool] = []
    deterministic_compliance: list[bool] = []

    for row in rows:
        case_id = _cell(row, "case_id")
        expected_workflow_id = case_workflows.get(case_id)
        if not expected_workflow_id:
            continue
        workflow = workflows.get(expected_workflow_id, {})
        actual_workflow_id = _cell(row, "actual_workflow_id")
        if "actual_workflow_id" in row:
            assignment_matches.append(actual_workflow_id == expected_workflow_id)

        assignment = workflow.get("model_assignment", {})
        if not isinstance(assignment, dict):
            continue
        mode = assignment.get("mode")
        actual_model_id = _cell(row, "actual_model_id")
        if "actual_model_id" in row:
            if mode == "none":
                model_compliance.append(not actual_model_id)
            else:
                approved = {
                    str(model_id).strip()
                    for model_id in assignment.get("approved_models", [])
                    if isinstance(model_id, str) and model_id.strip()
                }
                model_compliance.append(bool(actual_model_id) and actual_model_id in approved)

        observed_version = _cell(row, "routing_policy_version")
        if "routing_policy_version" in row and version:
            version_matches.append(bool(observed_version) and observed_version == version)

        if workflow.get("kind") in {"deterministic", "human"} and "actual_model_id" in row:
            deterministic_compliance.append(
                actual_workflow_id == expected_workflow_id and not actual_model_id
            )

    return {
        "workflow_assignment_accuracy": _bool_rate(assignment_matches),
        "model_policy_compliance": _bool_rate(model_compliance),
        "routing_policy_version_match_rate": _bool_rate(version_matches),
        "deterministic_path_compliance": _bool_rate(deterministic_compliance),
    }


def _bool_rate(values: list[bool]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)
