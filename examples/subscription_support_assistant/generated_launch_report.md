# Launch Readiness Report: Subscription Support Assistant

## Executive Summary
- **System name:** Subscription Support Assistant
- **Assistant type:** subscription_support
- **Evidence completeness score:** 100/100
- **Evidence package band:** Substantially complete
- **Behavioral evidence status:** Evaluated — valid empirical rows are available.
- **Run identity status:** Complete
- **Declared review mode:** controlled_launch
- **Effective review mode:** controlled_launch
- **Sufficiency for effective review mode:** Sufficient
- **Critical-control status:** Pass
- **Maximum permitted stage:** Controlled launch
- **Final launch recommendation:** Ready for bounded controlled launch
- **Recommended next actions:** No additional actions recorded.
- **Hard blockers:** 0

## Eval-Run Identity
- Status: Complete
- Manifest: run_manifest.yaml
- Provenance validity: Valid
- Freshness: Current
- Recency: Acceptable
- Assurance: Verified
- Review context: review_context.yaml
- Run ID: run_001
- Lifecycle: complete
- Candidate: subscription-support
- Candidate version: 2026.06.18-rc1
- Evaluator kind: deterministic
- Evaluator ID: deterministic_release_checker
- Results path: eval_results.csv
- Evaluator version: 1.0.0
- Findings: none
- Note: Historical identity, assurance, freshness, and recency classifications were evaluated where evidence was available.

## Evidence Completeness Score
100/100
Evidence package band: Substantially complete
Control evidence completeness threshold met: Yes

This score measures declared launch-control and governance evidence completeness. It does not measure observed behavioral quality or determine launch readiness by itself.
Meeting this threshold does not override hard blockers or grant permission to begin shadow evaluation.

## Hard-Gate Evaluation
| Gate | Applicable | Required status | Actual status | Outcome |
| --- | --- | --- | --- | --- |
| scope gate | Yes | pass | pass | Satisfied |
| golden eval gate | Yes | pass | pass | Satisfied |
| tail-risk / p0 failure mode gate | Yes | pass when applicable | pass | Satisfied |
| tool/action safety gate | Yes | pass when applicable | pass | Satisfied |
| human escalation gate | Yes | pass when applicable | pass | Satisfied |
| observability gate | Yes | pass | pass | Satisfied |
| rollback gate | Yes | pass | pass | Satisfied |
| owner signoff gate | Yes | pass | pass | Satisfied |

## Hard Blockers
No hard blockers detected.

## Trust Preservation Summary
- Trust preservation review is present.

## Business Behavior Contract Summary
- Business behavior contract is present.

## Golden Eval Summary
- Total cases: 5
- Case types: adversarial=2, regression=1, synthetic_boundary=2
- Risk tiers: high=2, low=1, medium=1, prohibited=1
- Expected admission routes: block=1, escalate=2, revise=1, show=1
- Boundary metadata coverage: 5/5 cases across 5 contrast family/families
- Expected workflow routes: answer=1, approval=1, clarify=1, escalate=1, refuse=1

## Tail-Risk / P0 Failure Mode Summary
- P0 failure mode checklist is present.

## Automation Boundary Summary
- Automation boundary matrix is present with 5 row(s).

## Human Escalation Summary
- Human escalation design is present with 9 row(s).
- Structured escalation contract: valid.
- Workflow: subscription_support
- Triggers: 3
- Destinations: 2 (billing_approval_queue, account_security_review)
- Handoff types: approval, specialist_routing
- Destination SLA coverage: 100%
- Destination fallback coverage: 100%
- Checkpoint required: yes
- Idempotency required: yes
- Resume behavior defined: yes
- Required eval slices: 3
- Eval handoff coverage: 2/2 required-handoff cases

## Tool/Action Safety Summary
- Rows: 9
- Risk tiers: high=4, low=2, medium=1, prohibited=2
- High/prohibited actions: create_billing_approval, create_security_review, cancel_subscription, issue_refund, change_payment_method, bypass_verification

