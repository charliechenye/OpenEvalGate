# Output Critic Guide

An output critic is a reviewer for proposed assistant responses. It does not need to be fancy. In V1 it can be a rubric used by humans, eval scripts, or future LLM judges.

## Required dimensions

- Grounding: claims are supported by retrieved context.
- Policy alignment: response respects applicable policy.
- Helpfulness: user receives a useful next step.
- Action safety: tools and actions respect risk controls.
- Escalation judgment: cases beyond automation scope route correctly.

## Admission decisions

- **Show:** Response is safe and useful.
- **Revise:** Response has fixable quality, clarity, or grounding issues.
- **Escalate:** Human review is required.
- **Block:** Response or action is unsafe, prohibited, or policy-inconsistent.

## Launch gate

Before launch, the critic should be tested on boundary, adversarial, and regression cases. A critic that only approves happy-path outputs is not a launch control.
