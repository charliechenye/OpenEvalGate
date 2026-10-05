# Human Escalation Incident Ingestion

**Human incident worksheet; the CLI does not read this file.**

Production failures should become durable eval cases, contract updates, or release-gate checks.

```text
Incident detected
      ↓
Reconstruct workflow trace
      ↓
Classify failure mode
      ↓
Identify contract gap
      ↓
Create or update eval case
      ↓
Update policy, routing, payload, or workflow state
      ↓
Run release gate
      ↓
Deploy with rollback
      ↓
Monitor affected slice
```

| Field | Notes |
| --- | --- |
| Incident ID |  |
| Workflow ID and version |  |
| Policy version |  |
| Model and prompt version |  |
| User impact |  |
| Business impact |  |
| First escalation signal |  |
| Actual boundary path |  |
| Expected boundary path |  |
| Destination selected |  |
| Expected destination |  |
| Handoff payload completeness |  |
| Queue and SLA outcome |  |
| Fallback activated? |  |
| Human decision |  |
| Review ID / action digest / checkpoint / policy binding |  |
| Callback disposition: rejected, edited, expired, late, duplicate, mismatched |  |
| All matched triggers, execution blocks, and specialist routes |  |
| Original operation identity and reconciliation result |  |
| Resume outcome |  |
| Root-cause category | prompt, model, policy, routing, data, tool, queue, payload, durable state, monitoring |
| New eval case required? |  |
| Contract update required? |  |
| Release gate update required? |  |
| Owner |  |
| Due date |  |

## Common Failure Modes

| Failure mode | Typical remediation |
| --- | --- |
| Under-escalation | Add deterministic trigger and eval slice. |
| Over-escalation | Tighten trigger and add routine-case release check. |
| Late escalation | Add retry budget or frustration override. |
| Wrong destination | Update routing contract and destination eval. |
| Payload gap | Extend schema and payload validation. |
| Queue failure | Add fallback path and alert. |
| Resume failure | Add checkpoint and idempotency control. |
| Approval replay or edit | Bind and consume current approval; test each callback state. |
| Unknown tool result | Reconcile the original operation before any retry. |
| Conflicting triggers | Preserve all execution blocks and necessary specialist routes. |
| Privacy overexposure | Enforce minimum-sufficient-context schema. |
| Observability gap | Add trace event and version capture. |
