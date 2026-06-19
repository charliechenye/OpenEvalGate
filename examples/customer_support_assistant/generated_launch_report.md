# Launch Readiness Report: Customer Support Refund Assistant

## Executive Summary
- **System name:** Customer Support Refund Assistant
- **Assistant type:** customer_support
- **Overall readiness score:** 90/100
- **Recommendation:** Not ready
- **Launch blocker status:** 1 hard blocker(s) require remediation.

## Overall Readiness Score
90/100

## Recommendation
Not ready

## Hard Blockers
- **critical_escalation_regression:** High-risk escalation evidence contains under-escalation, wrong-destination, payload, or resume failures. Evidence: refund_abuse_history_002, wrong_destination_fraud_012

## Trust Preservation Summary
- Trust preservation review is present.

## Business Behavior Contract Summary
- Business behavior contract is present.

## Golden Eval Summary
- Total cases: 17
- Case types: adversarial=2, fresh_drift_sample=1, historical_production=2, regression=1, synthetic_boundary=11
- Risk tiers: high=5, low=1, medium=9, prohibited=2
- Expected admission routes: block=2, escalate=9, revise=3, show=3
- Boundary metadata coverage: 14/17 cases across 8 contrast family/families
- Expected workflow routes: act=2, answer=2, approval=2, clarify=1, escalate=7, refuse=2

## Tail-Risk / P0 Failure Mode Summary
- P0 failure mode checklist is present.

## Automation Boundary Summary
- Automation boundary matrix is present with 12 row(s).

## Human Escalation Summary
- Human escalation design is present with 25 row(s).
- Structured escalation contract: valid.
- Workflow: refund_request
- Triggers: 9
- Destinations: 6 (senior_refund_review, live_support_or_callback, policy_support_review, async_case_queue, fraud_operations, safety_review)
- Handoff types: approval, async_case, conversation_handoff, specialist_routing
- Destination SLA coverage: 100%
- Destination fallback coverage: 100%
- Checkpoint required: yes
- Idempotency required: yes
- Resume behavior defined: yes
- Required eval slices: 14
- Eval handoff coverage: 9/9 required-handoff cases

## Tool/Action Safety Summary
- Rows: 7
- Risk tiers: high=2, low=1, medium=2, prohibited=2
- High/prohibited actions: issue_refund, issue_refund_without_policy_check, create_safety_escalation, close_case_without_resolution

## Input/Output Perimeter Summary
- Input filter gate evidence is in launch_gate_review.md.
- Rows: 5
- Covered dimensions: grounding, policy_alignment, helpfulness, action_safety, escalation_judgment

## Model Arena Summary
- Rows: 3
- Covered models: gpt-4.1-mini, claude-haiku-candidate, larger-frontier-model

## Metric Stack Summary
- Chatbot success metric stack is present.

## Domain-Owner Feedback Loop Summary
- Domain-owner feedback loop evidence is present.

## Observability / Rollback Summary
- Observability gate: partial
- Drift monitoring gate: partial
- Rollback gate: pass

## Eval Results Summary
- Total result rows: 6
- Latest run ID: run_002
- Candidate coverage: gpt-4.1-mini
- Pass rate: 33%
- Route match rate: 50%
- Failed case IDs: refund_abuse_history_002, refund_boundary_case_001, routine_status_no_escalation_013, wrong_destination_fraud_012
- Top failure categories: over_escalation=2, under_escalation=1, wrong_destination=1
- Workflow-route accuracy: 50%
- Trajectory pass rate: 50%
- End-state pass rate: 33%
- Prohibited-action rate: 0%
- Contrast-family reliability: 33% (3/8 families have complete result coverage)
- Semantic stability: unknown
- Repeated-run reliability: unknown (0 repeatedly evaluated case(s))
- Required-escalation recall: 67%
- Over-escalation rate: 67%
- Destination accuracy: 33%
- Context-preservation rate: 67%
- Fallback success rate: 100%
- Resume success rate: 33%
- Late-escalation rate: 33%
- Observed output paths: eval_runs/run_001/refund_boundary_case_001.md, eval_runs/run_001/refund_abuse_history_002.md, eval_runs/run_001/merchant_blame_adversarial_003.md, eval_runs/run_002/dependency_failure_escalation_011.md, eval_runs/run_002/wrong_destination_fraud_012.md, eval_runs/run_002/routine_status_no_escalation_013.md

## Required Mitigations
- Launch blocker: High-risk escalation evidence contains under-escalation, wrong-destination, payload, or resume failures.
- Model arena gate: Add a final latency run before rollout.
- Input filter gate: Add prompt injection cases to eval set.
- Observability gate: Confirm dashboard owner and alert threshold.
- Cost/latency gate: Validate p95 latency under launch traffic.
- Drift monitoring gate: Schedule weekly review and owner rotation.

## Suggested Next Actions
- Resolve hard blockers before any user-facing launch.
- Close mitigation for Model arena gate.
- Close mitigation for Input filter gate.
- Close mitigation for Observability gate.
- Close mitigation for Cost/latency gate.
- Close mitigation for Drift monitoring gate.

## Final Launch Recommendation
Not ready. Do not launch until hard blockers are resolved.
