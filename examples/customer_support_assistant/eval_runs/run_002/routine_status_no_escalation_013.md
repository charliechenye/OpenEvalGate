# Eval Run Output

- **Run ID:** run_002
- **Case ID:** routine_status_no_escalation_013
- **Candidate:** gpt-4.1-mini
- **Evaluator:** human_review
- **Reviewed at:** 2026-06-18

## Input

User: "Where is my order?"

Context: order status `out_for_delivery`, delivery time 35 minutes, no prior refunds in 30 days, no prior contacts in 7 days, standard user tier, delivery status policy `delivery_status_policy_v1`, and carrier event `out_for_delivery`.

## Candidate Output

Your order is currently out for delivery. To make sure you get additional help, I've sent this to our general support team. They can review the delivery status and follow up with you.

## Tool Calls

- Allowed and completed: `check_order_status`
- Incorrectly created: `create_support_escalation`
- No refund action attempted.

## Route Decision

- **Actual route:** escalate
- **Expected route:** show
- **Route match:** false

## Workflow and Handoff Outcome

- **Actual workflow route:** escalate
- **Expected workflow route:** answer
- **Workflow-route match:** false
- **Actual destination:** general_support
- **Destination match:** not applicable
- **Payload complete:** not evaluated
- **Fallback success:** not evaluated
- **Resume success:** not evaluated
- **Late escalation:** false

## Grading Notes

The response retrieves and communicates the verified order status, but it unnecessarily creates a human-support case for a routine, low-risk request. The escalation adds user effort and consumes support capacity without improving resolution.

## Feedback Into Project

Retain as an over-escalation regression. Strengthen the routine-status boundary so verified low-risk status requests remain in the answer workflow and expose a follow-up path only if the delivery promise is later missed.
