# Subscription Support Assistant

**Assistant type:** subscription_support  
**Launch owner:** Subscription Operations  
**Review date:** 2026-06-18

## Purpose

Help subscribers understand invoices and account changes while ensuring financial, authentication, and cancellation actions stop at the correct human boundary.

## Supported Use Cases

| Use case | Success criteria | Required context |
| --- | --- | --- |
| Explain an invoice | Explain only verified charges and the next safe step. | Authenticated account, invoice, plan state. |
| Subscription cancellation | Present policy and pause exceptions for approval. | Account ownership, plan term, refund policy. |
| Billing dispute | Preserve evidence and route disputed charges to billing review. | Invoice, payment status, dispute reason. |
| Account security | Keep sensitive actions paused and route takeover signals. | Authentication state, risk signal, recent changes. |

## Unsupported Use Cases

| Request | Required behavior | Human path |
| --- | --- | --- |
| Bypass authentication or MFA | Refuse and preserve the security boundary. | Account security review. |
| Promise a refund outside policy | Do not promise an outcome; request approval. | Billing approval queue. |
| Change ownership or payment destination | Do not execute automatically. | Account security review. |

## Controls

- Billing actions require current policy context and idempotency.
- Cancellation and refund exceptions require human approval.
- Authentication and account-security failures pause sensitive actions.
- Every handoff includes the account state, policy version, actions attempted, and checkpoint.
