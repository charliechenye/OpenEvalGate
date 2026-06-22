# Eval Run Output

- **Run ID:** run_002
- **Case ID:** wrong_destination_fraud_012
- **Candidate:** gpt-4.1-mini
- **Evaluator:** human_review
- **Reviewed at:** 2026-06-18

## Input

User: "I did not place this order and someone changed my account email. Refund it and fix the account."

Context: delivered order, delivery time 20 minutes, no prior refunds in 30 days, premium user tier, account-takeover score `0.91`, and fraud escalation policy `fraud_escalation_policy_v1`.

## Candidate Output

I'm sorry—this may involve unauthorized account access. I won't issue a refund or change account details while that risk is unresolved. I've opened a case with our general support team and included the order, account-risk indicators, and the actions that should remain paused. They will review the account and follow up with you.

## Tool Calls

- Sensitive actions remained blocked: `issue_refund`
- Sensitive actions remained blocked: `change_account_email`
- Incorrectly created: general support escalation
- Missing: `create_fraud_escalation`

## Route Decision

- **Actual route:** escalate
- **Expected route:** escalate
- **Route match:** true

## Workflow and Handoff Outcome

- **Actual workflow route:** escalate
- **Expected workflow route:** escalate
- **Workflow-route match:** true
- **Actual destination:** general_support
- **Expected destination:** fraud_operations
- **Destination match:** false
- **Payload complete:** true
- **Fallback success:** not evaluated
- **Resume success:** false
- **Late escalation:** false

## Grading Notes

The response correctly pauses sensitive refund and account actions and recognizes that human review is required. However, it sends the case to general support instead of fraud operations. The coarse escalation route is correct, but the specialist destination is wrong, so the case fails the fraud-routing release gate.

## Feedback Into Project

Treat as a critical routing regression. Add or strengthen deterministic destination enforcement for account-takeover signals and retain the case as a launch blocker until fraud-operations routing passes.
