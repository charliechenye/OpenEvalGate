# Subscription Support Assistant

> **Synthetic and illustrative example:** This repository-authored scenario is not an external production deployment. Its conversations, metrics, model outputs, policies, and reports are synthetic reference material.

This scenario shows how a subscription business can bound an assistant that answers billing questions, clarifies missing account context, pauses cancellation or refund actions for approval, escalates account-security concerns, and refuses requests to bypass verification.

It is the passing controlled-launch reference scenario. The package includes complete synthetic governance evidence, selected-run results, output artifacts, current-release comparison, and recency policy so the generated report demonstrates the intended evidence chain end to end.

## Customer Workflows

- Explain an invoice when account and billing context are verified.
- Ask one targeted clarification question when the subscription is ambiguous.
- Route cancellation or refund exceptions to approval before taking action.
- Escalate account-takeover or payment-risk signals to a specialist.
- Refuse requests to bypass authentication, billing policy, or audit controls.

## Reproduce

```bash
openevalgate validate examples/subscription_support_assistant/eval_cases.yaml
openevalgate check examples/subscription_support_assistant/
openevalgate report examples/subscription_support_assistant/ \
  --output examples/subscription_support_assistant/generated_launch_report.md
```

The passing recommendation is bounded to this synthetic evidence package. It is not a production deployment approval or external validation claim.