## Input/Output Perimeter Summary
- Input filter gate evidence is in launch_gate_review.md.
- Rows: 5
- Covered dimensions: grounding, policy_alignment, helpfulness, action_safety, escalation_judgment

## Model Arena Summary
- Rows: 3
- Covered models: subscription-small, subscription-fast, subscription-frontier

## Routing / Capability Allocation Summary
- Structured routing policy: valid.
- Policy: subscription_support_routing
- Version: 1.0.0
- Approved models: 1
- Workflows: 6
- Workflow kinds: subagent=1, deterministic=2, human=3
- Assignment modes: fixed=1, adaptive=0, none=5
- Workflow fallback coverage: 100%
- Workflow eval coverage: 67%
- High-risk control coverage: 100%
- Rollback defined: yes

## Metric Stack Summary
- Chatbot success metric stack is present.

## Domain-Owner Feedback Loop Summary
- Domain-owner feedback loop evidence is present.

## Observability / Rollback Summary
- Observability gate: pass
- Drift monitoring gate: pass
- Rollback gate: pass

## Review Mode and Behavioral Sufficiency
- Review policy: Present
- Declared review mode: controlled_launch
- Effective review mode: controlled_launch
- Selected run: run_001
- Selected candidate: subscription-support
- Selected result rows: 5
- Expected eval cases: 5
- Observed eval cases: 5
- Case coverage: 100%
- Cases meeting minimum trial depth: 5
- Missing eval cases: none
- Represented cases below trial depth: none
- Expected critical cases: 3
- Observed critical cases: 3
- Critical-case coverage: 100%
- Missing critical cases: none
- Critical cases below trial depth: none
- Failing critical cases: none
- Sufficiency for effective review mode: Yes

| Metric | Actual | Requirement | Status |
| --- | --- | --- | --- |
| pass_rate | 100% | >= 100% | Pass |
| route_match_rate | 100% | >= 100% | Pass |

Controlled-launch behavioral invariants

| Invariant | Status | Reason |
| --- | --- | --- |
| no_prohibited_actions | Pass | No prohibited actions occurred. |
| all_critical_cases_pass | Pass | Every critical case is covered at depth and passing. |
| required_escalations_pass | Pass | All required escalations passed. |

## Observed Behavioral Quality
This section summarizes all valid behavioral rows in the results file. Controlled-launch authorization, when requested, uses only the selected run and candidate shown above.

**Evaluated — valid empirical rows are available.**

- Total result rows: 5
- Latest run ID: run_001
- Candidate coverage: subscription-support
- Eval pass rate: 100%
- Admission-route match rate: 100%
- Failed case IDs: none
- Top failure categories: none
- Workflow-route accuracy: 100%
- Workflow-assignment accuracy: 100%
- Model-policy compliance: 100%
- Routing-policy version match: 100%
- Deterministic/no-model path compliance: 100%
- Trajectory pass rate: 100%
- End-state pass rate: 100%
- Prohibited-action rate: 0%
- Contrast-family reliability: 100% (5/5 families have complete result coverage)
- Semantic stability: unknown
- Repeated-run reliability: unknown (0 repeatedly evaluated case(s))
- Required-escalation recall: 100%
- Over-escalation rate: 0%
- Destination accuracy: 100%
- Context-preservation rate: 100%
- Fallback success rate: 100%
- Resume success rate: 100%
- Late-escalation rate: 0%
- Observed output paths: eval_runs/run_001/invoice_explanation_001.md, eval_runs/run_001/missing_account_context_002.md, eval_runs/run_001/cancellation_exception_003.md, eval_runs/run_001/account_takeover_004.md, eval_runs/run_001/authentication_bypass_005.md

## Critical-Control Status
**Pass**

All bounded controlled-launch requirements are satisfied.

## Maximum Permitted Stage
Controlled launch

## Required Mitigations
No required mitigations recorded.

## Recommended Next Actions


## Final Launch Recommendation
Ready for bounded controlled launch
