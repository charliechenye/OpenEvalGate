# Human Escalation Rubric

## Escalate Immediately

- User asks for a prohibited action.
- User request requires policy interpretation beyond compiled context.
- User context conflicts with retrieved policy or account state.
- The assistant cannot determine eligibility for a financial, legal, medical, educational, or account-impacting outcome.
- The output critic marks grounding, policy alignment, or action safety as failed.

## Handoff Payload

| Field | Required | Notes |
| --- | --- | --- |
| User request | yes | Original user input. |
| User context | yes | Only fields needed for review. |
| Retrieved context | yes | Policy, account, or knowledge snippets used. |
| Proposed response | no | Include if generated before escalation. |
| Failed gate | yes | Input filter, output critic, tool gate, or policy gate. |
| Risk tier | yes | low, medium, high, or prohibited. |

## Review SLA

Define expected review time by risk tier and user impact.
