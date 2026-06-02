# Presales Commercial Queue Routing

| Escalation reason | Destination | Response model | SLA | Priority | Required payload | Fallback path | Owner | Eval coverage |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Roadmap or unsupported feature commitment | Account executive follow-up | Async case | 1 business day | medium | Prospect question, account segment, current product facts, requested commitment | Sales ops triage | sales_ops | unsupported_roadmap_claim_001 |
| Discount or pricing exception | Account executive follow-up | Async case | 1 business day | medium | Public pricing context, requested discount, sales stage | Sales ops triage | sales_ops | public_pricing_question_002, discount_approval_boundary_004 |
| Legal, security, or compliance commitment | Legal/security review | Specialist review | 2 business days | high | Question, security context, customer requirements, approved collateral | Sales ops triage | legal_security | legal_security_commitment_003 |
