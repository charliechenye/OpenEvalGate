# Education Integrity Queue Routing

| Escalation reason | Destination | Response model | SLA | Priority | Required payload | Fallback path | Owner | Eval coverage |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graded-work dispute | Instructor review | Async case | 1 business day | medium | Learner request, course ID, assessment type, policy boundary, proposed response | Course staff triage | course_staff | graded_dispute_escalation_003 |
| Learner safety or crisis concern | Learner safety review | Specialist review | 30 minutes | urgent | Minimal relevant learner message, course context, safety trigger | Campus support protocol | learner_safety | learner_safety_escalation_004 |
| Accommodation or policy ambiguity | Accessibility policy review | Specialist review | 2 business days | high | Learner request, course context, policy conflict, prior actions | Course staff triage | accessibility_services | accommodation_policy_ambiguity_005 |
