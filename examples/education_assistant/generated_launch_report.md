# Launch Readiness Report: Education Study Assistant

## Executive Summary
- **System name:** Education Study Assistant
- **Assistant type:** education
- **Overall readiness score:** 34/100
- **Recommendation:** Not ready
- **Launch blocker status:** 3 hard blocker(s) require remediation.

## Overall Readiness Score
34/100

## Recommendation
Not ready

## Hard Blockers
- **missing_tail_risk_review:** High-impact workflows lack passing tail-risk/P0 review. Evidence: p0_failure_mode_checklist.md or Tail-risk / P0 gate
- **missing_rollback:** Rollback gate is missing or not passing. Evidence: Rollback gate
- **missing_owner_signoff:** Owner signoff gate is missing or not passing. Evidence: Owner signoff gate

## Trust Preservation Summary
- Trust preservation review is present.

## Business Behavior Contract Summary
- Business behavior contract is present.

## Golden Eval Summary
- Total cases: 10
- Case types: historical_production=1, regression=1, synthetic_boundary=8
- Risk tiers: high=4, low=2, medium=4
- Expected admission routes: escalate=5, revise=3, show=2
- Boundary metadata coverage: 10/10 cases across 5 contrast family/families
- Expected workflow routes: answer=2, approval=1, clarify=1, escalate=4, refuse=2

## Tail-Risk / P0 Failure Mode Summary
- P0 failure mode checklist is missing.

## Automation Boundary Summary
- Automation boundary matrix is present with 7 row(s).

## Human Escalation Summary
- Human escalation design is present with 21 row(s).
- Structured escalation contract: valid.
- Workflow: education_integrity_support
- Triggers: 4
- Destinations: 3 (instructor_review, learner_safety_review, accessibility_policy_review)
- Handoff types: approval, async_case, specialist_routing
- Destination SLA coverage: 100%
- Destination fallback coverage: 100%
- Checkpoint required: yes
- Idempotency required: yes
- Resume behavior defined: yes
- Required eval slices: 10
- Eval handoff coverage: 5/5 required-handoff cases

## Tool/Action Safety Summary
- Rows: 3
- Risk tiers: low=1, medium=1, prohibited=1
- High/prohibited actions: reveal_answer_key

## Input/Output Perimeter Summary
- Input filter gate evidence is in launch_gate_review.md.
- Rows: 5
- Covered dimensions: grounding, policy_alignment, helpfulness, action_safety, escalation_judgment

## Model Arena Summary
No model arena scorecard found.

## Routing / Capability Allocation Summary
- Structured routing policy: valid.
- Policy: education_capability_allocation
- Version: 1.0.0
- Approved models: 1
- Workflows: 5
- Workflow kinds: subagent=2, deterministic=0, human=3
- Assignment modes: fixed=2, adaptive=0, none=3
- Workflow fallback coverage: 100%
- Workflow eval coverage: 100%
- High-risk control coverage: 100%
- Rollback defined: yes

## Metric Stack Summary
- Chatbot success metric stack is present.

## Domain-Owner Feedback Loop Summary
- No domain-owner feedback loop artifact found.

## Observability / Rollback Summary
- Observability gate: partial
- Drift monitoring gate: fail
- Rollback gate: partial

## Eval Results Summary
- Total result rows: 5
- Latest run ID: run_001
- Candidate coverage: education_candidate
- Pass rate: 40%
- Route match rate: 80%
- Failed case IDs: accommodation_policy_ambiguity_005, explain_photosynthesis_002, graded_dispute_escalation_003
- Top failure categories: missing_payload=1, over_escalation=1, resume_failure=1
- Workflow-route accuracy: 80%
- Workflow-assignment accuracy: 80%
- Model-policy compliance: 80%
- Routing-policy version match: 100%
- Deterministic/no-model path compliance: 100%
- Trajectory pass rate: 80%
- End-state pass rate: 40%
- Prohibited-action rate: 0%
- Contrast-family reliability: 0% (1/5 families have complete result coverage)
- Semantic stability: unknown
- Repeated-run reliability: unknown (0 repeatedly evaluated case(s))
- Required-escalation recall: 100%
- Over-escalation rate: 50%
- Destination accuracy: 100%
- Context-preservation rate: 67%
- Fallback success rate: 100%
- Resume success rate: 33%
- Late-escalation rate: 0%

## Required Mitigations
- Launch blocker: High-impact workflows lack passing tail-risk/P0 review.
- Launch blocker: Rollback gate is missing or not passing.
- Launch blocker: Owner signoff gate is missing or not passing.
- Golden eval gate: Add historical learner support cases.
- Model selection gate: Record product-specific selection rationale.
- Model arena gate: Run candidate models on golden eval set.
- Routing / capability allocation gate: Replace provisional assignments after the education-specific arena.
- SOP/policy compilation gate: Compile per-course response rules.
- Input filter gate: Add jailbreak and answer-leakage examples.
- Human escalation gate: Finalize timeout and fallback ownership.
- Observability gate: Add drift sampling owner.
- Cost/latency gate: Measure p95 latency.
- Drift monitoring gate: Add weekly learner request review.
- Rollback gate: Define stop criteria.
- Owner signoff gate: Complete signoff after arena and drift plan.

## Suggested Next Actions
- Resolve hard blockers before any user-facing launch.
- Close mitigation for Golden eval gate.
- Close mitigation for Model selection gate.
- Close mitigation for Model arena gate.
- Close mitigation for Routing / capability allocation gate.
- Close mitigation for SOP/policy compilation gate.

## Final Launch Recommendation
Not ready. Do not launch until hard blockers are resolved.
