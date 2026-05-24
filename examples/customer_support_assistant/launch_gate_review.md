# Launch Gate Review

| Gate | Status | Evidence | Required mitigation | Owner |
| --- | --- | --- | --- | --- |
| Scope gate | pass | PRD defines supported refund, order status, and escalation use cases. | None | product |
| Golden eval gate | pass | Eval set includes historical, boundary, and adversarial cases. | None | ai_product_team |
| Model selection gate | pass | Candidate model selected from internal arena results. | None | ml_engineering |
| Model arena gate | partial | Three candidates compared on launch evals. | Add a final latency run before rollout. | ml_engineering |
| Grounding gate | pass | Refund and support-tone policies are explicit retrieved context. | None | platform |
| SOP/policy compilation gate | pass | Policy references are versioned and compiled before generation. | None | platform |
| Tool/action safety gate | partial | Action risk matrix blocks prohibited refund actions. | Add service-level audit event for refund attempts. | platform |
| Input filter gate | partial | Unsupported merchant blame and refund override requests are defined. | Add prompt injection cases to eval set. | trust_safety |
| Output critic gate | pass | Rubric covers grounding, policy alignment, helpfulness, action safety, and escalation. | None | ai_quality |
| Human escalation gate | pass | Boundary refund cases route to support ops. | None | operations |
| Observability gate | partial | Required trace fields identified. | Confirm dashboard owner and alert threshold. | platform |
| Cost/latency gate | partial | Candidate cost and latency captured. | Validate p95 latency under launch traffic. | engineering |
| Drift monitoring gate | partial | Fresh drift sample review proposed. | Schedule weekly review and owner rotation. | ai_quality |
| Rollback gate | pass | Product and engineering owners can pause rollout. | None | engineering |
| Owner signoff gate | partial | Launch owner named. | Complete final signoff after latency and observability evidence. | product |
