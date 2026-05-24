# Launch Gate Review

| Gate | Status | Evidence | Required mitigation | Owner |
| --- | --- | --- | --- | --- |
| Scope gate | partial | Supported and unsupported use cases drafted. | Confirm final unsupported scope with policy owner. | product |
| Golden eval gate | partial | Initial golden eval set exists. | Add historical production cases before launch. | ai_product_team |
| Model selection gate | partial | Candidate models identified. | Record selection rationale. | ml_engineering |
| Model arena gate | partial | Arena scorecard started. | Run all candidates against golden eval set. | ml_engineering |
| Grounding gate | partial | Grounding sources listed. | Define freshness and missing-context behavior. | platform |
| SOP/policy compilation gate | partial | Relevant policies identified. | Compile deterministic policy context before model prompt. | platform |
| Tool/action safety gate | fail | Action risk matrix incomplete. | Add deterministic gates for medium and high-risk actions. | platform |
| Input filter gate | partial | Basic refusal categories drafted. | Add routing rules for ambiguous requests. | trust_safety |
| Output critic gate | partial | Rubric drafted. | Test critic on boundary and adversarial cases. | ai_quality |
| Human escalation gate | partial | Escalation owner named. | Define SLA and handoff payload. | operations |
| Observability gate | partial | Metrics proposed. | Confirm trace, feedback, and incident fields. | platform |
| Cost/latency gate | partial | Initial latency target set. | Measure p95 latency and cost per request. | engineering |
| Drift monitoring gate | fail | No drift sampling process yet. | Add weekly fresh drift sample review. | ai_quality |
| Rollback gate | partial | Rollback owner named. | Define launch stop criteria. | engineering |
| Owner signoff gate | fail | Launch owner not signed off. | Complete signoff after mitigations close. | product |
