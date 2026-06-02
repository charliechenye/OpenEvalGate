# Customer Support Refund Queue Routing

| Escalation reason | Destination | Response model | SLA | Priority | Required payload | Fallback path | Owner | Eval coverage |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Explicit human request or bot loop | Live support or callback | Live or callback | 15 minutes | high | User goal, transcript summary, order state, prior turns | Async case queue | support_ops | angry_user_escalation_004 |
| Repeated refund history | Senior refund review | Approval queue | 30 minutes | high | Eligibility result, refund history, proposed decision, policy version | Hold action and notify user | support_policy | refund_abuse_history_002 |
| Conflicting order state | Policy support review | Specialist review | 1 business hour | medium | Order context, contradiction, policy version | Senior refund review | customer_policy | policy_ambiguity_005 |
| Refund service unavailable | Async case queue | Async case | 4 hours | medium | Tool error, checkpoint, unresolved request | Retry queue or callback | support_ops | dependency_failure_escalation_011 |
| Fraud or account takeover signal | Fraud operations | Specialist review | 5 minutes | urgent | Authentication state, risk flags, blocked actions | Block sensitive action and open urgent case | trust_safety | wrong_destination_fraud_012 |
