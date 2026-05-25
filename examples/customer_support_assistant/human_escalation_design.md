# Human Escalation Design

| Escalation trigger | User-facing handoff message | Human task payload | Context passed to human | Priority level | SLA | Required human decision | Feedback returned to system | Eval case coverage | Monitoring metric |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Repeated refund history | I need to send this to a support specialist so we handle it correctly. | Review refund eligibility and abuse signal. | Order status, refund history, policy version, proposed response. | high | 15 minutes | approve refund / deny / request more info | decision reason and policy reference | refund_abuse_history_002 | escalation correctness |
| User explicitly asks for human on active complaint | I can connect this to a support specialist. | Continue case with full context. | User request, order state, prior bot turns. | medium | 15 minutes | resolve / follow up | outcome and issue category | angry_user_escalation_004 | repeat escalation |
| Self-harm or violence language | I am going to route this for urgent review. | Safety review handoff. | User text and minimal relevant account context. | urgent | immediate | safety handling decision | safety category only | self_harm_threat_007 | safety escalation latency |
| Policy ambiguity | I need a specialist to review the policy details before I answer. | Policy interpretation review. | Policy version and conflicting context. | medium | 1 business hour | policy answer / update policy | policy decision | policy_ambiguity_005 | policy ambiguity rate |
