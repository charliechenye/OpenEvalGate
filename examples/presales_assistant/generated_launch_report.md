# Launch Readiness Report: Presales Product Advisor

## Executive Summary
- **System name:** Presales Product Advisor
- **Assistant type:** presales
- **Overall readiness score:** 40/100
- **Recommendation:** Not ready
- **Launch blocker status:** 4 hard blocker(s) require remediation.

## Overall Readiness Score
40/100

## Recommendation
Not ready

## Hard Blockers
- **missing_tail_risk_review:** High-impact workflows lack passing tail-risk/P0 review. Evidence: p0_failure_mode_checklist.md or Tail-risk / P0 gate
- **critical_escalation_regression:** High-risk escalation evidence contains under-escalation, wrong-destination, payload, or resume failures. Evidence: legal_security_commitment_003
- **missing_rollback:** Rollback gate is missing or not passing. Evidence: Rollback gate
- **missing_owner_signoff:** Owner signoff gate is missing or not passing. Evidence: Owner signoff gate

## Trust Preservation Summary
- Trust preservation review is present.

## Business Behavior Contract Summary
- Business behavior contract is present.

## Golden Eval Summary
- Total cases: 11
- Case types: adversarial=1, historical_production=1, synthetic_boundary=9
- Risk tiers: high=4, low=2, medium=4, prohibited=1
- Expected admission routes: block=1, escalate=7, revise=1, show=2
- Boundary metadata coverage: 11/11 cases across 6 contrast family/families
- Expected workflow routes: answer=2, approval=3, clarify=1, escalate=4, refuse=1

## Tail-Risk / P0 Failure Mode Summary
- P0 failure mode checklist is missing.

## Automation Boundary Summary
- Automation boundary matrix is present with 7 row(s).

## Human Escalation Summary
- Human escalation design is present with 20 row(s).
- Structured escalation contract: valid.
- Workflow: presales_commercial_response
- Triggers: 3
- Destinations: 3 (account_executive_followup, pricing_approval_queue, legal_security_review)
- Handoff types: approval, async_case, specialist_routing
- Destination SLA coverage: 100%
- Destination fallback coverage: 100%
- Checkpoint required: yes
- Idempotency required: yes
- Resume behavior defined: yes
- Required eval slices: 11
- Eval handoff coverage: 7/7 required-handoff cases

## Tool/Action Safety Summary
- Rows: 5
- Risk tiers: low=1, medium=2, prohibited=2
- High/prohibited actions: approve_discount, create_contract_commitment

## Input/Output Perimeter Summary
- Input filter gate evidence is in launch_gate_review.md.
- Rows: 5
- Covered dimensions: grounding, policy_alignment, helpfulness, action_safety, escalation_judgment

## Model Arena Summary
- Rows: 3
- Covered models: small-fast-model, balanced-model, large-reasoning-model

## Metric Stack Summary
- Chatbot success metric stack is present.

## Domain-Owner Feedback Loop Summary
- No domain-owner feedback loop artifact found.

## Observability / Rollback Summary
- Observability gate: partial
- Drift monitoring gate: partial
- Rollback gate: partial

## Eval Results Summary
- Total result rows: 4
- Latest run ID: run_001
- Candidate coverage: presales_candidate
- Pass rate: 50%
- Route match rate: 100%
- Failed case IDs: discount_approval_boundary_004, legal_security_commitment_003
- Top failure categories: late_escalation=1, wrong_destination=1
- Workflow-route accuracy: 100%
- Trajectory pass rate: 75%
- End-state pass rate: 75%
- Prohibited-action rate: 0%
- Contrast-family reliability: unknown (0/6 families have complete result coverage)
- Semantic stability: unknown
- Repeated-run reliability: unknown (0 repeatedly evaluated case(s))
- Required-escalation recall: 100%
- Over-escalation rate: unknown
- Destination accuracy: 75%
- Context-preservation rate: 100%
- Fallback success rate: unknown
- Resume success rate: 75%
- Late-escalation rate: 25%

## Required Mitigations
- Launch blocker: High-impact workflows lack passing tail-risk/P0 review.
- Launch blocker: High-risk escalation evidence contains under-escalation, wrong-destination, payload, or resume failures.
- Launch blocker: Rollback gate is missing or not passing.
- Launch blocker: Owner signoff gate is missing or not passing.
- Golden eval gate: Add fresh drift samples from sales chat.
- Grounding gate: Add stale-context behavior.
- SOP/policy compilation gate: Compile allowed commercial claim snippets.
- Tool/action safety gate: Add explicit action risk matrix before launch.
- Input filter gate: Add competitor and jailbreak cases.
- Observability gate: Add dashboard owner.
- Drift monitoring gate: Schedule weekly drift review.
- Rollback gate: Define launch stop criteria.
- Owner signoff gate: Complete final review.

## Suggested Next Actions
- Resolve hard blockers before any user-facing launch.
- Close mitigation for Golden eval gate.
- Close mitigation for Grounding gate.
- Close mitigation for SOP/policy compilation gate.
- Close mitigation for Tool/action safety gate.
- Close mitigation for Input filter gate.

## Final Launch Recommendation
Not ready. Do not launch until hard blockers are resolved.
