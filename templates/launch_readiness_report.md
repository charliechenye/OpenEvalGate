# Launch Readiness Report

- **System name:**
- **Assistant type:**
- **Evidence completeness score:**
- **Evidence package band:**
- **Control evidence completeness threshold met:**
- **Behavioral evidence status:**
- **Critical-control status:**
- **Maximum permitted stage:**
- **Final launch recommendation:**
- **Recommended next actions:**

## Executive Summary

Summarize what is ready, what is blocked, and whether launch would preserve user trust.

## Evidence Completeness Score

Report completeness of declared launch-control and governance evidence. Do not present this score as observed behavioral quality or as the final launch determination.

Use only these evidence package bands: `Substantially complete`, `Material gaps`, or `Incomplete`.

State whether the control evidence completeness threshold is met. Explain that meeting it does not override hard blockers or grant permission to begin shadow evaluation.

## Hard-Gate Evaluation

Render one deterministic row for each centralized hard gate:

| Gate | Applicable | Required status | Actual status | Outcome |
| --- | --- | --- | --- | --- |
|  | Yes / No / Unknown | pass / pass when applicable | pass / partial / fail / not_applicable / missing / invalid | Satisfied / Blocked / Not applicable / Invalid |

Unknown applicability must be `Blocked`. Unsupported or duplicate declarations must be `Invalid`; do not select one duplicate row.

## Hard Blockers

List blockers that force `Not ready` regardless of score.

## Trust Preservation Summary

Summarize evidence that the assistant helps users complete the task now while preserving trust for future interactions.

## Business Behavior Contract Summary

Summarize business-owned expected behavior, unacceptable behavior, action policy, and signoff.

## Golden Eval Summary

Summarize eval case coverage, risk tiers, routes, and known gaps.

## Tail-Risk / P0 Failure Mode Summary

Summarize worst plausible failures and how they are prevented, detected, escalated, or blocked.

## Automation Boundary Summary

Summarize automate, clarify, recommend, human approval, escalate, and block routes.

## Human Escalation Summary

Summarize escalation-contract validity, triggers, destinations, handoff types, SLA/fallback coverage, payload requirements, checkpoint/idempotency controls, and eval-slice coverage.

## Tool/Action Safety Summary

Summarize action risk tiers, deterministic gates, approval requirements, and prohibited actions.

## Input/Output Perimeter Summary

Summarize input filter, output critic, response admission, and expected routes.

## Model Arena Summary

Summarize candidate model results if available.

## Metric Stack Summary

Summarize efficiency, quality, journey, and business/trust metrics.

## Domain-Owner Feedback Loop Summary

Summarize how domain owners review behavior, add eval cases, propose policy changes, and approve risky updates.

## Observability / Rollback Summary

Summarize monitoring, drift review, incident response, and rollback evidence.

## Observed Behavioral Quality

Summarize externally generated candidate outputs and grading feedback from `eval_results.csv`, including required-escalation recall, over-escalation, destination accuracy, context preservation, fallback success, resume success, and late escalation.

Use the exact behavioral-evidence wording for missing, empty, invalid, and available results. Do not calculate metrics from invalid rows.

## Critical-Control Status

Report `Fail`, `Not evaluated`, or `No known blockers detected`. Do not use `Pass` until complete critical-control policy exists.

## Maximum Permitted Stage

State the highest permitted stage from the deterministic assessment. Do not permit controlled launch in this iteration.

## Required Mitigations

| Mitigation | Owner | Due date | Launch blocker |
| --- | --- | --- | --- |
|  |  |  |  |

## Recommended Next Actions

State the deterministic recommended next action.

## Final Launch Recommendation

Make the final launch recommendation independently from the evidence completeness score and state what must be fixed before launch.
