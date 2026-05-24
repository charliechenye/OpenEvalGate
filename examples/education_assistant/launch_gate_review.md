# Launch Gate Review

| Gate | Status | Evidence | Required mitigation | Owner |
| --- | --- | --- | --- | --- |
| Scope gate | pass | PRD defines concept explanation and practice hint boundaries. | None | product |
| Golden eval gate | partial | Initial boundary and regression cases exist. | Add historical learner support cases. | learning_product |
| Model selection gate | partial | Candidate model selected from prior platform default. | Record product-specific selection rationale. | ml_engineering |
| Model arena gate | fail | No education-specific arena run yet. | Run candidate models on golden eval set. | ml_engineering |
| Grounding gate | pass | Course material and policy references are explicit. | None | platform |
| SOP/policy compilation gate | partial | Academic integrity policy identified. | Compile per-course response rules. | platform |
| Tool/action safety gate | pass | Answer-key tool is blocked. | None | platform |
| Input filter gate | partial | Graded-answer requests are defined. | Add jailbreak and answer-leakage examples. | trust_safety |
| Output critic gate | pass | Rubric covers integrity, grounding, and helpfulness. | None | ai_quality |
| Human escalation gate | partial | Instructor review path exists. | Define SLA for academic integrity disputes. | operations |
| Observability gate | partial | Feedback and escalation metrics proposed. | Add drift sampling owner. | platform |
| Cost/latency gate | partial | No launch load test yet. | Measure p95 latency. | engineering |
| Drift monitoring gate | fail | No fresh sample process. | Add weekly learner request review. | ai_quality |
| Rollback gate | partial | Product owner can pause launch. | Define stop criteria. | engineering |
| Owner signoff gate | partial | Launch owner identified. | Complete signoff after arena and drift plan. | product |
