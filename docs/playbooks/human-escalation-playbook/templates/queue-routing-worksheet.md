# Queue Routing Worksheet

Use this worksheet to prove the human system on the other side of the agent is real, owned, and observable.

| Escalation reason | Destination | Response model | SLA | Priority | Required payload | Fallback path | Owner | Eval coverage |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Repeated failed attempts | Live support or callback | Immediate or prioritized |  |  | Transcript summary, prior attempts, workflow state | Async case queue |  |  |
| High-value exception | Senior approval queue | Bounded reviewer decision |  |  | Eligibility result, requested action, policy version | Hold action and notify user |  |  |
| Specialist risk signal | Specialist operations | Urgent specialist handling |  |  | Authentication state, risk flags, affected actions | Block sensitive action and open urgent case |  |  |
| Dependency failure | Async case queue | Visible response-time commitment |  |  | Tool error, workflow checkpoint, unresolved request | Retry queue or callback |  |  |
| Policy gray area | Policy-owner review | Bounded expert decision |  |  | Ambiguous rule, workflow state, user impact | Senior review |  |  |

## Capacity Prompts

- What is expected daily escalation volume by route?
- What is peak-hour escalation volume?
- Which routes require live coverage?
- Which routes can operate asynchronously?
- Which routes require on-call coverage?
- What happens during queue saturation?
- Can the system offer a callback or visible response-time promise?
- Which routes require language, regional, policy, safety, legal, fraud, or senior-review expertise?
- Which queues need escalation-to-escalation behavior?
