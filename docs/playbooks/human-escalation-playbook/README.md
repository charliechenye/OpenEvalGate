# Human Escalation Playbook

A practical playbook for product, engineering, operations, and risk teams designing human escalation for production GenAI assistants and agents.

OpenEvalGate treats human escalation as launch-readiness evidence. A production agent should know when to resolve autonomously, ask for clarification, pause for approval, transfer judgment to a human workflow, or refuse an unsafe action. The goal is not maximum automation. The goal is trustworthy resolution at the right level of autonomy for the workflow's risk profile.

## What Human Escalation Is

Human escalation is not a vague fallback after the model fails. It is a control surface made of policies, deterministic checks, workflow states, routing destinations, handoff payloads, SLAs, eval cases, and monitoring.

For each workflow, the system should choose one of these paths:

| Path | Use when | Required evidence |
| --- | --- | --- |
| Resolve | Intent is clear, context is sufficient, policy is deterministic, and risk is bounded. | Eval cases prove routine work is completed without unnecessary handoff. |
| Clarify | A narrow, recoverable context gap prevents safe completion. | Clarification budget and repeated-question behavior are defined. |
| Escalate | Human judgment, specialist expertise, authority, or operational handling is required. | Destination, SLA, handoff payload, fallback, and eval coverage are defined. |
| Approval | The agent has a proposed high-impact action that must pause before execution. | Reviewer decision, timeout, resume, and idempotency behavior are defined. |
| Refuse or block | The request violates policy, safety, compliance, or abuse controls. | Refusal/block criteria are deterministic and tested. |

## How This Fits OpenEvalGate

Use this playbook alongside the required project artifacts:

- `automation_boundary_matrix.md` defines where automation is appropriate.
- `human_escalation_design.md` defines where human paths begin and how they work.
- `escalation_contract.yaml` provides optional machine-readable triggers, destinations, SLAs, fallbacks, payload requirements, and durable-state controls.
- `eval_cases.yaml` proves the expected route for routine, ambiguous, risky, and prohibited cases.
- `launch_gate_review.md` records whether the human escalation gate is ready.
- `chatbot_success_metric_stack.md` and observability artifacts track whether escalation preserves durable resolution and trust.

`human_escalation_design.md` remains the required human-readable review artifact. `escalation_contract.yaml` is optional, but `openevalgate check` validates it and its eval-case references when present. Existing projects without the structured contract remain compatible.

## Practitioner Workflow

1. Select one workflow where wrong autonomy, delayed handoff, or missing human review would materially harm users or the business.
2. Define the resolve, clarify, escalate, approval, and refusal boundaries.
3. Write an escalation contract with triggers, risk tiers, destinations, SLAs, fallback behavior, owners, and eval slices.
4. Define the handoff payload using the minimum-sufficient-context principle.
5. Map queues, specialist routes, approval paths, and callback or async fallbacks.
6. Confirm durable workflow state: checkpoints, idempotency, status transitions, timeout handling, and audit events.
7. Add eval cases for under-escalation, over-escalation, late escalation, missing context, wrong destination, approval resume, and prohibited actions.
8. Apply a slice-based release gate and feed incidents back into the eval set.
9. Recertify high-risk escalation contracts as policies, tools, queues, and user behavior change.

## Validate The Evidence

From the repo root:

```bash
openevalgate validate examples/customer_support_assistant/eval_cases.yaml
openevalgate check examples/customer_support_assistant/
openevalgate report examples/customer_support_assistant/
```

The generated report summarizes required-escalation recall, over-escalation, destination accuracy, context preservation, fallback success, resume success, and late escalation. High-risk failures can become hard blockers even when evidence completeness appears healthy.

## Files

```text
docs/playbooks/human-escalation-playbook/
  README.md
  templates/
    escalation-contract.yaml
    handoff-payload-schema.yaml
    queue-routing-worksheet.md
    fallback-and-durable-state-checklist.md
    escalation-release-gate.yaml
    incident-ingestion-template.md
    recertification-checklist.md
  examples/
    customer-support-refund/
      escalation-contract.yaml
      handoff-payload.yaml
      queue-routing-worksheet.md
      escalation-release-gate.yaml
    presales-commercial/
      escalation-contract.yaml
      queue-routing-worksheet.md
    education-integrity/
      escalation-contract.yaml
      queue-routing-worksheet.md
```

## Design Rules

- Do not use "low confidence" as the whole policy. Combine model signals with deterministic risk, authorization, policy, context, repeated-failure, and user-friction checks.
- Do not send every unresolved case to one universal queue. Live handoff, async case, approval queue, callback, fraud review, policy review, and safety review are different products.
- Do not make the user restart the journey after handoff. A handoff is a state transfer, not a redirect.
- Do not optimize escalation rate to zero. Measure whether the right cases escalated at the right time with the right context to the right destination.
- Do not launch high-impact workflows unless fallback, timeout, resume, audit, and rollback behavior are defined.

## Practitioner Rule

Do not ask only:

> Can the agent avoid a human?

Ask:

> What path preserves trustworthy resolution for this workflow when autonomy is no longer the right product decision?
