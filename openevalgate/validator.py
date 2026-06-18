"""Project structure validation for OpenEvalGate examples and user projects."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from openevalgate.escalation import validate_escalation_contract
from openevalgate.eval_results import validate_eval_results
from openevalgate.schema import ValidationIssue, validate_eval_cases


REQUIRED_PROJECT_FILES = [
    "assistant_prd.md",
    "eval_cases.yaml",
    "action_risk_matrix.csv",
    "output_critic_rubric.csv",
    "launch_gate_review.md",
    "business_behavior_contract.md",
    "automation_boundary_matrix.md",
    "human_escalation_design.md",
    "chatbot_success_metric_stack.md",
    "trust_preservation_review.md",
]

OPTIONAL_PROJECT_FILES = [
    "model_arena_scorecard.csv",
    "eval_results.csv",
    "domain_owner_feedback_loop.md",
    "agent_behavior_change_request.md",
    "p0_failure_mode_checklist.md",
    "tail_risk_eval_cases.yaml",
    "purpose_built_assistant_scope.md",
    "escalation_contract.yaml",
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

    if (root / "eval_results.csv").is_file():
        results_validation = validate_eval_results(root)
        issues.extend(results_validation.issues)

    escalation_path = root / "escalation_contract.yaml"
    if escalation_path.is_file():
        escalation_validation = validate_escalation_contract(escalation_path, eval_path)
        issues.extend(escalation_validation.issues)

    valid = not missing and not issues
    return ProjectCheckResult(valid, root, missing, present_optional, issues)
