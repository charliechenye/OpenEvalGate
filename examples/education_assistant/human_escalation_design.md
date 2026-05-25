# Human Escalation Design

| Escalation trigger | User-facing handoff message | Human task payload | Context passed to human | Priority level | SLA | Required human decision | Feedback returned to system | Eval case coverage | Monitoring metric |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graded-work dispute | I need to route this to course staff so we respect the learning policy. | Learner request and course context | Course ID, assessment type, proposed response | medium | 1 business day | allow hint / refuse / clarify | decision and reason | graded_answer_request_001 | escalation correctness |
