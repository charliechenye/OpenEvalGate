# Automation Boundary And Escalation

Over-automation is a production AI failure mode.

The right question is not "how much can we automate?" The better question is "where is automation appropriate, and where does it become risky?"

Human intervention is not failure; it is a control surface.

## Workflow Routes

For each workflow, define whether the assistant should:

- Resolve directly.
- Clarify.
- Recommend for human approval.
- Escalate immediately.
- Refuse or block.

## High-ROI Escalation Points

Escalation should be used where it protects users and the business:

- High ambiguity.
- High risk.
- Emotional intensity.
- Policy sensitivity.
- Business impact.
- Low model confidence.

## Automation Boundary Matrix

| Risk level | Confidence level | Action route |
| --- | --- | --- |
| Low | High | Automate |
| Low | Low | Clarify |
| Medium | High | Recommend / approval |
| Medium | Low | Escalate |
| High | High | Human approval |
| High | Low | Escalate / block |
| Prohibited | Any | Block |
