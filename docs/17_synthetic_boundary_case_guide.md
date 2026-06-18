# Synthetic Boundary Case Guide

Synthetic boundary cases are the consequence-weighted layer of a golden eval set. Historical production cases show whether the system serves normal demand. Boundary cases test the exact point where a product rule changes what the system is permitted to do.

The OpenEvalGate operating chain is:

```text
Business rule
  -> boundary map
  -> contrast family
  -> executable golden eval cases
  -> route, trajectory, and end-state grading
  -> slice-specific release gate
  -> production learning
```

## Start With The Business Rule

Define the decision, required evidence, controlling threshold or state, permitted behavior, prohibited behavior, and fallback. Record these decisions in the business behavior contract, automation boundary matrix, action risk matrix, and human escalation design.

Do not ask an LLM to invent the answer key. Domain and policy owners define the rule. An LLM may expand an approved seed into controlled variants.

## Build A Contrast Family

A contrast family starts with an anchor case and changes one controlling fact at a time. Useful variation types are:

- `threshold_neighbor`: immediately below, at, or above a limit;
- `missing_fact`: remove one required fact;
- `conflicting_evidence`: introduce disagreement between authoritative sources;
- `authority_state`: change permission, consent, ownership, or workflow state;
- `semantic_invariance`: change wording, language, order, or tone without changing the rule.

Each member records:

```yaml
boundary:
  family_id: refund_automation_limit
  anchor_case_id: refund_limit_anchor_001
  controlling_fact: requested_refund
  variation_type: threshold_neighbor
  before_value: 49.99
  after_value: 50.01
```

The anchor references itself and uses `variation_type: anchor`.

## Separate Workflow And Admission Routes

OpenEvalGate represents two different decisions:

- `expected_workflow_route`: `answer`, `clarify`, `act`, `approval`, `escalate`, or `refuse`;
- `expected_route`: response admission through `show`, `revise`, `escalate`, or `block`.

An agent may correctly choose `act`, execute an authorized tool, and then have its final response admitted as `show`. Keeping these dimensions separate prevents response quality from hiding an unsafe action.

## Grade Route, Trajectory, And End State

Use deterministic checks wherever possible:

```yaml
expected_workflow_route: approval
expected_trajectory:
  required_events:
    - create_refund_review_case
  prohibited_events:
    - issue_refund
expected_end_state:
  assertions:
    - refund_not_issued
    - review_case_created
```

The external eval runner executes the candidate system. OpenEvalGate ingests the result, including optional workflow-route, trajectory, end-state, prohibited-action, and repeated-trial evidence.

## Turn Evidence Into A Release Control

Boundary families should be connected to case-level release-gate metadata and slice-specific thresholds. Critical prohibited actions normally require a 100% pass threshold. Material workflow-route failures should block or constrain the affected slice. Style issues may remain non-blocking when no trust or business contract was violated.

Boundary evidence supports the golden-eval, tail-risk/P0, tool/action safety, automation-boundary, human-escalation, observability, rollback, and owner-signoff gates.

The generated report can summarize:

- workflow-route accuracy;
- prohibited-action rate;
- contrast-family reliability when every family member has results;
- semantic stability when anchor and semantic variants have comparable workflow-route evidence;
- repeated-run reliability for cases executed more than once.

Unavailable metrics remain explicitly marked as unknown rather than being inferred from incomplete evidence.

## Production Learning Loop

Use this loop after an incident, override, appeal, or policy change:

```text
Production failure
  -> expert-authored anchor
  -> nearby contrast variants
  -> deterministic and rubric grading
  -> release-gate update
  -> monitored rollout and rollback criteria
```

One incident should create coverage of the surrounding decision surface, not only a single replay.
