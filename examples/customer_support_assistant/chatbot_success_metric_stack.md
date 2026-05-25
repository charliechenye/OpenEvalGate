# Chatbot Success Metric Stack

## Efficiency Metrics

| Metric | Target | Owner | Review cadence |
| --- | --- | --- | --- |
| Containment | Monitor only | Product | weekly |
| Automation rate | Below unsafe escalation threshold | Product | weekly |
| Cost per interaction | Within launch target | Engineering | weekly |

## Quality Metrics

| Metric | Target | Owner | Review cadence |
| --- | --- | --- | --- |
| Golden eval pass rate | >= 90% | AI Quality | each release |
| Output critic pass rate | >= 95% for shown responses | AI Quality | weekly |
| Escalation correctness | >= 95% on high-risk cases | Support Operations | weekly |
| Policy alignment | No P0 policy failures | Customer Policy | each release |

## Journey Metrics

| Metric | Target | Owner | Review cadence |
| --- | --- | --- | --- |
| True resolution | Improve without recontact increase | Support Operations | weekly |
| Recontact rate | No increase after launch | Support Operations | weekly |
| Repeat escalation | No increase for refund cases | Support Operations | weekly |
| Time to durable resolution | Improve or hold flat | Product | weekly |
| Bypass attempts | Monitor for increase | Trust/Safety | weekly |

## Business / Trust Metrics

| Metric | Target | Owner | Review cadence |
| --- | --- | --- | --- |
| Complaint rate | No increase | Support Operations | weekly |
| Trust/sentiment | No decline in refund journeys | Product | weekly |
| Compensation leakage | No increase | Finance Operations | weekly |
| Downstream support cost | Decrease without recontact increase | Support Operations | monthly |

## Anti-Metrics / Warning Signs

- High containment + high recontact.
- Low escalation + rising complaints.
- High bot CSAT but lower durable resolution.
- High output critic pass rate but poor journey resolution.
- Reduced human contacts but higher complaint rate.

## Launch Gate Use

If containment rises while recontact or complaints rise, the launch gate should fail even if short-term automation metrics improve.
