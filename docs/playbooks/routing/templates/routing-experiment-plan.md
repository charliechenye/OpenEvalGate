# Routing Experiment Plan

## Decision Under Test

| Field | Value |
| --- | --- |
| Experiment ID |  |
| Scenario or workflow |  |
| Decision owner |  |
| Start date |  |
| Review date |  |
| Current baseline route |  |
| Proposed route |  |
| Eligible segment |  |
| Excluded segment |  |

## Hypothesis

State the expected quality lift, latency or cost change, and user outcome improvement.

## Experiment Arms

| Arm | Execution path | Purpose | Traffic or sample allocation |
| --- | --- | --- | --- |
| A | Baseline route served immediately | Efficient baseline |  |
| B | Stronger or alternative route served with real latency | Net product impact |  |
| C | Baseline route delayed to match Arm B latency | Pure latency penalty |  |

## Evaluation Set

| Eval slice | Required coverage | Cases or source |
| --- | --- | --- |
| Historical cases |  |  |
| Boundary cases |  |  |
| Conflicting-context cases |  |  |
| Tail-risk/P0 cases |  |  |
| Fresh drift samples |  |  |

## Success Thresholds

| Metric | Minimum acceptable result | Owner |
| --- | --- | --- |
| Durable resolution rate |  | product |
| Repeat-contact rate |  | product |
| Escalation quality |  | operations |
| Policy compliance |  | trust_safety |
| Human-review acceptance rate |  | operations |
| p95 time to resolution |  | engineering |
| Quality-adjusted cost per resolved task |  | platform |

## Guardrails

| Guardrail | Threshold | Action if breached |
| --- | --- | --- |
| High-risk action without deterministic check | 0 | Stop experiment |
| P0 failure | 0 | Stop experiment and add regression case |
| Unsafe escalation miss |  | Pause eligible segment |
| p95 latency |  | Roll back to baseline |
| Negative feedback or abandonment |  | Review before expansion |

## Analysis Plan

- Compare Arm A vs. Arm C to estimate pure latency penalty.
- Compare Arm B vs. Arm C to decide whether stronger output compensates for the wait.
- Compare Arm A vs. Arm B to assess net product impact.
- Segment results by scenario, workflow, risk tier, language, complexity, and tool-use depth.

## Launch Decision

| Decision | Criteria |
| --- | --- |
| Expand |  |
| Hold |  |
| Roll back |  |

## Notes

Record known caveats, unresolved questions, and required follow-up eval cases.
