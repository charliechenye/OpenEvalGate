# Automation Boundary Matrix

| Risk level | Confidence level | Action route | Examples | Required controls | Human role | Eval coverage |
| --- | --- | --- | --- | --- | --- | --- |
| Low | High | automate | Simple status lookup | Auth and ownership check | None | Regression eval |
| Low | Low | clarify | Ambiguous user intent | Clarifying question | None | Boundary eval |
| Medium | High | recommend | Refund eligibility recommendation | Policy service check | Approve exceptions | Historical eval |
| Medium | Low | escalate | Conflicting account and policy context | Escalation trigger | Decide outcome | Boundary eval |
| High | High | human approval | Financial compensation | Deterministic eligibility and audit | Approve or reject | P0 eval |
| High | Low | escalate | Angry user with policy ambiguity | Escalation trigger | Handle case | P0 eval |
| Prohibited | Any | block | Unauthorized account mutation | Hard block | Review incident if needed | Adversarial eval |
