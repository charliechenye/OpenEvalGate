# Launch Readiness Report: Customer Support Refund Assistant

- **System name:** Customer Support Refund Assistant
- **Assistant type:** customer_support
- **Launch recommendation:** Conditional launch
- **Overall readiness score:** 79/100

## Passed Gates
- Scope gate: pass
- Golden eval gate: pass
- Model selection gate: pass
- Grounding gate: pass
- SOP/policy compilation gate: pass
- Output critic gate: pass
- Human escalation gate: pass
- Rollback gate: pass

## Failed Or Weak Gates
- Model arena gate: partial
- Tool/action safety gate: partial
- Input filter gate: partial
- Observability gate: partial
- Cost/latency gate: partial
- Drift monitoring gate: partial
- Owner signoff gate: partial

## Required Mitigations
- Model arena gate: Add a final latency run before rollout.
- Tool/action safety gate: Add service-level audit event for refund attempts.
- Input filter gate: Add prompt injection cases to eval set.
- Observability gate: Confirm dashboard owner and alert threshold.
- Cost/latency gate: Validate p95 latency under launch traffic.
- Drift monitoring gate: Schedule weekly review and owner rotation.
- Owner signoff gate: Complete final signoff after latency and observability evidence.

## Top Production Risks
- 1 eval case(s) marked high risk.
- 2 eval case(s) marked medium risk.
- High-risk actions require deterministic gates: issue_refund, issue_refund_without_policy_check.

## Suggested Next Actions
- Close mitigation for Model arena gate.
- Close mitigation for Tool/action safety gate.
- Close mitigation for Input filter gate.
- Close mitigation for Observability gate.
- Close mitigation for Cost/latency gate.
- Limit rollout to a controlled launch cohort with explicit rollback criteria.

## Checklist Summary
- Pass: 8
- Partial: 7
- Fail: 0
- Not applicable: 0

## Eval Set Summary
- Total cases: 3
- Case types: adversarial=1, historical_production=1, synthetic_boundary=1
- Risk tiers: high=1, medium=2
- Expected routes: escalate=2, revise=1

## Model Arena Summary
- Rows: 3
- Covered models: gpt-4.1-mini, claude-haiku-candidate, larger-frontier-model

## Action Risk Summary
- Rows: 4
- Covered actions: check_order_status, check_refund_eligibility, issue_refund, issue_refund_without_policy_check

## Output Critic Summary
- Rows: 5
- Covered dimensions: grounding, policy_alignment, helpfulness, action_safety, escalation_judgment
