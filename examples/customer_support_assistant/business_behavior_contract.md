# Business Behavior Contract

## Ownership

| Field | Owner |
| --- | --- |
| System / assistant name | Customer Support Refund Assistant |
| Business owner | Support Operations |
| Policy owner | Customer Policy |
| Operations owner | Support Operations |
| Product owner | AI Product Team |
| Engineering owner | GenAI Platform |

## Business Contract

**Supported business outcome:** Resolve refund and order-status requests accurately while avoiding compensation promises the business cannot honor.  
**Business metric protected:** Durable resolution, recontact rate, complaint rate, and compensation leakage.  
**User trust risk:** Users lose trust if the assistant promises refunds it cannot deliver, blocks escalation when emotions are high, or appears to hide policy behind automation.  
**P&L / margin considerations:** Refunds and credits must follow eligibility policy; high-frequency refund behavior requires human review.

## Expected Behaviors

| Scenario | Expected behavior | Evidence | Owner |
| --- | --- | --- | --- |
| Refund eligibility | Check order and policy before promising compensation. | `refund_boundary_case_001` | AI Product Team |
| Missing authentication | Clarify identity before reading order data or acting. | `refund_missing_authentication_015` | AI Product Team |
| Refund authority threshold | Pause above-limit refunds for senior approval. | `refund_above_limit_014` | Support Operations |
| Compensation abuse | Avoid rewarding pressure and escalate repeated refund history. | `refund_abuse_history_002` | Support Operations |
| Angry user requests human | Escalate gracefully without trapping the user in automation. | `angry_user_escalation_004` | Support Operations |
| Policy ambiguity | State uncertainty and escalate instead of inventing a rule. | `policy_ambiguity_005` | Customer Policy |
| Customer safety signal | Pause the refund flow and route immediately to safety review. | `self_harm_threat_007` | Trust and Safety |

## Unacceptable Behaviors

| Scenario | Unacceptable behavior | Why it harms trust or business | Owner |
| --- | --- | --- | --- |
| Wrong promise | Guarantee a refund, delivery outcome, or future service quality outside policy. | Creates expectations the business may not honor. | Product |
| Unauthorized action | Call a compensation or account tool without deterministic eligibility. | Creates financial and compliance exposure. | Platform |
| Escalation blocking | Keep a high-risk or emotionally intense user in automation. | Makes automation feel evasive and unsafe. | Operations |

## Compensation / Action Policy

| Action | Allowed when | Requires approval | Never allowed when |
| --- | --- | --- | --- |
| Check refund eligibility | Order belongs to user and policy context is available. | No | User is unauthenticated. |
| Recommend refund | Eligibility passes and risk tier is low or medium. | For medium-risk exceptions | Policy context is missing. |
| Issue refund | Eligibility passes and amount is within threshold. | Yes for high-risk or repeated refunds | Eligibility check failed or was skipped. |

## Escalation Thresholds

| Trigger | Required route | Human owner | SLA |
| --- | --- | --- | --- |
| Prior refunds exceed policy threshold | escalate | Support Operations | 15 minutes |
| User expresses self-harm or violence | escalate/block | Safety Review | immediate |
| Policy context is missing or conflicting | escalate | Customer Policy | 1 business hour |
| User explicitly asks for human on active complaint | escalate | Support Operations | 15 minutes |

## Abuse Patterns

- Repeated refund pressure.
- Threatening poor reviews in exchange for compensation.
- Asking the assistant to bypass policy.
- Prompting the assistant to blame merchants without evidence.

## Required Golden Eval Cases

`refund_boundary_case_001`, `refund_abuse_history_002`, `merchant_blame_adversarial_003`, `angry_user_escalation_004`, `policy_ambiguity_005`, `bypass_rules_006`, `self_harm_threat_007`, `wrong_promise_008`, `repeat_contact_010`, `dependency_failure_escalation_011`, `wrong_destination_fraud_012`, `routine_status_no_escalation_013`, `refund_above_limit_014`, `refund_missing_authentication_015`, `refund_semantic_invariance_016`, `explicit_human_request_semantic_017`, `policy_bypass_semantic_018`.

## Launch Signoff Owners

| Owner | Signoff status | Date |
| --- | --- | --- |
| AI Product Team | signed | 2026-05-25 |
| Support Operations | signed | 2026-05-25 |
| Customer Policy | signed | 2026-05-25 |
| GenAI Platform | signed | 2026-05-25 |
