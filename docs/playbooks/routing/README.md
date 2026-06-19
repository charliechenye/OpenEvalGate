# Routing Playbook

This playbook helps product and platform teams decide when a GenAI system should use a simple deterministic path, a specialist workflow, a smaller model, a stronger reasoning model, a fallback, or human review.

OpenEvalGate treats routing as launch-readiness evidence. These artifacts do not replace `eval_cases.yaml`, the model arena, action-risk controls, observability, or launch gates. They make the routing decision explicit so teams can review it before production traffic depends on it.

For core project integration, copy the top-level `templates/routing_policy.yaml` to the assistant project as `routing_policy.yaml`. The structured policy is optional, but `openevalgate check` validates it and its eval-case references when present, and `openevalgate report` summarizes its workflow and model-assignment coverage.

## Who Should Use This

- AI product managers defining scenario and workflow behavior.
- GenAI platform teams building routing control planes.
- ML and AI engineers comparing models, cascades, and fallback paths.
- Operations, policy, trust, safety, legal, and compliance reviewers approving risk controls.

## Practitioner Workflow

1. Read [Routing Stack](routing-stack.md) to separate scenario, workflow, model, and risk routing.
2. Read [Right-Sized Intelligence Framework](right-sized-intelligence-framework.md) to decide when more model capability is worth the user friction and system cost.
3. Copy `templates/` from this playbook into your assistant project when routing needs explicit launch evidence.
4. Add `routing_policy.yaml` when workflow or subagent assignments should become machine-readable launch evidence.
5. Fill out one routing decision card per scenario or specialist workflow.
6. Design the routing experiment before launch, including latency-isolation and rollback criteria.
7. Add routing observability fields to production traces.
8. Use the staged rollout checklist to move from baseline to bounded rollout.
9. Feed failures, drift samples, and disputed routing decisions back into the golden eval set and launch gate review.

## Files

```text
docs/playbooks/routing/
  README.md
  right-sized-intelligence-framework.md
  routing-stack.md
  templates/
    routing-decision-card.yaml
    routing-experiment-plan.md
    routing-observability-checklist.md
    staged-rollout-checklist.md
  examples/
    delayed-order-support/
      scenario-routing-policy.yaml
      experiment-plan.md
      rollout-checklist.md
```

## How This Fits OpenEvalGate

Routing artifacts complement the existing launch-readiness project files:

- Use `eval_cases.yaml` to define expected behavior and route expectations.
- Use `model_arena_scorecard.csv` to compare candidate models.
- Use `routing_policy.yaml` to assign approved model capability to each bounded workflow or subagent.
- Use `action_risk_matrix.csv` and `automation_boundary_matrix.md` to define deterministic controls and allowed action paths.
- Use `observability_checklist.md` and the routing observability checklist to make routing decisions inspectable.
- Use `launch_gate_review.md` to record whether routing evidence is sufficient for launch.

OpenEvalGate does not run a router or call model APIs. Use your existing eval, tracing, routing, or LLMOps stack to execute experiments, then record the evidence in these artifacts.

Model selection is not always one product-wide decision. A specialist subagent can use a fixed or adaptive approved model pool, while deterministic and human workflows explicitly use no model. In every case, risk controls remain outside the model assignment.

## Practitioner Rule

Do not ask only:

> Which model is strongest?

Ask:

> What level of intelligence resolves this scenario with enough quality to justify the waiting time, user effort, cost, and risk controls it introduces?
