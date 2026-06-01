# Staged Rollout Checklist

## Baseline

| Check | Status | Evidence | Owner |
| --- | --- | --- | --- |
| Current route is documented |  |  | product |
| Baseline resolution, escalation, latency, and cost are measured |  |  | platform |
| Known failure modes are represented in eval cases |  |  | ai_quality |
| Existing rollback path is confirmed |  |  | engineering |

## Offline Validation

| Check | Status | Evidence | Owner |
| --- | --- | --- | --- |
| Routing decision cards are complete for eligible scenarios |  |  | product |
| Golden eval coverage includes route expectations |  |  | ai_quality |
| Tail-risk/P0 cases pass for eligible scenarios |  |  | trust_safety |
| Deterministic risk overrides are tested |  |  | platform |
| Model arena or route comparison is complete |  |  | ml_engineering |

## Shadow Mode

| Check | Status | Evidence | Owner |
| --- | --- | --- | --- |
| Alternative route runs without changing user-visible behavior |  |  | platform |
| Route decisions are logged with router version |  |  | platform |
| Disagreements with baseline are reviewed |  |  | ai_quality |
| High-risk disagreements are escalated before launch |  |  | trust_safety |

## Limited Launch

| Check | Status | Evidence | Owner |
| --- | --- | --- | --- |
| Eligible segment is bounded |  |  | product |
| Excluded scenarios are blocked from the experiment |  |  | product |
| Traffic percentage or cohort is defined |  |  | engineering |
| Monitoring dashboard is live |  |  | platform |
| On-call and rollback owner are named |  |  | engineering |

## Expansion

| Check | Status | Evidence | Owner |
| --- | --- | --- | --- |
| Durable resolution improves or remains healthy |  |  | product |
| Repeat contacts do not increase |  |  | product |
| Escalation quality remains acceptable |  |  | operations |
| Safety and policy guardrails pass |  |  | trust_safety |
| p95 latency remains within threshold |  |  | engineering |
| Quality-adjusted cost per resolved task is acceptable |  |  | platform |

## Rollback

| Trigger | Threshold | Action | Owner |
| --- | --- | --- | --- |
| P0 or unsafe action |  | Stop rollout and add regression case | trust_safety |
| Missing deterministic control |  | Revert to baseline route | platform |
| Resolution degradation |  | Pause expansion | product |
| Repeat-contact increase |  | Pause expansion | product |
| p95 latency breach |  | Revert to baseline route | engineering |
| Human-review overload |  | Reduce eligible segment | operations |
