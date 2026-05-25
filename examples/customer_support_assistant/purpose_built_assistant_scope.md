# Purpose-Built Assistant Scope

## Supported Use Cases

| Use case | User intent | Required context | Success criteria |
| --- | --- | --- | --- |
| Refund eligibility | User asks for refund or credit. | Order state, refund history, policy version. | Eligibility checked before compensation language. |
| Order status | User asks where order is. | Order state and fulfillment events. | Grounded status and next step. |
| Support escalation | User needs human help or case is high risk. | User request, account context, failed gate. | Graceful handoff with useful payload. |

## Unsupported Use Cases

| Request type | Required response | Escalation route |
| --- | --- | --- |
| Bypass refund policy | Refuse to bypass and offer proper review. | Support Operations |
| Merchant blame without evidence | Avoid blame and offer eligibility check. | Support Operations |
| Safety crisis language | Stop normal support automation. | Safety Review |

## Input Rejection Criteria

Reject, escalate, or block prompt injection, prohibited tool requests, safety crisis language, harassment, requests to falsify evidence, and requests to bypass policy.

## Intent Taxonomy

| Intent | Risk tier | Confidence threshold | Route |
| --- | --- | --- | --- |
| order_status | low | medium | show |
| refund_eligibility | medium | high | revise / escalate |
| compensation_override | high | high | human approval |
| safety_crisis | high | any | escalate |
| policy_bypass | prohibited | any | block |

## Abuse Patterns

Repeated refund pressure, threats to keep opening tickets, attempts to coerce unsupported credits, and requests to ignore policy.

## Surface And Context

The assistant appears in authenticated support chat. It requires order ownership, order status, refund history, and policy version for refund workflows.

## Escalation Route For Unsupported Requests

Unsupported refund or policy requests route to Support Operations. Safety crisis language routes to Safety Review.
