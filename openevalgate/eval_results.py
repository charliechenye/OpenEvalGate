"""Eval result ingestion for externally run candidate assistant evaluations."""

from __future__ import annotations

import csv
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from openevalgate.schema import EXPECTED_ROUTES, ValidationIssue, load_eval_cases


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


def read_eval_results(path: str | Path) -> list[dict[str, str]]:
    """Read eval result CSV rows."""

    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def validate_eval_results(project_dir: str | Path) -> EvalResultsValidationResult:
    """Validate optional eval_results.csv against eval cases and the result contract."""

    root = Path(project_dir)
    results_path = root / "eval_results.csv"
    if not results_path.is_file():
        return EvalResultsValidationResult(True, [], 0)

    issues: list[ValidationIssue] = []

    with results_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames or []
        missing_headers = [column for column in REQUIRED_EVAL_RESULT_COLUMNS if column not in fieldnames]
        for header in missing_headers:
            issues.append(ValidationIssue(f"{results_path}:{header}", "Required eval result column is missing."))
        rows = list(reader)

    case_ids = _case_ids(root / "eval_cases.yaml")
    for index, row in enumerate(rows, start=2):
        prefix = f"{results_path}:row[{index}]"
        case_id = row.get("case_id", "").strip()
        if case_id and case_ids and case_id not in case_ids:
            issues.append(ValidationIssue(f"{prefix}.case_id", f"Unknown eval case id: {case_id}."))

        for route_field in ("actual_route", "expected_route"):
            route = row.get(route_field, "").strip()
            if route not in EXPECTED_ROUTES:
                issues.append(ValidationIssue(f"{prefix}.{route_field}", "Must be one of: block, escalate, revise, show."))

        for bool_field in ("route_match", "passed"):
            value = row.get(bool_field, "").strip().lower()
            if value not in {"true", "false"}:
                issues.append(ValidationIssue(f"{prefix}.{bool_field}", "Must be true or false."))

        score = row.get("score", "").strip()
        try:
            numeric_score = float(score)
        except ValueError:
            issues.append(ValidationIssue(f"{prefix}.score", "Must be numeric from 0 to 1."))
        else:
            if numeric_score < 0 or numeric_score > 1:
                issues.append(ValidationIssue(f"{prefix}.score", "Must be numeric from 0 to 1."))

    return EvalResultsValidationResult(not issues, issues, len(rows))


def summarize_eval_results(project_dir: str | Path) -> EvalResultsSummary | None:
    """Summarize optional eval_results.csv for launch reports."""

    path = Path(project_dir) / "eval_results.csv"
    if not path.is_file():
        return None

    rows = read_eval_results(path)
    if not rows:
        return EvalResultsSummary(0, None, [], None, None, [], Counter(), [])

    candidates = sorted({row.get("candidate", "").strip() for row in rows if row.get("candidate", "").strip()})
    failed_case_ids = sorted({row.get("case_id", "").strip() for row in rows if row.get("passed", "").strip().lower() == "false" and row.get("case_id", "").strip()})
    failure_categories = Counter(
        row.get("failure_category", "").strip()
        for row in rows
        if row.get("failure_category", "").strip()
    )
    observed_output_paths = [
        row.get("observed_output_path", "").strip()
        for row in rows
        if row.get("observed_output_path", "").strip()
    ]

    passed_values = [row.get("passed", "").strip().lower() for row in rows]
    route_values = [row.get("route_match", "").strip().lower() for row in rows]

    return EvalResultsSummary(
        row_count=len(rows),
        latest_run_id=_latest_run_id(rows),
        candidates=candidates,
        pass_rate=_true_rate(passed_values),
        route_match_rate=_true_rate(route_values),
        failed_case_ids=failed_case_ids,
        failure_categories=failure_categories,
        observed_output_paths=observed_output_paths,
    )


def _case_ids(path: Path) -> set[str]:
    if not path.is_file():
        return set()
    return {str(case.get("id", "")).strip() for case in load_eval_cases(path) if str(case.get("id", "")).strip()}


def _latest_run_id(rows: list[dict[str, str]]) -> str | None:
    run_ids = [row.get("run_id", "").strip() for row in rows if row.get("run_id", "").strip()]
    return run_ids[-1] if run_ids else None


def _true_rate(values: list[str]) -> float | None:
    normalized = [value for value in values if value in {"true", "false"}]
    if not normalized:
        return None
    return sum(1 for value in normalized if value == "true") / len(normalized)
