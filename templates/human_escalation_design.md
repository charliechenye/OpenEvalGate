# Human Escalation Design

| Escalation trigger | User-facing handoff message | Human task payload | Context passed to human | Priority level | SLA | Required human decision | Feedback returned to system | Eval case coverage | Monitoring metric |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| High-risk action request | I need to send this to a specialist so we handle it correctly. | User request, relevant context, failed gate | Policy version, account state, proposed route | high | 15 minutes | approve / reject / request more info | decision and reason |  | escalation correctness |
