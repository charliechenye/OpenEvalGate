# Stakeholder Alignment Brief

Use this before writing eval cases. The goal is to align the team on expected behavior, unacceptable behavior, tool boundaries, policy sources, risk, and launch authority.

## Product Use Case

Describe the assistant or agent and the user problem it solves.

## Stakeholders

| Area | Owner | Role in eval set |
| --- | --- | --- |
| Product |  | Defines expected behavior and launch tradeoffs |
| Engineering / AI platform |  | Owns eval execution and trace evidence |
| Operations / support |  | Provides production failure modes and escalation realities |
| Policy / legal / risk |  | Defines boundaries, prohibited behavior, and high-risk cases |
| Domain experts |  | Adjudicate specialized workflow behavior |
| Analytics |  | Defines slices, drift signals, and metric monitoring |

## In-Scope Intents

- 

## Out-Of-Scope Intents

- 

## Allowed Behaviors

- Answer from grounded context.
- Ask clarifying questions.
- Escalate to a human or domain owner.
- Refuse unsupported or unsafe requests.
- Call approved tools only when eligibility is established.

## Prohibited Behaviors

- 

## Tools And Actions

| Tool/action | Read or write | Eligibility requirement | Confirmation required | Human review required |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

## Policy Sources Of Truth

- 

## High-Risk Scenarios

- 

## Launch Blockers

- 

## Decision Owners

| Decision | Owner |
| --- | --- |
| Expected behavior |  |
| Policy interpretation |  |
| Eval infrastructure |  |
| Production failure review |  |
| Release decision |  |
