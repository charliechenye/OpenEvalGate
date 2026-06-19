# Customer Support Refund Assistant

**Assistant type:** customer_support
**Launch owner:** AI Product Team
**Review date:** 2026-05-23

## Purpose

Help customers understand order status, refund eligibility, and next steps without promising compensation that policy or account state does not support.

## Supported Use Cases

| Use case | User intent | Success criteria | Required context | Owner |
| --- | --- | --- | --- | --- |
| Refund eligibility | User wants a refund or credit. | Assistant checks policy and eligibility before promising compensation. | Order status, delivery time, refund history, policy version. | AI Product Team |
| Order status | User asks where an order is. | Assistant gives grounded status and next step. | Order status and fulfillment events. | Support Ops |
| Escalation | User case is ambiguous or high impact. | Assistant routes to human support with clear context. | User request, account state, failed gate. | Support Ops |

## Unsupported Use Cases

| Unsupported request | Required behavior | Escalation path | Policy reference |
| --- | --- | --- | --- |
| Guaranteed refund without eligibility check | Explain that eligibility must be checked first. | Escalate if user disputes. | refund_policy_us_v3 |
| Merchant blame or unverified fault | Avoid assigning blame without evidence. | Escalate if safety or fraud concern exists. | support_tone_v2 |
| Manual override of refund limits | Refuse automation and escalate. | Human support manager. | refund_policy_us_v3 |

## Tools And Actions

| Tool or action | Risk tier | Preconditions | Deterministic enforcement |
| --- | --- | --- | --- |
| check_order_status | low | Authenticated user and valid order ID. | Auth and ownership check. |
| check_refund_eligibility | medium | Delivered order and current refund policy. | Refund eligibility service. |
| issue_refund | high | Eligibility pass and human approval for boundary cases. | Refund service policy gate. |

## Workflow And Capability Allocation

| Workflow or subagent | Job | Risk tier | Model assignment | Mandatory controls | Fallback | Owner |
| --- | --- | --- | --- | --- | --- | --- |
| Order status specialist | Grounded delivery status | low | fixed: gpt-4.1-mini | Authentication, ownership, carrier grounding | Human support | Support Ops |
| Refund resolution specialist | Resolve eligible refunds and explain outcomes | high | adaptive: gpt-4.1-mini or approved frontier model | Eligibility service, policy version, idempotency | Human support | Support Ops |
| Policy refusal | Block bypass attempts | prohibited | none: deterministic | Hard policy block and audit event | Human support | Trust and Safety |
| Fraud and safety review | Handle specialist-risk signals | high | none: human workflow | Sensitive-action block and urgent routing | Human support | Trust and Safety |

## Output Critic Requirements

The output critic must block policy-inconsistent compensation, revise unsupported factual claims, and escalate ambiguous boundary cases.
