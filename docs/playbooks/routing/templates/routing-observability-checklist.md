# Routing Observability Checklist

Use this checklist to confirm that production traces explain why a route was chosen, what controls ran, and whether the user outcome improved.

| Signal | Required before launch | Owner | Notes |
| --- | --- | --- | --- |
| Request ID and response ID | yes | platform | Needed for incident review. |
| Scenario classification | yes | platform | Include label, confidence, and version where available. |
| Specialist workflow | yes | platform | The bounded workflow selected for the user scenario. |
| Risk tier | yes | trust_safety | low, medium, high, or prohibited. |
| Router version | yes | platform | Needed for rollback and regression analysis. |
| Candidate model pool | yes | platform | Approved models or deterministic systems considered. |
| Selected model or route | yes | platform | Include deterministic route, model route, cascade, or human review. |
| Routing reason or score | yes | ai_quality | Record explanation, score, policy rule, or classifier output. |
| Time to first token | yes | engineering | Track p50, p95, and outliers. |
| End-to-end time to resolution | yes | product | More important than model latency alone. |
| Tool calls and outcomes | yes | platform | Include validation failures and retries. |
| Deterministic control result | yes | platform | Eligibility, ownership, policy, confirmation, block, or approval. |
| Escalation path | yes | operations | Human queue, approval workflow, or blocked action. |
| Output quality score | yes | ai_quality | Rubric, critic, human review, or eval result. |
| User feedback | yes | product | Explicit and implicit feedback. |
| Repeat attempts or recontacts | yes | product | Needed for durable resolution and cheap-failure detection. |
| Abandonment | yes | product | Needed to understand latency and interaction burden. |
| Cost per resolved task | yes | platform | Include model, tools, retries, review, and downstream rework where measurable. |
| Rollback marker | yes | engineering | Identifies traffic affected by route changes. |

## Review Cadence

| Review | Cadence | Owner | Output |
| --- | --- | --- | --- |
| Routing quality review |  | ai_quality | Failure clusters and eval updates |
| Scenario drift review |  | product | New or changed scenarios |
| Risk-control review |  | trust_safety | Control gaps and blocked-action review |
| Cost/latency review |  | platform | Route tuning recommendations |
| Rollback readiness review |  | engineering | Confirm rollback still works |
