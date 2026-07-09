# Launch Gate Review

| Gate | Status | Evidence | Required mitigation | Owner |
| --- | --- | --- | --- | --- |
| Scope gate | pass | PRD defines billing, cancellation, refund, and security boundaries. | None | subscriber_experience |
| Trust preservation gate | pass | Contract defines false promises, unauthorized actions, and safe stopping boundaries. | None | trust_safety |
| Business behavior contract gate | pass | Business contract has cross-functional signoff. | None | subscription_operations |
| Golden eval gate | pass | Five cases cover answer, clarify, approval, escalation, and refusal. | None | ai_quality |
| Tail-risk / P0 failure mode gate | pass | Checklist covers unauthorized payment, unapproved refund, and missed takeover escalation. | None | trust_safety |
| Model selection gate | pass | Candidate selected from the synthetic arena scorecard. | None | ml_engineering |
| Model arena gate | pass | Candidate comparison includes quality, safety, latency, and cost. | None | ml_engineering |
| Routing / capability allocation gate | pass | Versioned policy maps each case to a bounded workflow. | None | account_platform |
| Grounding gate | pass | Billing and security policies are versioned inputs. | None | billing_policy |
| SOP/policy compilation gate | pass | Action and approval rules are compiled before response generation. | None | billing_policy |
| Tool/action safety gate | pass | High-risk actions require approval and prohibited actions are blocked. | None | account_platform |
| Automation boundary gate | pass | Boundary matrix defines answer, clarify, approval, escalate, and block. | None | subscriber_experience |
| Human escalation gate | pass | Billing and security destinations include payload, SLA, fallback, and resume rules. | None | operations |
| Input filter gate | pass | Authentication bypass and security signals are covered. | None | trust_safety |
| Output critic gate | pass | Rubric covers grounding, policy, action safety, and escalation. | None | ai_quality |
| Domain-owner feedback loop gate | pass | Subscription Operations owns review and policy updates. | None | subscription_operations |
| Observability gate | pass | Trace, approval, security, and action events are defined. | None | platform |
| Cost/latency gate | pass | Candidate remains within synthetic launch targets. | None | engineering |
| Journey metric / durable resolution gate | pass | Recontact and durable-resolution metrics are defined. | None | subscription_operations |
| Business trust metric gate | pass | Billing complaints and unauthorized-action metrics are defined. | None | subscription_operations |
| Drift monitoring gate | pass | Weekly billing and security drift review is assigned. | None | ai_quality |
| Rollback gate | pass | Account Platform can pause sensitive workflows and revert routing. | None | account_platform |
| Owner signoff gate | pass | Business, policy, product, platform, and risk owners signed off. | None | subscription_operations |
