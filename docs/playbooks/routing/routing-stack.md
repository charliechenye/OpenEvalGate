# Routing Stack

Production routing is broader than choosing a small model or a large model. A mature GenAI system routes the request through four separate decisions:

```text
Scenario -> specialist workflow -> model capability -> risk control path
```

Do not collapse these layers into one probabilistic model choice. Each layer answers a different launch-readiness question.

## Routing Layers

| Layer | Question | Example route for delayed order support |
| --- | --- | --- |
| Scenario routing | What job is the user trying to accomplish? | Check ETA, request refund, report fraud, request exception |
| Workflow routing | Which bounded workflow should handle it? | Delivery-status lookup, refund flow, fraud escalation, exception review |
| Model routing | What level of model capability does that workflow require? | Retrieval plus small model, stronger reasoning model, deterministic response, or no generation |
| Risk routing | Can the result be returned, executed, confirmed, reviewed, or blocked? | Show answer, run eligibility check, request confirmation, escalate, require approval, block |

## Control Plane Responsibilities

The routing control plane is the platform layer that makes routing governable, observable, and reversible. It should manage:

- Scenario taxonomy.
- Specialist workflow registry.
- Approved model pool.
- Routing policies and thresholds.
- Deterministic risk overrides.
- Fallback paths.
- Experiment configuration.
- Observability and trace logging.
- Rollout and rollback controls.

The router should optimize inside an approved policy envelope. It should not decide whether the policy applies.

## Deterministic Overrides

Model strength is not a safety control. A frontier model may reason better, but it does not become an authorization system.

High-impact actions still need deterministic checks, structured validation, auditability, and human approval where judgment matters. Examples include:

- Refund eligibility and compensation limits.
- Account ownership and authentication.
- Region-specific policy restrictions.
- Fraud, safety, legal, privacy, or compliance escalation.
- High-value exceptions.
- Prohibited account or financial mutations.

If a route proposes an action that violates the policy envelope, the deterministic control path wins.

## Observability

At minimum, log enough to reconstruct why a route was chosen and whether it worked:

- Scenario and workflow classification.
- Risk tier.
- Router version.
- Candidate model pool and selected model.
- Routing reason, confidence, or score where available.
- Time to first token and end-to-end latency.
- Tool calls and validation results.
- Deterministic control decisions.
- Escalation path.
- Outcome-quality score.
- Repeat attempts, recontacts, and abandonment.

Routing should be treated as a living control plane:

```text
Define segments -> route within approved paths -> observe outcomes
-> review failure clusters -> add cases to the eval set -> recalibrate
```

## Staged Rollout

Start with deterministic routing. Add learned routing only when workload variance, traffic volume, and evaluation data justify the operational complexity.

A practical rollout sequence:

1. Establish the current baseline.
2. Identify bounded eligible fast paths.
3. Validate offline against golden evals and tail-risk cases.
4. Shadow alternative routes without changing user-visible behavior.
5. Launch bounded routing to a small eligible segment.
6. Monitor resolution, latency, friction, safety, escalation, and cost together.
7. Expand only when end-to-end outcomes remain healthy.
8. Roll back quickly when routing errors create unresolved tasks, unsafe actions, or trust risk.

## Anti-Patterns

- Routing every request to the frontier model.
- Routing every request to the cheapest model.
- Treating model size as a safety control.
- Optimizing on average latency or average cost without scenario slices.
- Launching without fallbacks, observability, rollback, and owner signoff.
