# AI Assistant PRD

**System name:**  
**Assistant type:**  
**Launch owner:**  
**Review date:**  

## Purpose

Describe the assistant's user-facing job in one paragraph. Focus on what the system is allowed to help users accomplish.

## Trust Preservation Thesis

Describe the user trust this assistant depends on, what could break that trust, and how launch gates bound the downside.

## Business Behavior Contract

Link to the business behavior contract that defines expected behavior, unacceptable behavior, compensation/action policy, escalation thresholds, and launch signoff owners.

## Supported Use Cases

| Use case | User intent | Success criteria | Required context | Owner |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

## Unsupported Use Cases

| Unsupported request | Required behavior | Escalation path | Policy reference |
| --- | --- | --- | --- |
|  |  |  |  |

## User Context

List the user, account, workflow, or entitlement fields required to answer safely.

## Grounding Sources

| Source | Freshness requirement | Retrieval rule | Known gaps |
| --- | --- | --- | --- |
|  |  |  |  |

## Tools And Actions

| Tool or action | Risk tier | Preconditions | Deterministic enforcement |
| --- | --- | --- | --- |
|  |  |  |  |

## Automation Boundary

Define when the assistant should automate, clarify, recommend for human approval, escalate, or block.

## Workflow And Capability Allocation

| Workflow or subagent | Job | Risk tier | Model assignment | Mandatory controls | Fallback | Owner |
| --- | --- | --- | --- | --- | --- | --- |
|  |  |  | fixed / adaptive / none |  |  |  |

Model capability does not replace authorization, deterministic enforcement, approval, escalation, or blocking.

## Input Filter Requirements

Define requests that should be accepted, refused, routed to human review, or blocked before generation.

## Output Critic Requirements

Define the criteria used to decide whether a proposed response can be shown, revised, escalated, or blocked.

## Metric Stack

Define efficiency, quality, journey, and business/trust metrics. Explain which metric could mislead the launch decision if viewed alone.

## Domain-Owner Feedback Loop

Define how business, operations, policy, trust/safety, or compliance owners can review traces, propose eval cases, approve behavior changes, and monitor drift.

## Launch Gates

Summarize the evidence required before this assistant can reach real users.
