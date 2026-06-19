# Launch Gate Review

| Gate | Status | Evidence | Required mitigation | Owner |
| --- | --- | --- | --- | --- |
| Scope gate | pass | PRD defines product fit and pricing boundaries. | None | product |
| Golden eval gate | partial | Historical and adversarial commercial cases exist. | Add fresh drift samples from sales chat. | revenue_product |
| Model selection gate | pass | Balanced model chosen from scorecard. | None | ml_engineering |
| Model arena gate | pass | Three candidates compared on product-fit and pricing cases. | None | ml_engineering |
| Routing / capability allocation gate | partial | Routing policy assigns product, pricing, approval, and specialist workflows. | Correct legal/security workflow assignment regression before expansion. | ml_engineering |
| Grounding gate | partial | Product catalog and pricing policy references defined. | Add stale-context behavior. | platform |
| SOP/policy compilation gate | partial | Roadmap and pricing policies identified. | Compile allowed commercial claim snippets. | platform |
| Tool/action safety gate | partial | Discount and contract actions blocked in rubric. | Add explicit action risk matrix before launch. | platform |
| Input filter gate | partial | Commercial commitment asks identified. | Add competitor and jailbreak cases. | trust_safety |
| Output critic gate | pass | Rubric covers claims, pricing, and commitments. | None | ai_quality |
| Human escalation gate | pass | Sales follow-up, legal/security review, and discount approval paths exist. | None | sales_ops |
| Observability gate | partial | Feedback and handoff metrics proposed. | Add dashboard owner. | platform |
| Cost/latency gate | pass | Candidate latency and cost are inside target. | None | engineering |
| Drift monitoring gate | partial | Sales chat sample review proposed. | Schedule weekly drift review. | ai_quality |
| Rollback gate | partial | Product owner can disable widget. | Define launch stop criteria. | engineering |
| Owner signoff gate | partial | Launch owner named. | Complete final review. | product |
