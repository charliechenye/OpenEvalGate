# Human Escalation Design

## Escalation Paths

| Trigger | Path | Destination | Minimum payload | SLA | Fallback | Resume behavior | Eval case |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Refund or cancellation exception | approval | billing_approval_queue | Account, renewal, policy, proposed action | 30 minutes | billing_case_queue | Revalidate and execute one approved action | cancellation_exception_003 |
| Account-takeover signal | specialist routing | account_security_review | Risk signals, authentication, attempted actions | 5 minutes | lock_sensitive_actions | Resume after security decision and fresh verification | account_takeover_004 |

## Durable State

| Requirement | Status | Evidence |
| --- | --- | --- |
| Checkpoint before approval or handoff | pass | Billing workflow persists a checkpoint. |
| Idempotency prevents duplicate action | pass | Action key is tied to the checkpoint. |
| Minimum-sufficient context | pass | Payload contains only relevant account and policy context. |
| Reviewer decision recorded | pass | Approval and security queues require a decision. |
| Fallback destination observable | pass | Queue and lock events are monitored. |
| Versioned policy and workflow captured | pass | Audit event records policy, workflow, and model versions. |
