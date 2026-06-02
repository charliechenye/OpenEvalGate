# Fallback And Durable State Checklist

## Fallback Planning

| Failure condition | Detection signal | User experience | System behavior | Fallback destination | State preserved? | Owner |
| --- | --- | --- | --- | --- | --- | --- |
| Live queue full | Queue-depth threshold | Offer callback or async case | Preserve transcript and state packet |  |  |  |
| SLA exceeded | Timer event | Notify user of delay | Escalate priority or reroute |  |  |  |
| Reviewer does not respond | Approval timeout | Explain pending status | Keep action paused; open case |  |  |  |
| Callback fails | Contact failure | Confirm contact channel | Convert to async case |  |  |  |
| Specialist team unavailable | Route-health signal | Provide visible next step | Keep sensitive action blocked |  |  |  |
| Tool dependency degraded | Circuit breaker | Communicate delay | Persist checkpoint; retry asynchronously |  |  |  |
| Handoff payload creation fails | Schema or storage error | Avoid silent drop | Log incident; create minimal case record |  |  |  |

## Durable State Checklist

| Capability | Required behavior | Pass / fail | Notes |
| --- | --- | --- | --- |
| Workflow checkpointing | Persist current workflow state before handoff or approval. |  |  |
| Idempotency | Prevent duplicate execution after resume or retry. |  |  |
| Correlation ID | Tie conversation, workflow, tool calls, and human review together. |  |  |
| Explicit status model | Represent pending_review, escalated, approved, rejected, timed_out, resumed, and closed. |  |  |
| Reviewer identity | Record who approved, edited, rejected, or rerouted the case. |  |  |
| Timeout behavior | Define what happens when no reviewer responds. |  |  |
| Resume behavior | Continue from the last safe checkpoint. |  |  |
| Revalidation | Re-check policy, context freshness, and authorization before execution. |  |  |
| Audit history | Preserve state transitions and decision history. |  |  |
| Data minimization | Transfer only minimum sufficient context. |  |  |
| Version capture | Record model, prompt, policy, workflow, and tool versions. |  |  |
| Failure recovery | Recover from partial handoff, queue, and persistence failures. |  |  |
