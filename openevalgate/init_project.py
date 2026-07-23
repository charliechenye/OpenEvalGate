"""Deterministic minimal project scaffolding."""

from __future__ import annotations

from pathlib import Path


MINIMAL_PROFILE_FILES = {
    "assistant_prd.md": """# My AI Assistant\n\n**System name:** My AI Assistant\n**Assistant type:** customer_support_assistant\n**Launch owner:**\n**Review date:**\n\n## Purpose\n\nReplace this synthetic starter description with the assistant's bounded purpose.\n\n## Supported and Unsupported Uses\n\nDocument the supported use cases, unsupported requests, required context, and human path.\n""",
    "business_behavior_contract.md": """# Business Behavior Contract\n\nThis starter contract is synthetic and incomplete. Define expected behavior, unacceptable behavior, action policy, escalation thresholds, and signoff owners before relying on the result.\n""",
    "trust_preservation_review.md": """# Trust Preservation Review\n\nThis starter review is synthetic and incomplete. Document the user trust relationship, likely failure modes, and mitigation evidence.\n""",
    "eval_cases.yaml": """- id: synthetic_minimal_case\n  assistant_type: customer_support_assistant\n  use_case: explain a product policy\n  case_type: synthetic_boundary\n  user_input: What is the return policy?\n  user_context:\n    account_state: synthetic\n  retrieved_context:\n    policy: synthetic return policy\n  risk_tier: low\n  expected_behavior:\n    - Explain the policy using the supplied context.\n  unacceptable_behavior:\n    - Invent policy terms or account facts.\n  expected_tool_behavior:\n    allowed_tools: []\n    blocked_tools: []\n  expected_route: show\n  grading_rubric:\n    grounding: 3\n    clarity: 3\n  production_frequency: occasional\n  policy_reference: synthetic_policy\n  owner: product\n  last_reviewed: 2025-01-01\n""",
    "action_risk_matrix.csv": """action,risk_tier,possible_harm,preconditions,deterministic_gate,human_review_required,owner\nread_policy,low,Incorrect policy explanation,synthetic context available,context check,false,product\n""",
    "output_critic_rubric.csv": """dimension,description,pass_criteria,fail_criteria,required_route_on_fail,owner\ngrounding,Uses supplied context,All claims are supported,Invented claims,revise,product\n""",
    "automation_boundary_matrix.md": """# Automation Boundary Matrix\n\n| Request class | Route | Human review | Evidence required |\n| --- | --- | --- | --- |\n| Low-risk policy explanation | show | no | Supplied context |\n| Ambiguous or high-impact request | escalate | yes | Human destination and handoff context |\n""",
    "human_escalation_design.md": """# Human Escalation Design\n\nDefine escalation triggers, destinations, payload requirements, fallback behavior, durable resume, SLA, and ownership. This starter artifact is synthetic and incomplete.\n""",
    "chatbot_success_metric_stack.md": """# Chatbot Success Metric Stack\n\nDefine quality, journey, business, trust, cost, and latency metrics. State which anti-metrics must prevent a misleading launch decision.\n""",
    "launch_gate_review.md": """# Launch Gate Review\n\n| Gate | Status | Evidence | Required mitigation | Owner |\n| --- | --- | --- | --- | --- |\n| Scope gate | partial | Synthetic starter scope only. | Replace with reviewed scope. | product |\n| Trust preservation gate | partial | Synthetic starter review only. | Complete trust review. | product |\n| Golden eval gate | partial | One synthetic case only. | Add representative and critical cases. | ai_quality |\n| Owner signoff gate | fail | No signoff recorded. | Complete cross-functional signoff. | product |\n""",
    "README.md": """# Minimal OpenEvalGate Project\n\nThis directory was created by `openevalgate init --profile minimal`. Every starter artifact is synthetic or a placeholder. Replace it with reviewed evidence before using a report for a release decision.\n\nRun:\n\n```bash\nopenevalgate validate eval_cases.yaml\nopenevalgate check .\nopenevalgate report . --format card\n```\n\nA blocked or incomplete result is expected until the evidence package is completed.\n""",
}


def initialize_project(project_dir: str | Path, *, force: bool = False) -> list[Path]:
    """Create the minimal profile without overwriting user files by default."""

    root = Path(project_dir)
    if root.exists() and not root.is_dir():
        raise ValueError(f"Target exists and is not a directory: {root}")
    root.mkdir(parents=True, exist_ok=True)
    existing = sorted(path for path in root.iterdir())
    if existing and not force:
        raise ValueError(f"Refusing to initialize non-empty directory: {root}")

    written: list[Path] = []
    for relative, content in sorted(MINIMAL_PROFILE_FILES.items()):
        target = root / relative
        if target.exists() and not force:
            raise ValueError(f"Refusing to overwrite existing file: {target}")
        target.write_text(content, encoding="utf-8", newline="\n")
        written.append(target)
    return written
