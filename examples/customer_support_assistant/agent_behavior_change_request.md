# Agent Behavior Change Request

| Field | Value |
| --- | --- |
| Change request ID | cs-refund-escalation-001 |
| Requested by | Support Operations |
| Business/domain owner | Support Operations |
| Current behavior | Candidate assistant may stay in `show` route for repeated refund-history cases. |
| Desired behavior | Route repeated refund-history cases to human support before compensation language. |
| Reason for change | Repeated refund history is a high-risk boundary case with abuse and trust implications. |
| User/customer evidence | Synthetic eval failure `refund_abuse_history_002` and support escalation review. |
| Policy evidence | `refund_policy_us_v3` repeated refund threshold. |
| Golden eval cases to add/update | `refund_abuse_history_002`, `overcompensation_abuse_009` |
| Risk tier | high |
| Impacted intents | refund_eligibility, compensation_policy |
| Impacted tools/actions | check_refund_eligibility, issue_refund |
| Required approval | Support Operations, Customer Policy, GenAI Platform |
| Rollback plan | Disable refund recommendation route and escalate refund requests to human queue. |
| Launch gate impact | Tool/action safety, automation boundary, human escalation, tail-risk/P0 failure mode |
| Monitoring plan | Track escalation correctness, refund leakage, recontact, and complaint rate. |
