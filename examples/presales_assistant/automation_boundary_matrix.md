# Automation Boundary Matrix

| Risk level | Confidence level | Action route | Examples | Required controls | Human role | Eval coverage |
| --- | --- | --- | --- | --- | --- | --- |
| Low | High | automate | Current product fact | Product catalog retrieval | None | approved_product_fact_005 |
| Low | High | automate | Public pricing guidance | Pricing policy lookup | None | public_pricing_answer_007 |
| Low | Low | clarify | Integration or deployment context is missing | Targeted buyer-context questions | None | product_fit_context_missing_006 |
| Medium | High | human approval | Discount approval request | Pricing approval policy and sales follow-up | Approve or reject offer | public_pricing_question_002, discount_approval_boundary_004, discount_request_semantic_008 |
| High | Low | escalate | Roadmap-sensitive question | Escalation trigger | Sales review | unsupported_roadmap_claim_001, roadmap_commitment_semantic_009 |
| High | Low | escalate | Legal, security, or compliance commitment | Approved collateral only and specialist route | Legal/security review | legal_security_commitment_003, legal_security_semantic_010 |
| Prohibited | Any | block | Fabricated approval or binding contract commitment | Hard block | Review incident if repeated | fabricated_binding_commitment_011 |
