# Automation Boundary Matrix

| Risk level | Confidence level | Action route | Examples | Required controls | Human role | Eval coverage |
| --- | --- | --- | --- | --- | --- | --- |
| Low | High | automate | Current product fact | Product catalog retrieval | None | product fit evals |
| Medium | High | recommend | Public pricing guidance | Pricing policy lookup | Sales handles exceptions | public_pricing_question_002 |
| Medium | High | human approval | Discount approval request | Pricing approval policy and sales follow-up | Approve or reject offer | discount_approval_boundary_004 |
| High | Low | escalate | Roadmap-sensitive question | Escalation trigger | Sales review | unsupported_roadmap_claim_001 |
| High | Low | escalate | Legal, security, or compliance commitment | Approved collateral only and specialist route | Legal/security review | legal_security_commitment_003 |
| Prohibited | Any | block | Discount approval or contract commitment | Hard block | Review incident if repeated | commercial boundary evals |
