# Launch Gate Review

| Gate | Status | Evidence | Required mitigation | Owner |
| --- | --- | --- | --- | --- |
| Scope gate | pass | PRD defines supported refund, order status, and escalation use cases. | None | product |
| Trust preservation gate | pass | Trust preservation review identifies wrong-promise, escalation blocking, and containment risks. | None | product |
| Business behavior contract gate | pass | Business behavior contract is signed by product, operations, policy, and platform owners. | None | support_ops |
| Golden eval gate | pass | Eval set includes historical, boundary, adversarial, regression, and fresh drift cases. | None | ai_product_team |
| Tail-risk / P0 failure mode gate | pass | P0 checklist covers refund overpromise, unauthorized refund, safety escalation, and containment failure. | None | trust_safety |
| Model selection gate | pass | Candidate model selected from internal arena results. | None | ml_engineering |
| Model arena gate | partial | Three candidates compared on launch evals. | Add a final latency run before rollout. | ml_engineering |
| Routing / capability allocation gate | partial | Versioned routing policy covers six workflows and two approved models. | Fix high-risk workflow assignment regressions and rerun routing slices. | ml_engineering |
| Grounding gate | pass | Refund and support-tone policies are explicit retrieved context. | None | platform |
| SOP/policy compilation gate | pass | Policy references are versioned and compiled before generation. | None | platform |
| Tool/action safety gate | pass | Action risk matrix blocks prohibited actions and requires approval for high-risk refund and safety actions. | None | platform |
| Automation boundary gate | pass | Automation boundary matrix defines automate, clarify, recommend, approval, escalate, and block routes. | None | product |
| Human escalation gate | pass | Human escalation design covers refund history, angry users, safety language, and policy ambiguity. | None | operations |
| Input filter gate | partial | Unsupported merchant blame and refund override requests are defined. | Add prompt injection cases to eval set. | trust_safety |
| Output critic gate | pass | Rubric covers grounding, policy alignment, helpfulness, action safety, and escalation. | None | ai_quality |
| Domain-owner feedback loop gate | pass | Support Operations feedback loop created behavior change request for refund-history escalation. | None | platform |
| Observability gate | partial | Required trace fields identified. | Confirm dashboard owner and alert threshold. | platform |
| Cost/latency gate | partial | Candidate cost and latency captured. | Validate p95 latency under launch traffic. | engineering |
| Journey metric / durable resolution gate | pass | Metric stack tracks true resolution, recontact, repeat escalation, and time to durable resolution. | None | product |
| Business trust metric gate | pass | Metric stack tracks complaint rate, trust/sentiment, compensation leakage, and downstream support cost. | None | support_ops |
| Drift monitoring gate | partial | Fresh drift sample review proposed. | Schedule weekly review and owner rotation. | ai_quality |
| Rollback gate | pass | Product and engineering owners can pause rollout. | None | engineering |
| Owner signoff gate | pass | Launch signoff owners recorded in business behavior contract. | None | product |
