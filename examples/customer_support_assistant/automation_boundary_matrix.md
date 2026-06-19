# Automation Boundary Matrix

| Risk level | Confidence level | Action route | Examples | Required controls | Human role | Eval coverage |
| --- | --- | --- | --- | --- | --- | --- |
| Low | High | automate | Order status lookup | Auth and order ownership check | None | routine_status_no_escalation_013 |
| Low | High | automate | Routine status lookup with complete context | Order lookup and latest carrier event | None | routine_status_no_escalation_013 |
| Low | Low | clarify | Missing authentication or order ownership | Clarifying question before data access | None | refund_missing_authentication_015 |
| Medium | High | automate | Refund is eligible and inside autonomous limit | Eligibility service, policy version, and idempotency | None | refund_boundary_case_001, refund_semantic_invariance_016 |
| High | High | human approval | Refund exceeds autonomous amount limit | Eligibility service, audit event, and paused execution | Approve or reject | refund_above_limit_014 |
| Medium | Low | escalate | Policy ambiguity or conflicting context | Escalation trigger | Decide outcome | policy_ambiguity_005 |
| Medium | Low | escalate | Refund eligibility service unavailable | Preserve checkpoint and create async case | Retry or manually review | dependency_failure_escalation_011 |
| High | High | human approval | Repeated refund history | Eligibility service, audit event | Approve or reject | refund_abuse_history_002 |
| High | Low | escalate | Angry user demanding human | Escalation trigger | Handle case | angry_user_escalation_004 |
| High | Low | escalate | Fraud or account takeover signal | Specialist route and sensitive-action block | Fraud operations review | wrong_destination_fraud_012 |
| High | Low | escalate | Customer safety or self-harm signal | Safety protocol trigger and ordinary-flow pause | Safety review | self_harm_threat_007 |
| Prohibited | Any | block | Refund without policy check | Hard block | Review incident if repeated | bypass_rules_006 |
