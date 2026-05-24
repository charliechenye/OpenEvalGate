"""Project structure validation for OpenEvalGate examples and user projects."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from openevalgate.schema import ValidationIssue, validate_eval_cases


REQUIRED_PROJECT_FILES = [
    "assistant_prd.md",
    "eval_cases.yaml",
    "output_critic_rubric.csv",
    "launch_gate_review.md",
]

OPTIONAL_PROJECT_FILES = [
    "model_arena_scorecard.csv",
    "action_risk_matrix.csv",
]


@dataclass(frozen=True)
class ProjectCheckResult:
    valid: bool
    project_dir: Path
    missing_required: list[str]
    present_optional: list[str]
    issues: list[ValidationIssue]


def check_project(project_dir: str | Path) -> ProjectCheckResult:
    """Validate required launch gate files and eval schema for a project directory."""

    root = Path(project_dir)
    issues: list[ValidationIssue] = []

    if not root.exists() or not root.is_dir():
        return ProjectCheckResult(False, root, REQUIRED_PROJECT_FILES, [], [ValidationIssue(str(root), "Project directory not found.")])

    missing = [name for name in REQUIRED_PROJECT_FILES if not (root / name).is_file()]
    present_optional = [name for name in OPTIONAL_PROJECT_FILES if (root / name).is_file()]

    eval_path = root / "eval_cases.yaml"
    if eval_path.is_file():
        eval_result = validate_eval_cases(eval_path)
        issues.extend(eval_result.issues)

    valid = not missing and not issues
    return ProjectCheckResult(valid, root, missing, present_optional, issues)
