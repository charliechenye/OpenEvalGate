"""Structural inspection for the action-risk matrix."""

from __future__ import annotations

import csv
from collections import Counter
from dataclasses import dataclass, field
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
    raw_cells: tuple[str, ...] = ()

    def get(self, key: str, default: str = "") -> str:
        return self.normalized_values.get(key, default)


@dataclass(frozen=True)
class ActionRiskReview:
    present: bool
    valid: bool
    rows: list[ActionRiskRow]
    issues: list[ValidationIssue]
    normalized_headers: tuple[str, ...] = ()
    header_positions: dict[str, tuple[int, ...]] = field(
        default_factory=dict
    )


def inspect_action_risk_matrix(path: str | Path) -> ActionRiskReview:
    """Read the action matrix once and validate policy-relevant columns."""

    matrix_path = Path(path)
    if not matrix_path.is_file():
        return ActionRiskReview(False, False, [], [])

    try:
        with matrix_path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.reader(handle, strict=True)
            try:
                raw_headers = next(reader)
                header_row_present = True
            except StopIteration:
                raw_headers = []
                header_row_present = False
            if header_row_present and not raw_headers:
                raw_headers = [""]
            normalized_headers = tuple(
                header.strip() for header in raw_headers
            )
            positions: dict[str, list[int]] = {}
            for index, header in enumerate(normalized_headers):
                positions.setdefault(header, []).append(index)
            header_positions = {
                header: tuple(indexes)
                for header, indexes in positions.items()
            }
            blank_header_issues = [
                ValidationIssue(
                    f"{matrix_path}:header[{index + 1}]",
                    "Action-risk header name must be nonblank.",
                    source="action_risk_matrix",
                )
                for index, header in enumerate(normalized_headers)
                if not header
            ]
            header_counts = Counter(normalized_headers)
            seen_duplicates: set[str] = set()
            duplicate_headers: list[str] = []
            for header in normalized_headers:
                if (
                    header
                    and header_counts[header] > 1
                    and header not in seen_duplicates
                ):
                    seen_duplicates.add(header)
                    duplicate_headers.append(header)
            duplicate_header_issues = [
                ValidationIssue(
                    f"{matrix_path}:header",
                    f"Duplicate action-risk header: {header}.",
                    source="action_risk_matrix",
                )
                for header in duplicate_headers
            ]
            missing = [
                column
                for column in REQUIRED_ACTION_RISK_COLUMNS
                if column not in header_positions
            ]
            missing_header_issues = [
                ValidationIssue(
                    f"{matrix_path}:{column}",
                    "Required action-risk column is missing.",
                    source="action_risk_matrix",
                )
                for column in missing
            ]
            issues = [
                *blank_header_issues,
                *duplicate_header_issues,
                *missing_header_issues,
            ]
            usable_headers = {
                header: indexes[0]
                for header, indexes in header_positions.items()
                if header and len(indexes) == 1
            }
            rows: list[ActionRiskRow] = []
            for row_number, cells in enumerate(reader, start=2):
                raw_cells = tuple(cells)
                if not any(cell.strip() for cell in raw_cells):
                    continue
                padded_cells = list(raw_cells)
                if len(padded_cells) < len(normalized_headers):
                    padded_cells.extend(
                        [""] * (len(normalized_headers) - len(padded_cells))
                    )
                row_issues: list[ValidationIssue] = []
                if len(raw_cells) > len(normalized_headers):
                    row_issues.append(
                        ValidationIssue(
                            f"{matrix_path}:{row_number}",
                            "Action-risk row contains more cells than the header.",
                            source="action_risk_matrix",
                        )
                    )
                raw_values = {
                    header: padded_cells[index].strip()
                    for header, index in usable_headers.items()
                }
                normalized_values = dict(raw_values)
                if "risk_tier" in raw_values:
                    normalized_values["risk_tier"] = raw_values[
                        "risk_tier"
                    ].lower()
                if "human_review_required" in raw_values:
                    normalized_values["human_review_required"] = raw_values[
                        "human_review_required"
                    ].lower()

                if "action" in usable_headers and not raw_values["action"]:
                    row_issues.append(
                        ValidationIssue(
                            f"{matrix_path}:{row_number}.action",
                            "Action must be nonblank for a populated row.",
                            source="action_risk_matrix",
                        )
                    )
                if "risk_tier" in usable_headers:
                    raw_risk_tier = raw_values["risk_tier"]
                    normalized_risk_tier = normalized_values["risk_tier"]
                    if not raw_risk_tier:
                        row_issues.append(
                            ValidationIssue(
                                f"{matrix_path}:{row_number}.risk_tier",
                                "Risk tier must be nonblank for a populated row.",
                                source="action_risk_matrix",
                            )
                        )
                    elif (
                        normalized_risk_tier
                        not in ALLOWED_ACTION_RISK_TIERS
                    ):
                        row_issues.append(
                            ValidationIssue(
                                f"{matrix_path}:{row_number}.risk_tier",
                                (
                                    f"Unsupported risk tier `{raw_risk_tier}`; "
                                    "expected one of: "
                                    + ", ".join(
                                        sorted(ALLOWED_ACTION_RISK_TIERS)
                                    )
                                    + "."
                                ),
                                source="action_risk_matrix",
                            )
                        )
                if "human_review_required" in usable_headers:
                    raw_human_review = raw_values[
                        "human_review_required"
                    ]
                    normalized_human_review = normalized_values[
                        "human_review_required"
                    ]
                    if not raw_human_review:
                        row_issues.append(
                            ValidationIssue(
                                (
                                    f"{matrix_path}:{row_number}."
                                    "human_review_required"
                                ),
                                (
                                    "Human-review requirement must be nonblank "
                                    "for a populated row."
                                ),
                                source="action_risk_matrix",
                            )
                        )
                    elif (
                        normalized_human_review
                        not in ALLOWED_BOOLEAN_VALUES
                    ):
                        row_issues.append(
                            ValidationIssue(
                                (
                                    f"{matrix_path}:{row_number}."
                                    "human_review_required"
                                ),
                                (
                                    "Unsupported human-review requirement "
                                    f"`{raw_human_review}`; expected one of: "
                                    + ", ".join(
                                        sorted(ALLOWED_BOOLEAN_VALUES)
                                    )
                                    + "."
                                ),
                                source="action_risk_matrix",
                            )
                        )
                issues.extend(row_issues)
                rows.append(
                    ActionRiskRow(
                        raw_values=raw_values,
                        normalized_values=normalized_values,
                        source_line=row_number,
                        raw_cells=raw_cells,
                    )
                )
    except (OSError, csv.Error, UnicodeError) as exc:
        return ActionRiskReview(
            present=True,
            valid=False,
            rows=[],
            issues=[
                ValidationIssue(
                    str(matrix_path),
                    f"Could not read action-risk matrix: {exc}",
                    source="action_risk_matrix",
                )
            ],
        )

    return ActionRiskReview(
        present=True,
        valid=not issues,
        rows=rows,
        issues=issues,
        normalized_headers=normalized_headers,
        header_positions=header_positions,
    )
