"""Project structure validation for OpenEvalGate examples and user projects."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from openevalgate.action_risk import ActionRiskReview, inspect_action_risk_matrix
from openevalgate.escalation import validate_escalation_contract
from openevalgate.eval_results import validate_eval_results
from openevalgate.provenance import RunIdentityInspection, RunIdentityStatus, inspect_run_identity
from openevalgate.launch_gate_review import (
    LaunchGateReview,
    parse_launch_gate_review,
)
from openevalgate.routing import validate_routing_policy
from openevalgate.review_policy import validate_review_policy
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
    "routing_policy.yaml",
    "review_policy.yaml",
    "run_manifest.yaml",
]


@dataclass(frozen=True)
class ProjectCheckResult:
    valid: bool
    project_dir: Path
    missing_required: list[str]
    present_optional: list[str]
    issues: list[ValidationIssue]
    launch_gate_review: LaunchGateReview = field(
        default_factory=lambda: LaunchGateReview(
            [],
            [],
            frozenset(),
            [],
        )
    )
    action_risk_review: ActionRiskReview = field(
        default_factory=lambda: ActionRiskReview(False, False, [], [])
    )
    run_identity_inspection: RunIdentityInspection | None = None


def check_project(
    project_dir: str | Path,
    *,
    identity_inspection: RunIdentityInspection | None = None,
) -> ProjectCheckResult:
    """Validate required launch gate files and eval schema for a project directory."""

    root = Path(project_dir)
    issues: list[ValidationIssue] = []
    run_identity = identity_inspection

    if not root.exists() or not root.is_dir():
        return ProjectCheckResult(
            False,
            root,
            REQUIRED_PROJECT_FILES,
            [],
            [ValidationIssue(str(root), "Project directory not found.")],
            LaunchGateReview([], [], frozenset(), []),
            ActionRiskReview(False, False, [], []),
            None,
        )

    if run_identity is None:
        run_identity = inspect_run_identity(root)

    missing = [name for name in REQUIRED_PROJECT_FILES if not (root / name).is_file()]
    present_optional = [name for name in OPTIONAL_PROJECT_FILES if (root / name).is_file()]

    eval_path = root / "eval_cases.yaml"
    if eval_path.is_file():
        eval_result = validate_eval_cases(eval_path)
        issues.extend(eval_result.issues)

    results_validation = validate_eval_results(root, identity_inspection=run_identity)
    issues.extend(results_validation.issues)

    if (root / "review_policy.yaml").is_file():
        issues.extend(validate_review_policy(root).issues)

    escalation_path = root / "escalation_contract.yaml"
    if escalation_path.is_file():
        escalation_validation = validate_escalation_contract(escalation_path, eval_path)
        issues.extend(escalation_validation.issues)

    routing_path = root / "routing_policy.yaml"
    if routing_path.is_file():
        routing_validation = validate_routing_policy(routing_path, eval_path)
        issues.extend(routing_validation.issues)

    launch_gate_review = parse_launch_gate_review(root / "launch_gate_review.md")
    issues.extend(launch_gate_review.issues)

    action_risk_review = inspect_action_risk_matrix(
        root / "action_risk_matrix.csv"
    )
    issues.extend(action_risk_review.issues)

    valid = not missing and not issues
    return ProjectCheckResult(
        valid,
        root,
        missing,
        present_optional,
        issues,
        launch_gate_review,
        action_risk_review,
        run_identity,
    )
