"""Launch-gate review parsing and declaration validation."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from openevalgate.schema import ValidationIssue


STANDARD_GATE_NAMES = (
    "scope gate",
    "trust preservation gate",
    "business behavior contract gate",
    "golden eval gate",
    "tail-risk / p0 failure mode gate",
    "model selection gate",
    "model arena gate",
    "routing / capability allocation gate",
    "grounding gate",
    "sop/policy compilation gate",
    "tool/action safety gate",
    "automation boundary gate",
    "human escalation gate",
    "input filter gate",
    "output critic gate",
    "domain-owner feedback loop gate",
    "observability gate",
    "cost/latency gate",
    "journey metric / durable resolution gate",
    "business trust metric gate",
    "drift monitoring gate",
    "rollback gate",
    "owner signoff gate",
)

ALLOWED_GATE_STATUSES = frozenset(
    {"pass", "partial", "fail", "not_applicable"}
)

NON_EVIDENCE_VALUES = frozenset(
    {
        "",
        "-",
        "none",
        "n/a",
        "na",
        "not provided",
        "not_provided",
        "tbd",
        "todo",
        "unknown",
    }
)

_STANDARD_GATE_SET = frozenset(STANDARD_GATE_NAMES)
_GATE_ALIASES = {
    "tail-risk/p0 failure mode gate": "tail-risk / p0 failure mode gate",
    "routing/capability allocation gate": "routing / capability allocation gate",
}


@dataclass(frozen=True)
class GateRow:
    """A launch-gate declaration with raw and canonical diagnostics."""

    gate: str
    status: str
    evidence: str
    mitigation: str
    owner: str
    canonical_gate: str | None = None
    source_line: int | None = None

    @property
    def normalized_status(self) -> str:
        return normalize_status(self.status)


@dataclass(frozen=True)
class LaunchGateReview:
    """Parsed launch-gate rows and structural declaration issues."""

    rows: list[GateRow]
    valid_rows: list[GateRow]
    invalid_canonical_gates: frozenset[str]
    issues: list[ValidationIssue]


def parse_launch_gate_review(path: str | Path) -> LaunchGateReview:
    """Parse and structurally validate a Markdown launch-gate table."""

    review_path = Path(path)
    if not review_path.is_file():
        return LaunchGateReview([], [], frozenset(), [])

    rows: list[GateRow] = []
    issues: list[ValidationIssue] = []
    for line_number, line in enumerate(
        review_path.read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        stripped = line.strip()
        if not stripped.startswith("|") or _is_separator_row(stripped):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if cells and normalize_gate_name(cells[0]) == "gate":
            continue
        if len(cells) < 5:
            issues.append(
                ValidationIssue(
                    f"{review_path}:{line_number}",
                    "Launch-gate rows must contain Gate, Status, Evidence, Required mitigation, and Owner.",
                    source="launch_gate_review",
                )
            )
            continue

        gate = cells[0]
        status = cells[1]
        normalized_gate = normalize_gate_name(gate)
        canonical_gate = canonicalize_gate_name(normalized_gate)
        row = GateRow(
            gate,
            status,
            cells[2],
            cells[3],
            cells[4],
            canonical_gate=canonical_gate,
            source_line=line_number,
        )
        rows.append(row)
        if row.normalized_status not in ALLOWED_GATE_STATUSES:
            issues.append(
                ValidationIssue(
                    f"{review_path}:{line_number}.status",
                    (
                        f"Unsupported launch-gate status {status!r}; expected one of: "
                        + ", ".join(sorted(ALLOWED_GATE_STATUSES))
                        + "."
                    ),
                    source="launch_gate_review",
                )
            )

    canonical_counts = Counter(
        row.canonical_gate for row in rows if row.canonical_gate is not None
    )
    duplicates = frozenset(
        gate for gate, count in canonical_counts.items() if count > 1
    )
    for canonical_gate in STANDARD_GATE_NAMES:
        if canonical_gate in duplicates:
            issues.append(
                ValidationIssue(
                    str(review_path),
                    f"Duplicate standard launch-gate declaration: {canonical_gate}.",
                    source="launch_gate_review",
                )
            )

    valid_rows = [
        row
        for row in rows
        if row.normalized_status in ALLOWED_GATE_STATUSES
        and row.canonical_gate not in duplicates
    ]
    return LaunchGateReview(rows, valid_rows, duplicates, issues)


def canonicalize_gate_name(gate: str) -> str | None:
    """Return a canonical standard-gate name, or None for a custom gate."""

    normalized = normalize_gate_name(gate)
    canonical = _GATE_ALIASES.get(normalized, normalized)
    return canonical if canonical in _STANDARD_GATE_SET else None


def normalize_gate_name(gate: str) -> str:
    return " ".join(gate.strip().lower().split())


def normalize_status(status: str) -> str:
    return status.strip().lower()


def is_meaningful_evidence(value: str) -> bool:
    return normalize_gate_name(value) not in NON_EVIDENCE_VALUES


def is_meaningful_mitigation(value: str) -> bool:
    return normalize_gate_name(value) not in NON_EVIDENCE_VALUES


def _is_separator_row(line: str) -> bool:
    cells = [cell.strip() for cell in line.strip("|").split("|")]
    return bool(cells) and all(cell and set(cell) <= {"-", ":"} for cell in cells)
