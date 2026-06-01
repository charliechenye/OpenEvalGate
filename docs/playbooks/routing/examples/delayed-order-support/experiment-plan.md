# Delayed Order Support Routing Experiment Plan

## Decision Under Test

| Field | Value |
| --- | --- |
| Experiment ID | delayed_order_routing_exp_001 |
| Scenario or workflow | Delayed-order support |
| Decision owner | support_product |
| Current baseline route | Single general support model for all delayed-order requests |
| Proposed route | Scenario routing to delivery-status lookup, logistics reconciliation, refund eligibility, fraud escalation, or exception review |
| Eligible segment | Authenticated users with delayed shipped orders and English-language support requests |
| Excluded segment | Unauthenticated users, chargeback disputes, active fraud investigations, legal threats, regulated goods |

## Hypothesis

Scenario-first routing will improve durable resolution and reduce unnecessary latency for routine ETA questions while preserving stronger reasoning, deterministic checks, and human review for higher-risk delayed-order scenarios.

## Experiment Arms

| Arm | Execution path | Purpose | Allocation |
| --- | --- | --- | --- |
| A | Baseline general support model served immediately | Current production baseline | 40% of eligible sample |
| B | Scenario router with selected workflow and real route latency | Net product impact of routing | 40% of eligible sample |
| C | Baseline general support model delayed to match Arm B latency distribution | Estimate pure waiting penalty | 20% of eligible sample |

## Evaluation Set

| Eval slice | Required coverage | Cases or source |
| --- | --- | --- |
| Routine ETA lookup | Clear carrier ETA and no remedy request | Historical delayed-order contacts |
| Conflicting records | Carrier and warehouse disagree | Synthetic boundary cases plus past escalations |
| Refund request | User asks for refund because order is late | Refund policy evals |
| Fraud allegation | User reports unauthorized order or suspected account compromise | Tail-risk/P0 cases |
| High-value exception | User asks for compensation outside standard policy | Human-reviewed exception cases |

## Success Thresholds

| Metric | Minimum acceptable result | Owner |
| --- | --- | --- |
| Durable resolution rate | Improves by at least 3 points overall and does not regress in any high-risk slice | support_product |
| Repeat-contact rate | Does not increase for any eligible scenario | support_product |
| Fraud and high-risk escalation accuracy | 100% on P0 and fraud eval cases | trust_safety |
| Refund policy compliance | 100% of refund recommendations include deterministic eligibility result | platform |
| Human-review acceptance rate | At least 90% for exception-review summaries | operations |
| p95 time to resolution | Improves for ETA lookup and does not breach current baseline by more than 10% elsewhere | engineering |
| Quality-adjusted cost per resolved task | Improves or remains neutral after review and recontact costs | platform |

## Guardrails

| Guardrail | Threshold | Action if breached |
| --- | --- | --- |
| Refund recommendation without eligibility check | 0 | Stop experiment |
| Fraud allegation not escalated | 0 | Stop experiment and add regression case |
| High-value compensation without approval | 0 | Stop experiment |
| Repeat-contact increase in routine ETA slice | More than 2 points | Pause expansion |
| p95 latency breach | More than 10% above baseline for non-routine slices | Review before expansion |

## Analysis Plan

- Compare Arm A vs. Arm C to measure the user-facing penalty of waiting.
- Compare Arm B vs. Arm C to test whether routed output quality compensates for any extra latency.
- Compare Arm A vs. Arm B to decide whether routing improves the end-to-end product outcome.
- Report results by scenario, workflow, risk tier, and whether deterministic controls were required.

## Launch Decision

| Decision | Criteria |
| --- | --- |
| Expand | All guardrails pass; durable resolution improves; ETA latency improves; high-risk routing remains perfect on P0 cases |
| Hold | Quality improves but latency, repeat contacts, or review burden is inconclusive |
| Roll back | Any P0 guardrail breach, refund-control miss, fraud-escalation miss, or material repeat-contact increase |
