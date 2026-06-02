# Human Escalation Design

Use this required project artifact to define where human judgment, authority, specialist handling, or approval enters the workflow. Keep it narrow enough that product, engineering, operations, and risk owners can review it in a launch meeting.

## Boundary Summary

| Workflow | Resolve when | Clarify when | Escalate when | Approval required when | Refuse or block when | Owner |
| --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |

## Escalation Paths

| Escalation trigger | Boundary path | Human destination | User-facing handoff message | Human task payload | Minimum context passed | Priority level | SLA | Fallback path | Required human decision | Resume behavior | Feedback returned to system | Eval case coverage | Monitoring metric |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| High-risk action request | approval | Specialist approval queue | I need to send this to a specialist so we handle it correctly. | User request, relevant context, failed gate, proposed action | Policy version, account or workflow state, risk tier, escalation reason | high | 15 minutes | Hold action and notify user | approve / reject / request more info | Revalidate and resume from checkpoint | decision, reason, reviewer, policy reference |  | escalation correctness |

## Durable State And Audit

| Requirement | Status | Notes |
| --- | --- | --- |
| Workflow checkpoint is created before handoff or approval |  |  |
| Idempotency key prevents duplicate execution after resume |  |  |
| Handoff payload follows minimum-sufficient-context principle |  |  |
| Reviewer identity and decision are recorded |  |  |
| Timeout behavior is defined |  |  |
| Fallback destination is observable |  |  |
| Model, prompt, workflow, policy, and tool versions are captured |  |  |

## Launch Evidence

| Evidence | Linked artifact or case ID | Owner | Status |
| --- | --- | --- | --- |
| Under-escalation eval cases |  |  |  |
| Over-escalation eval cases |  |  |  |
| Explicit human request case |  |  |  |
| Approval-required action case |  |  |  |
| Dependency failure or queue fallback case |  |  |  |
| Human escalation gate in `launch_gate_review.md` |  |  |  |
