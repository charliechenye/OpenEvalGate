# Launch Readiness Report: Education Study Assistant

## Executive Summary
- **System name:** Education Study Assistant
- **Assistant type:** education
- **Evidence completeness score:** 34/100
- **Evidence package band:** Incomplete
- **Behavioral evidence status:** Evaluated — valid empirical rows are available.
- **Declared review mode:** Not configured
- **Effective review mode:** shadow_launch
- **Behavioral sufficiency status:** Sufficient
- **Critical-control status:** Fail
- **Maximum permitted stage:** Documentation remediation
- **Final launch recommendation:** Not ready for shadow evaluation
- **Recommended next actions:** Complete missing or invalid control-evidence requirements; Remediate known hard blockers.
- **Hard blockers:** 6

## Evidence Completeness Score
34/100
Evidence package band: Incomplete
Control evidence completeness threshold met: No

This score measures declared launch-control and governance evidence completeness. It does not measure observed behavioral quality or determine launch readiness by itself.
Meeting this threshold does not override hard blockers or grant permission to begin shadow evaluation.

## Hard-Gate Evaluation
| Gate | Applicable | Required status | Actual status | Outcome |
| --- | --- | --- | --- | --- |
| scope gate | Yes | pass | pass | Satisfied |
| golden eval gate | Yes | pass | partial | Blocked |
| tail-risk / p0 failure mode gate | Yes | pass when applicable | missing | Blocked |
| tool/action safety gate | Yes | pass when applicable | pass | Satisfied |
| human escalation gate | Yes | pass when applicable | partial | Blocked |
| observability gate | Yes | pass | partial | Blocked |
| rollback gate | Yes | pass | partial | Blocked |
| owner signoff gate | Yes | pass | partial | Blocked |

## Hard Blockers
- **missing_golden_eval:** Golden eval gate requires `pass`; actual status is `partial`. Evidence: eval_cases.yaml
- **missing_tail_risk_review:** Tail-risk / P0 failure mode gate requires `pass` for high-impact projects; the gate is missing. Required evidence is missing or invalid: p0_failure_mode_checklist.md. Evidence: p0_failure_mode_checklist.md
- **missing_escalation_path:** Human escalation gate requires `pass` for high-impact projects; actual status is `partial`. Evidence: human_escalation_design.md
- **missing_monitoring:** Observability gate requires `pass`; actual status is `partial`. Evidence: launch-gate evidence cell
- **missing_rollback:** Rollback gate requires `pass`; actual status is `partial`. Evidence: launch-gate evidence cell
- **missing_owner_signoff:** Owner signoff gate requires `pass`; actual status is `partial`. Evidence: launch-gate evidence cell

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

## Review Mode and Behavioral Sufficiency
- Review policy: Not provided
- Declared review mode: Not configured
- Effective review mode: shadow_launch
- Selected run: Not configured
- Selected candidate: Not configured
- Selected result rows: 0
- Expected eval cases: 10
- Observed eval cases: 0
- Case coverage: 0%
- Cases meeting minimum trial depth: 0
- Missing eval cases: accommodation_policy_ambiguity_005, assessment_context_missing_006, concept_explanation_semantic_007, explain_photosynthesis_002, grade_dispute_semantic_009, graded_answer_request_001, graded_answer_semantic_008, graded_dispute_escalation_003, learner_safety_escalation_004, learner_safety_semantic_010
- Represented cases below trial depth: none
- Expected critical cases: 7
- Observed critical cases: 0
- Critical-case coverage: 0%
- Missing critical cases: accommodation_policy_ambiguity_005, grade_dispute_semantic_009, graded_answer_request_001, graded_answer_semantic_008, graded_dispute_escalation_003, learner_safety_escalation_004, learner_safety_semantic_010
- Failing critical cases: none
- Behavioral sufficiency for requested mode: Yes

| Metric | Actual | Requirement | Status |
| --- | --- | --- | --- |
| pass_rate | Not evaluated | Not configured | Not configured |
| route_match_rate | Not evaluated | Not configured | Not configured |

| Invariant | Status | Reason |
| --- | --- | --- |
| no_prohibited_actions | Not applicable | Prohibited-action evidence is unavailable. |
| all_critical_cases_pass | Not applicable | No selected controlled-launch scope is configured. |
| required_escalations_pass | Not applicable | No selected controlled-launch scope is configured. |

## Observed Behavioral Quality
**Evaluated — valid empirical rows are available.**

- Total result rows: 5
- Latest run ID: run_001
- Candidate coverage: education_candidate
- Eval pass rate: 40%
- Admission-route match rate: 80%
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

## Critical-Control Status
**Fail**

The following critical controls failed:

- `missing_golden_eval`
- `missing_tail_risk_review`
- `missing_escalation_path`
- `missing_monitoring`
- `missing_rollback`
- `missing_owner_signoff`

## Maximum Permitted Stage
Documentation remediation

## Required Mitigations
- Launch blocker: Golden eval gate requires `pass`; actual status is `partial`.
- Launch blocker: Tail-risk / P0 failure mode gate requires `pass` for high-impact projects; the gate is missing. Required evidence is missing or invalid: p0_failure_mode_checklist.md.
- Launch blocker: Human escalation gate requires `pass` for high-impact projects; actual status is `partial`.
- Launch blocker: Observability gate requires `pass`; actual status is `partial`.
- Launch blocker: Rollback gate requires `pass`; actual status is `partial`.
- Launch blocker: Owner signoff gate requires `pass`; actual status is `partial`.
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

## Recommended Next Actions
- Complete missing or invalid control-evidence requirements.
- Remediate known hard blockers.

## Final Launch Recommendation
Not ready for shadow evaluation
