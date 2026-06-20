"""Structural inspection for the action-risk matrix."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from openevalgate.schema import ValidationIssue


ALLOWED_ACTION_RISK_TIERS = frozenset(
    {"low", "medium", "high", "prohibited"}
)
HIGH_IMPACT_ACTION_RISK_TIERS = frozenset({"high", "prohibited"})
ALLOWED_BOOLEAN_VALUES = frozenset({"true", "false"})

REQUIRED_ACTION_RISK_COLUMNS = (
    "action",
    "risk_tier",
    "deterministic_gate",
    "human_review_required",
)


@dataclass(frozen=True)
class ActionRiskRow:
    raw_values: dict[str, str]
    normalized_values: dict[str, str]
    source_line: int

    def get(self, key: str, default: str = "") -> str:
        return self.normalized_values.get(key, default)


@dataclass(frozen=True)
class ActionRiskReview:
    present: bool
    valid: bool
    rows: list[ActionRiskRow]
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
            rows: list[ActionRiskRow] = []
            for row_number, row in enumerate(reader, start=2):
                if None in row:
                    issues.append(
                        ValidationIssue(
                            f"{matrix_path}:{row_number}",
                            "Action-risk row contains more cells than the header.",
                            source="action_risk_matrix",
                        )
                    )
                raw_values = {
                    key: (value or "").strip()
                    for key, value in row.items()
                    if key is not None
                }
                if not any(raw_values.values()):
                    continue
                action = raw_values.get("action", "")
                raw_risk_tier = raw_values.get("risk_tier", "")
                normalized_risk_tier = raw_risk_tier.lower()
                raw_human_review = raw_values.get(
                    "human_review_required",
                    "",
                )
                normalized_human_review = raw_human_review.lower()
                if not action:
                    issues.append(
                        ValidationIssue(
                            f"{matrix_path}:{row_number}.action",
                            "Action must be nonblank for a populated row.",
                            source="action_risk_matrix",
                        )
                    )
                if not raw_risk_tier:
                    issues.append(
                        ValidationIssue(
                            f"{matrix_path}:{row_number}.risk_tier",
                            "Risk tier must be nonblank for a populated row.",
                            source="action_risk_matrix",
                        )
                    )
                elif normalized_risk_tier not in ALLOWED_ACTION_RISK_TIERS:
                    issues.append(
                        ValidationIssue(
                            f"{matrix_path}:{row_number}.risk_tier",
                            (
                                f"Unsupported risk tier `{raw_risk_tier}`; expected one of: "
                                + ", ".join(
                                    sorted(ALLOWED_ACTION_RISK_TIERS)
                                )
                                + "."
                            ),
                            source="action_risk_matrix",
                        )
                    )
                if not raw_human_review:
                    issues.append(
                        ValidationIssue(
                            f"{matrix_path}:{row_number}.human_review_required",
                            (
                                "Human-review requirement must be nonblank "
                                "for a populated row."
                            ),
                            source="action_risk_matrix",
                        )
                    )
                elif normalized_human_review not in ALLOWED_BOOLEAN_VALUES:
                    issues.append(
                        ValidationIssue(
                            f"{matrix_path}:{row_number}.human_review_required",
                            (
                                "Unsupported human-review requirement "
                                f"`{raw_human_review}`; expected one of: "
                                + ", ".join(sorted(ALLOWED_BOOLEAN_VALUES))
                                + "."
                            ),
                            source="action_risk_matrix",
                        )
                    )
                normalized_values = dict(raw_values)
                normalized_values["risk_tier"] = normalized_risk_tier
                normalized_values["human_review_required"] = (
                    normalized_human_review
                )
                rows.append(
                    ActionRiskRow(
                        raw_values=raw_values,
                        normalized_values=normalized_values,
                        source_line=row_number,
                    )
                )
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
