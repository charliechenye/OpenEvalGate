# Automation Boundary Matrix

| Risk level | Confidence level | Action route | Examples | Required controls | Human role | Eval coverage |
| --- | --- | --- | --- | --- | --- | --- |
| Low | High | automate | Order status lookup | Auth and order ownership check | None | status_regression |
| Low | Low | clarify | Missing order details | Clarifying question | None | missing_context_boundary |
| Medium | High | recommend | Refund appears eligible but no abuse signal | Eligibility service and policy version | Approve exceptions | refund_boundary_case_001 |
| Medium | Low | escalate | Policy ambiguity or conflicting context | Escalation trigger | Decide outcome | policy_ambiguity_005 |
| High | High | human approval | Repeated refund history | Eligibility service, audit event | Approve or reject | refund_abuse_history_002 |
| High | Low | escalate | Angry user demanding human | Escalation trigger | Handle case | angry_user_escalation_004 |
| Prohibited | Any | block | Refund without policy check | Hard block | Review incident if repeated | bypass_rules_006 |
