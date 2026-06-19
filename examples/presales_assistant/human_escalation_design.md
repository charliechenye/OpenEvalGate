# Human Escalation Design

## Boundary Summary

| Workflow | Resolve when | Clarify when | Escalate when | Approval required when | Refuse or block when | Owner |
| --- | --- | --- | --- | --- | --- | --- |
| Presales commercial response | Answer is grounded in public product or pricing materials and makes no commitment. | Prospect need, segment, or deployment context is unclear. | Roadmap, discount, legal/security, or unsupported commitment needs owner review. | Response would create a pricing, contract, roadmap, or security commitment. | User asks the assistant to fabricate claims or approve a binding commitment. | sales_ops |

## Escalation Paths

| Escalation trigger | Boundary path | Human destination | User-facing handoff message | Human task payload | Minimum context passed | Priority level | SLA | Fallback path | Required human decision | Resume behavior | Feedback returned to system | Eval case coverage | Monitoring metric |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Roadmap or unsupported feature commitment | escalate | Account executive follow-up | I should connect you with sales so we do not overstate anything. | Prospect question and requested commitment. | Product context, account segment, requested term, approved collateral. | medium | 1 business day | Sales ops triage | approved response / follow-up / refuse commitment | Agent records sales outcome and avoids commitment until approved | decision and reason | unsupported_roadmap_claim_001 | sales acceptance |
| Discount or private pricing request | approval | Account executive follow-up | I can share public pricing, but a discount request needs sales review. | Pricing exception review. | Public pricing, requested discount, sales stage, account segment. | medium | 1 business day | Sales ops triage | approve offer / reject / request context | Agent sends only approved next step | offer decision and owner | public_pricing_question_002, discount_approval_boundary_004 | unauthorized discount rate |
| Legal, security, or compliance commitment | escalate | Legal/security review | I need the right specialist to review this before making any commitment. | Specialist review of requested commitment. | Prospect question, approved security materials, requested term, account context. | high | 2 business days | Sales ops triage | approved answer / legal follow-up / refuse claim | Agent resumes only with approved language | approved language and reviewer | legal_security_commitment_003 | unsupported commitment rate |

## Durable State And Audit

| Requirement | Status | Notes |
| --- | --- | --- |
| Workflow checkpoint is created before handoff or approval | pass | Follow-up case captures current conversation and prospect request. |
| Idempotency key prevents duplicate execution after resume | not_applicable | The assistant does not execute commercial commitments. |
| Handoff payload follows minimum-sufficient-context principle | pass | Payload includes requested commitment and current approved collateral only. |
| Reviewer identity and decision are recorded | partial | AE decisions are recorded; legal/security reviewer identity must be confirmed. |
| Timeout behavior is defined | partial | Sales follow-up SLA exists; legal/security timeout owner needs final signoff. |
| Fallback destination is observable | pass | Sales ops triage captures unrouted commitments. |
| Model, prompt, workflow, policy, and tool versions are captured | partial | Policy version is captured; prompt version needs release note linkage. |

## Launch Evidence

| Evidence | Linked artifact or case ID | Owner | Status |
| --- | --- | --- | --- |
| Under-escalation eval cases | unsupported_roadmap_claim_001, roadmap_commitment_semantic_009, legal_security_commitment_003, legal_security_semantic_010 | revenue_product | present |
| Over-escalation eval cases | approved_product_fact_005, public_pricing_answer_007 | ai_quality | present |
| Explicit human request case | sales follow-up handoff paths | sales_ops | present |
| Approval-required action case | public_pricing_question_002, discount_approval_boundary_004, discount_request_semantic_008 | sales_ops | present |
| Dependency failure or queue fallback case | sales ops triage fallback | sales_ops | planned |
| Human escalation gate in `launch_gate_review.md` | Human escalation gate | sales_ops | pass |
