"""Golden eval case schema validation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import yaml


CASE_TYPES = {
    "historical_production",
    "synthetic_boundary",
    "fresh_drift_sample",
    "adversarial",
    "regression",
}

RISK_TIERS = {"low", "medium", "high", "prohibited"}
EXPECTED_ROUTES = {"show", "revise", "escalate", "block"}

REQUIRED_FIELDS = [
    "id",
    "assistant_type",
    "use_case",
    "case_type",
    "user_input",
    "user_context",
    "retrieved_context",
    "risk_tier",
    "expected_behavior",
    "unacceptable_behavior",
    "expected_tool_behavior",
    "expected_route",
    "grading_rubric",
    "production_frequency",
    "policy_reference",
    "owner",
    "last_reviewed",
]


@dataclass(frozen=True)
class ValidationIssue:
    """A schema or project validation issue."""

    path: str
    message: str


@dataclass(frozen=True)
class ValidationResult:
    """Validation result with issues and normalized case count."""

    valid: bool
    issues: list[ValidationIssue]
    case_count: int = 0


def load_eval_cases(path: str | Path) -> list[dict[str, Any]]:
    """Load eval cases from a supported YAML shape."""

    with Path(path).open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)

    if data is None:
        return []
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "eval_cases" in data:
        cases = data["eval_cases"]
        if isinstance(cases, list):
            return cases
        raise ValueError("eval_cases must be a list")
    if isinstance(data, dict):
        return [data]
    raise ValueError("YAML must be an eval case, a list, or an object with eval_cases")


def validate_eval_cases(path: str | Path) -> ValidationResult:
    """Validate a golden eval YAML file."""

    issues: list[ValidationIssue] = []
    try:
        cases = load_eval_cases(path)
    except Exception as exc:  # noqa: BLE001 - CLI should report parser errors cleanly.
        return ValidationResult(False, [ValidationIssue(str(path), str(exc))], 0)

    if not cases:
        issues.append(ValidationIssue(str(path), "No eval cases found."))
        return ValidationResult(False, issues, 0)

    for index, case in enumerate(cases):
        case_path = f"case[{index}]"
        if not isinstance(case, dict):
            issues.append(ValidationIssue(case_path, "Eval case must be an object."))
            continue
        issues.extend(_validate_case(case, case_path))

    return ValidationResult(not issues, issues, len(cases))


def _validate_case(case: dict[str, Any], case_path: str) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    for field in REQUIRED_FIELDS:
        if field not in case:
            issues.append(ValidationIssue(f"{case_path}.{field}", "Required field is missing."))

    if "case_type" in case and case["case_type"] not in CASE_TYPES:
        issues.append(
            ValidationIssue(
                f"{case_path}.case_type",
                f"Must be one of: {', '.join(sorted(CASE_TYPES))}.",
            )
        )

    if "risk_tier" in case and case["risk_tier"] not in RISK_TIERS:
        issues.append(
            ValidationIssue(
                f"{case_path}.risk_tier",
                f"Must be one of: {', '.join(sorted(RISK_TIERS))}.",
            )
        )

    if "expected_route" in case and case["expected_route"] not in EXPECTED_ROUTES:
        issues.append(
            ValidationIssue(
                f"{case_path}.expected_route",
                f"Must be one of: {', '.join(sorted(EXPECTED_ROUTES))}.",
            )
        )

    _require_type(case, "expected_behavior", list, issues, case_path)
    _require_type(case, "unacceptable_behavior", list, issues, case_path)
    _require_type(case, "user_context", dict, issues, case_path)
    _require_type(case, "retrieved_context", dict, issues, case_path)
    _require_type(case, "expected_tool_behavior", dict, issues, case_path)
    _require_type(case, "grading_rubric", dict, issues, case_path)

    tool_behavior = case.get("expected_tool_behavior")
    if isinstance(tool_behavior, dict):
        for key in ("allowed_tools", "blocked_tools"):
            if key in tool_behavior and not isinstance(tool_behavior[key], list):
                issues.append(ValidationIssue(f"{case_path}.expected_tool_behavior.{key}", "Must be a list."))

    rubric = case.get("grading_rubric")
    if isinstance(rubric, dict):
        for name, value in rubric.items():
            if not isinstance(value, int) or not 1 <= value <= 5:
                issues.append(ValidationIssue(f"{case_path}.grading_rubric.{name}", "Must be an integer from 1 to 5."))

    if "last_reviewed" in case:
        reviewed = case["last_reviewed"]
        if isinstance(reviewed, date):
            pass
        elif isinstance(reviewed, str):
            try:
                date.fromisoformat(reviewed)
            except ValueError:
                issues.append(ValidationIssue(f"{case_path}.last_reviewed", "Must use YYYY-MM-DD format."))
        else:
            issues.append(ValidationIssue(f"{case_path}.last_reviewed", "Must use YYYY-MM-DD format."))

    return issues


def _require_type(
    case: dict[str, Any],
    field: str,
    expected_type: type,
    issues: list[ValidationIssue],
    case_path: str,
) -> None:
    if field in case and not isinstance(case[field], expected_type):
        issues.append(ValidationIssue(f"{case_path}.{field}", f"Must be a {expected_type.__name__}."))
