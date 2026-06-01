# Delayed Order Support Routing Rollout Checklist

## Baseline

| Check | Status | Evidence | Owner |
| --- | --- | --- | --- |
| Current delayed-order route documented | pass | Baseline general support workflow recorded | support_product |
| Baseline metrics captured | partial | Resolution, repeat contact, p95 latency, and escalation rate available | platform |
| Failure modes represented in evals | partial | Fraud and refund cases exist; add more conflicting-record cases | ai_quality |
| Rollback path confirmed | pass | Route flag can return all traffic to baseline support workflow | engineering |

## Offline Validation

| Check | Status | Evidence | Owner |
| --- | --- | --- | --- |
| Scenario-routing policy reviewed | pass | `scenario-routing-policy.yaml` drafted | support_product |
| Golden eval coverage includes route expectations | partial | Add expected route labels for high-value exceptions | ai_quality |
| Tail-risk/P0 cases pass | pass | Fraud and unauthorized refund cases must escalate or block | trust_safety |
| Deterministic risk overrides tested | pass | Ownership, refund eligibility, and compensation threshold checks run outside the model | platform |
| Route comparison complete | partial | Need final latency-isolation readout | ml_engineering |

## Shadow Mode

| Check | Status | Evidence | Owner |
| --- | --- | --- | --- |
| Router runs without changing user-visible behavior | planned | Shadow mode for eligible delayed-order contacts | platform |
| Router version logged | planned | `delayed-order-router-2026-05` in trace metadata | platform |
| Disagreements reviewed | planned | Daily review of baseline-vs-router disagreements | ai_quality |
| High-risk disagreements escalated | planned | Fraud, refund, and exception disagreement queue | trust_safety |

## Limited Launch

| Check | Status | Evidence | Owner |
| --- | --- | --- | --- |
| Eligible segment bounded | planned | Authenticated English delayed-order contacts only | support_product |
| Excluded scenarios blocked | planned | Fraud investigations, chargebacks, legal threats, regulated goods excluded | support_product |
| Traffic cohort defined | planned | Start at 5% of eligible segment | engineering |
| Monitoring dashboard live | planned | Routing, resolution, latency, repeat-contact, and guardrail dashboard | platform |
| Rollback owner named | planned | support_platform on call | engineering |

## Expansion Criteria

| Check | Status | Evidence | Owner |
| --- | --- | --- | --- |
| Durable resolution improves |  |  | support_product |
| Routine ETA latency improves |  |  | engineering |
| Repeat contacts do not increase |  |  | support_product |
| Fraud and refund controls pass |  |  | trust_safety |
| Human-review queue remains healthy |  |  | operations |
| Quality-adjusted cost per resolved task improves or remains neutral |  |  | platform |

## Rollback Triggers

| Trigger | Threshold | Action | Owner |
| --- | --- | --- | --- |
| Fraud allegation not escalated | 1 case | Stop rollout and add regression case | trust_safety |
| Refund recommendation without eligibility result | 1 case | Revert to baseline route | platform |
| High-value exception without approval | 1 case | Revert to baseline route | operations |
| Repeat-contact increase | More than 2 points in any scenario slice | Pause expansion | support_product |
| p95 latency breach | More than 10% above baseline outside ETA lookup | Revert to baseline route | engineering |
