# Human Escalation Design

| Escalation trigger | User-facing handoff message | Human task payload | Context passed to human | Priority level | SLA | Required human decision | Feedback returned to system | Eval case coverage | Monitoring metric |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Roadmap or discount commitment | I should connect you with sales so we do not overstate anything. | Prospect question and requested commitment | Product context, account segment, requested term | medium | 1 business day | approved response / follow-up / refuse commitment | decision and reason | unsupported_roadmap_claim_001 | sales acceptance |
