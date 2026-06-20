"""Structural inspection for the action-risk matrix."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from openevalgate.schema import ValidationIssue


REQUIRED_ACTION_RISK_COLUMNS = (
    "action",
    "risk_tier",
    "deterministic_gate",
    "human_review_required",
)


@dataclass(frozen=True)
class ActionRiskReview:
    present: bool
    valid: bool
    rows: list[dict[str, str]]
    issues: list[ValidationIssue]


def inspect_action_risk_matrix(path: str | Path) -> ActionRiskReview:
    """Read the action matrix once and validate policy-relevant columns."""

    matrix_path = Path(path)
    if not matrix_path.is_file():
        return ActionRiskReview(False, False, [], [])

    try:
        with matrix_path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            headers = reader.fieldnames or []
            missing = [
                column
                for column in REQUIRED_ACTION_RISK_COLUMNS
                if column not in headers
            ]
            issues = [
                ValidationIssue(
                    f"{matrix_path}:{column}",
                    "Required action-risk column is missing.",
                    source="action_risk_matrix",
                )
                for column in missing
            ]
            rows: list[dict[str, str]] = []
            for row_number, row in enumerate(reader, start=2):
                if None in row:
                    issues.append(
                        ValidationIssue(
                            f"{matrix_path}:{row_number}",
                            "Action-risk row contains more cells than the header.",
                            source="action_risk_matrix",
                        )
                    )
                normalized = {
                    key: (value or "").strip()
                    for key, value in row.items()
                    if key is not None
                }
                if not any(normalized.values()):
                    continue
                if not normalized.get("action"):
                    issues.append(
                        ValidationIssue(
                            f"{matrix_path}:{row_number}.action",
                            "Action must be nonblank for a populated row.",
                            source="action_risk_matrix",
                        )
                    )
                rows.append(normalized)
    except (OSError, csv.Error, UnicodeError) as exc:
        return ActionRiskReview(
            True,
            False,
            [],
            [
                ValidationIssue(
                    str(matrix_path),
                    f"Could not read action-risk matrix: {exc}",
                    source="action_risk_matrix",
                )
            ],
        )

    return ActionRiskReview(True, not issues, rows, issues)
