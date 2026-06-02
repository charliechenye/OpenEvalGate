# Human Escalation Design

## Boundary Summary

| Workflow | Resolve when | Clarify when | Escalate when | Approval required when | Refuse or block when | Owner |
| --- | --- | --- | --- | --- | --- | --- |
| Refund request | Order context is consistent, eligibility is routine, and action is within autonomous limits. | Order or intent is missing and one targeted question can recover it. | User asks for a human, order state conflicts, repeat contact appears, policy is ambiguous, or dependency fails. | Refund history, abuse signal, or compensation threshold requires senior review before action. | User asks to bypass rules, audit, or fraud controls. | support_ops |

## Escalation Paths

| Escalation trigger | Boundary path | Human destination | User-facing handoff message | Human task payload | Minimum context passed | Priority level | SLA | Fallback path | Required human decision | Resume behavior | Feedback returned to system | Eval case coverage | Monitoring metric |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Repeated refund history | approval | Senior refund review | I need to send this to a support specialist so we handle it correctly. | Review refund eligibility and abuse signal. | Order status, refund history, policy version, eligibility result, proposed decision. | high | 30 minutes | Hold action and notify user | approve refund / deny / request more info | Revalidate eligibility and execute exactly once from checkpoint | decision reason and policy reference | refund_abuse_history_002 | escalation correctness |
| User explicitly asks for human on active complaint | escalate | Live support or callback | I can connect this to a support specialist and pass along the context. | Continue case with full context. | User request, order state, prior bot turns, actions attempted. | medium | 15 minutes | Async case queue | resolve / follow up / reroute | Human owns conversation; agent records outcome | outcome and issue category | angry_user_escalation_004 | repeat escalation |
| Policy ambiguity or conflicting order state | escalate | Policy support review | I need a specialist to review the policy details before I answer. | Policy interpretation review. | Policy version, conflicting context, user impact, proposed next step. | medium | 1 business hour | Senior refund review | policy answer / update policy / reroute | Resume only after policy decision is captured | policy decision | policy_ambiguity_005 | policy ambiguity rate |
| Repeat contact after false containment | escalate | Live support or callback | Since this has already taken multiple attempts, I am going to route it with the prior context. | Resolve repeat-contact case. | Prior contacts, order state, failed resolution claim, user goal. | high | 15 minutes | Async case queue | resolve / follow up | Close only after durable outcome is recorded | resolution outcome and root cause | repeat_contact_010 | repeat contact by path |
| Refund eligibility service unavailable | escalate | Async case queue | I cannot safely complete this while the refund check is unavailable, so I will create a case with the current details. | Retry or manually review eligibility. | Tool error, checkpoint, order context, unresolved request. | medium | 4 hours | Callback queue | retry / manual decision | Retry from checkpoint with idempotency key | retry result and case outcome | dependency_failure_escalation_011 | fallback activation rate |
| Fraud or account-takeover signal | escalate | Fraud operations | I need to route this to a specialist team and keep sensitive actions paused. | Specialist fraud review. | Authentication state, risk flags, affected action, blocked tool call. | urgent | 5 minutes | Block sensitive action and open urgent case | confirm route / block / clear risk | Agent resumes only after risk decision | risk decision and allowed next step | wrong_destination_fraud_012 | correct destination rate |
| Routine order-status lookup | resolve | None |  | No human task. | Verified order and latest status only. | low |  |  | none | Complete in workflow | resolution outcome | routine_status_no_escalation_013 | over-escalation rate |

## Durable State And Audit

| Requirement | Status | Notes |
| --- | --- | --- |
| Workflow checkpoint is created before handoff or approval | pass | Refund workflow persists checkpoint before approval queue or async case. |
| Idempotency key prevents duplicate execution after resume | pass | Refund issue action requires idempotency key tied to checkpoint. |
| Handoff payload follows minimum-sufficient-context principle | pass | Payload excludes unrelated account data and includes policy/version context. |
| Reviewer identity and decision are recorded | pass | Senior review, policy review, and fraud routes require reviewer decision. |
| Timeout behavior is defined | partial | Senior review timeout is defined; live-support callback saturation needs load testing. |
| Fallback destination is observable | pass | Async queue and callback fallback emit route events. |
| Model, prompt, workflow, policy, and tool versions are captured | pass | Versions are captured in escalation audit events. |

## Launch Evidence

| Evidence | Linked artifact or case ID | Owner | Status |
| --- | --- | --- | --- |
| Under-escalation eval cases | refund_abuse_history_002, policy_ambiguity_005, wrong_destination_fraud_012 | support_ops | present |
| Over-escalation eval cases | routine_status_no_escalation_013 | ai_quality | present |
| Explicit human request case | angry_user_escalation_004 | support_ops | present |
| Approval-required action case | refund_abuse_history_002 | support_policy | present |
| Dependency failure or queue fallback case | dependency_failure_escalation_011 | platform | present |
| Human escalation gate in `launch_gate_review.md` | Human escalation gate | support_ops | pass |
