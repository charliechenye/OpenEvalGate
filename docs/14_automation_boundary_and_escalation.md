# Automation Boundary And Escalation

Over-automation is a production AI failure mode.

The right question is not "how much can we automate?" The better question is "where is automation appropriate, and where does it become risky?"

Human intervention is not failure. It is a control surface that protects users, operators, business outcomes, and platform trust when autonomous resolution is no longer the right product decision.

This is especially important for high-impact or high-agency systems. The [OWASP Top 10 for LLM Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/) calls attention to excessive agency and related risks, while AI governance frameworks emphasize oversight and accountable operation.

## Boundary Routes

For each workflow, define whether the assistant should:

- Resolve directly.
- Clarify with a bounded question.
- Recommend or pause for human approval.
- Escalate to the right human destination.
- Refuse or block.

These are separate product paths. A clarification is not an escalation. An approval queue is not a live handoff. A refusal is not a support ticket. Treating them as one generic fallback hides risk and makes launch evidence weak.

## Automation Boundary Matrix

| Risk level | Confidence level | Action route | Required control |
| --- | --- | --- | --- |
| Low | High | Resolve directly | Grounding, policy, and ownership checks pass. |
| Low | Low | Clarify | Ask a targeted question with a retry budget. |
| Medium | High | Recommend or prepare action | Deterministic policy/tool checks run before acting. |
| Medium | Low | Escalate | Handoff destination, payload, SLA, and fallback exist. |
| High | High | Human approval | Pause execution before action; resume from checkpoint. |
| High | Low | Escalate or block | Specialist route or refusal rule is deterministic. |
| Prohibited | Any | Block | Prevent execution; explain permitted next step. |

## Escalation Control Surface

The escalation control surface combines probabilistic model signals with deterministic system controls:

```text
Intent + context + policy + risk + user-friction signals
                          |
                          v
              Escalation Control Surface
                          |
                          v
       Resolve | Clarify | Escalate | Approval | Refuse
```

Useful triggers include:

- Intent ambiguity.
- Missing, stale, or contradictory context.
- Policy ambiguity or exception-heavy SOPs.
- Authorization thresholds or high-impact actions.
- Safety, compliance, fraud, abuse, or account-impacting signals.
- Repeated failed attempts or repeat contact.
- Explicit user request for a human.
- Tool outage, dependency degradation, or queue saturation.

Do not rely on "low model confidence" alone. A model can be confident and still propose an unauthorized action. A deterministic policy check should override model confidence.

## Human Path Requirements

A human escalation path is launch-ready only when the team can answer:

| Requirement | Question |
| --- | --- |
| Destination | Which human team can actually resolve this exception? |
| SLA | What response-time promise applies to this path? |
| Handoff payload | What minimum sufficient context transfers to the human? |
| Fallback | What happens if the queue, reviewer, callback, or dependency fails? |
| Durable state | Can the workflow pause, persist, and resume safely? |
| Idempotency | Can the system avoid duplicate execution after approval or retry? |
| Audit | Are triggers, decisions, versions, and reviewer actions recorded? |
| Eval coverage | Which cases prove under-escalation, over-escalation, late escalation, and wrong-destination behavior? |
| Metrics | How will the team know whether escalation preserves durable resolution? |

## Metrics Beyond Handoff Rate

Do not optimize escalation rate to zero. Measure escalation quality:

- Escalation precision: escalated cases that truly needed human handling.
- Escalation recall: cases needing a human that were actually escalated.
- Time from first escalation signal to handoff.
- Time to appropriate human destination.
- Context-preservation rate.
- Correct-destination rate.
- Fallback activation rate.
- Resume success and duplicate-action rate.
- True resolution and repeat-contact rate by path.

Containment is useful only when true resolution, customer effort, safety, and downstream trust remain healthy.

## OpenEvalGate Artifacts

Use the required project artifact `human_escalation_design.md` to document the production escalation path. Use `automation_boundary_matrix.md` to define when autonomy is appropriate. Use `eval_cases.yaml` to test the expected route for routine, ambiguous, risky, prohibited, approval-required, and dependency-failure cases.

For deeper workflow design, copy the optional templates from [Human Escalation Playbook](playbooks/human-escalation-playbook/README.md):

- Escalation contract.
- Handoff payload schema.
- Queue routing worksheet.
- Fallback and durable-state checklist.
- Escalation release gate.
- Incident ingestion template.
- Recertification checklist.

## Practitioner Rule

Escalation is not where architecture ends. It is where architecture proves whether automation is preserving trust.
