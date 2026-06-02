# Golden Eval Set Playbook

A practical playbook for product teams, domain owners, and builders who need to turn expected GenAI behavior into launch-ready eval cases.

OpenEvalGate treats the golden eval set as the behavioral PRD for a GenAI assistant or agent. This playbook explains how to create that artifact before model comparisons, prompt rewrites, tool launches, or rollout decisions.

## What A Golden Eval Set Is

A golden eval set is a curated set of cases that defines what the system should do, must not do, when it should call tools, when it should avoid tools, when it should escalate, and when it should block or refuse.

It is not a generic benchmark. It is product-specific launch evidence.

## Who Should Use This

- AI product managers defining assistant behavior.
- Domain owners who know policy, operations, edge cases, and business tradeoffs.
- ML/AI engineers building eval harnesses.
- Platform teams standardizing release gates.
- Trust, safety, legal, and compliance reviewers.

## How This Fits OpenEvalGate

Use this playbook to create and review `eval_cases.yaml`. Then use the broader OpenEvalGate project to connect those cases to:

- business behavior contracts,
- action risk matrices,
- output critic rubrics,
- automation boundaries,
- human escalation design,
- eval results,
- launch gate reviews,
- launch readiness reports.

## Workflow

1. Align stakeholders on scope, policy, risk, tools, and owners.
2. Define behavior categories and risk slices.
3. Draft cases from historical production, synthetic boundary, known failure, adversarial, regression, and fresh drift sources.
4. Write each case as a behavioral contract.
5. Choose deterministic checks, rubric checks, and human review where appropriate.
6. Define release gates by slice, not only aggregate score.
7. Review the eval set with product, engineering, operations, policy, and domain owners.
8. Feed production incidents and drift samples back into the set.

## Files In This Playbook

```text
schemas/golden_eval_case_schema.yaml
examples/refund_agent_eval_cases.yaml
examples/education_assistant_eval_cases.yaml
examples/presales_assistant_eval_cases.yaml
templates/stakeholder_alignment_brief.md
templates/release_gate_template.yaml
templates/incident_ingestion_template.md
templates/eval_review_agenda.md
```

## Example Categories

| Example file | Assistant category | What it demonstrates |
| --- | --- | --- |
| `examples/refund_agent_eval_cases.yaml` | Customer support assistant | Refund eligibility, compensation abuse, missing context, and policy bypass. |
| `examples/education_assistant_eval_cases.yaml` | Education assistant | Academic integrity, grounded concept explanation, weak grounding, and learner-support escalation. |
| `examples/presales_assistant_eval_cases.yaml` | Presales assistant | Roadmap overpromise, discount boundaries, competitor claims, and security/compliance escalation. |

## Validate The Examples

From the repo root:

```bash
python -m openevalgate.cli validate docs/playbooks/golden-eval-set-playbook/examples/refund_agent_eval_cases.yaml
python -m openevalgate.cli validate docs/playbooks/golden-eval-set-playbook/examples/education_assistant_eval_cases.yaml
python -m openevalgate.cli validate docs/playbooks/golden-eval-set-playbook/examples/presales_assistant_eval_cases.yaml
```

## Practitioner Rule

Do not start with “which model is best?”

Start with:

> What behavior must this GenAI product demonstrate before we trust it with users?
