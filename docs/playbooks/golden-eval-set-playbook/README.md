# Golden Eval Set Playbook

A practical product-manager workflow for turning expected GenAI behavior into
launch-ready eval cases. Use it before model comparisons, prompt rewrites,
tool launches, or rollout decisions.

OpenEvalGate treats a golden eval set as a product-specific behavioral
contract. The cases define what an assistant or agent should do, where it must
stop, and what evidence a release review needs. They do not replace the
business behavior contract, human judgment, or the organizational release
decision.

## What A Golden Eval Set Is

A golden eval set is a curated set of cases that defines what the system should do, must not do, when it should call tools, when it should avoid tools, when it should escalate, and when it should block or refuse.

It is not a generic benchmark. It is product-specific launch evidence.

The product is more than the model. A useful eval set covers the prompt,
retrieval, tools, policy, workflow, human handoff, and recovery behavior that
users actually experience.

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

The deterministic core validates the local evidence package after an external
runner or manual review produces results. It does not execute an LLM, choose a
model, or make an organizational approval decision.

## PM Operating Sequence

| Phase | Product question | OpenEvalGate artifact or output |
| --- | --- | --- |
| 0. Align | What is in scope, prohibited, high risk, and owned? | [Stakeholder alignment brief](templates/stakeholder_alignment_brief.md), assistant scope, behavior contract |
| 1. Map | Which intents, actions, and risk slices need different behavior? | `eval_cases.yaml`, action-risk matrix, automation boundary |
| 2. Collect | Which production, boundary, incident, and drift cases prove the boundary? | Golden eval cases, [incident intake](templates/incident_ingestion_template.md) |
| 3. Grade | What can be checked deterministically, reviewed with a rubric, or adjudicated by a human? | Eval runner output, output-critic rubric, trace evidence |
| 4. Gate | Which slices block, limit, or monitor a release? | [Release-gate template](templates/release_gate_template.yaml), review policy, launch-gate review |
| 5. Learn | Who owns updates, and how does production evidence reopen a decision? | [Review agenda](templates/eval_review_agenda.md), incident-to-regression recipe, report |

### 0. Align Before Writing Cases

The PM leads this phase because expected behavior and acceptable tradeoffs are
product decisions. Complete the stakeholder alignment brief before collecting
prompts. Establish the in- and out-of-scope intents; allowed, prohibited,
approval-required, escalation-required, and refusal behavior; policy sources
of truth; tool boundaries; high-impact failure modes; and decision owners.

Do not continue when stakeholders disagree about a high-risk expected
behavior. That is a product-specification gap, not a model-selection problem.

### 1. Map Behavior and Risk Slices

Start with principal user intents, then define the expected path for each:
answer, clarify, act, require approval, escalate, refuse, or block. Group
cases into slices that can reveal a dangerous regression hidden by an average:

- high-volume, low-risk interactions;
- critical tool eligibility and prohibited actions;
- policy, privacy, authorization, or financial boundaries;
- missing, stale, or contradictory context;
- required escalation, approval, refusal, fallback, and resume behavior;
- known incidents and historical failures; and
- fresh production samples that may indicate drift.

Use contrast families when a small context, permission, or risk change should
change the expected outcome. See the [Synthetic Boundary Case Guide](../../17_synthetic_boundary_case_guide.md).

### 2. Collect Cases From Four Sources

Build the initial set from four complementary sources:

1. **Production-shaped distribution:** representative logs, tickets,
   transcripts, operator workflows, or a safe proxy when the product is new.
2. **Synthetic boundaries:** rare but costly conditions, adversarial requests,
   policy edges, and contrast families that production volume may not expose.
3. **Known failures:** incidents, appeals, overrides, support complaints, and
   prior regressions that must not recur.
4. **Fresh samples:** a rolling, reviewable sample of current behavior used to
   discover drift and gaps in the stable regression set.

Keep source provenance in the case metadata where possible. Synthetic cases
must remain labeled as synthetic; they are not external production evidence.

### 3. Write a Behavioral Contract

Each case needs more than a prompt and a preferred answer. Record user and
relevant policy or retrieved context, expected and unacceptable behavior,
expected route, tool use or non-use, human destination and fallback where
relevant, risk tier, policy reference, source, owner, and required grading.

Use the included examples as structural references, then validate the project
case file before asking an external runner to produce result evidence.

### 4. Choose the Weakest Sufficient Grader

Use deterministic checks whenever the behavior is observable from structured
evidence: tool calls, prohibited actions, route selection, destinations,
required fields, status transitions, and calculated values. Use a rubric for
qualitative communication or policy interpretation that cannot be reduced to a
reliable deterministic check. Reserve human review for ambiguous,
high-impact, or launch-blocking cases.

An LLM judge may be an external evidence producer, but it is not part of the
OpenEvalGate deterministic core. Calibrate any model-based grading against
human review and do not let it replace a check that can be derived from a
trace or structured result.

### 5. Define Slice-Based Release Gates

Use the [release-gate template](templates/release_gate_template.yaml) to make
the decision rules explicit. A slice that cannot affect advancement is a
dashboard metric, not a launch gate. For every blocking slice, define the
threshold, unacceptable failure, exception owner, and resulting action.

Then connect the evidence to an OpenEvalGate review mode:

- **Documentation review:** controls and intended behavior are present, but
  empirical evidence may be absent.
- **Shadow launch:** evidence is being gathered without authorizing the
  requested controlled scope.
- **Controlled launch:** selected, valid behavioral evidence and hard controls
  support a bounded recommendation; this remains distinct from organizational
  approval.

See [Review Modes and Behavioral Sufficiency](../../review-modes.md) and the
[PM controlled-launch review recipe](../../18_product_manager_controlled_launch_review.md).

### 6. Operate the Set

Assign product ownership for expected behavior, engineering ownership for eval
execution, policy or domain ownership for ambiguous adjudication, and
operations ownership for production learning. Review the set after material
model, prompt, retrieval, tool, policy, or workflow changes, and on a regular
cadence for fresh samples and drift.

After an incident, use the
[incident-to-regression recipe](../../19_incident_to_regression_recipe.md) to
classify the gap, create a regression or boundary case, assign mitigation, and
decide whether the release scope needs re-evaluation, re-approval, pause, or
rollback.

## Workflow

1. Align stakeholders on scope, policy, risk, tools, and owners.
2. Define behavior categories and risk slices.
3. Draft cases from historical production, synthetic boundary, known failure, adversarial, regression, and fresh drift sources.
4. Write each case as a behavioral contract.
5. Choose deterministic checks, rubric checks, and human review where appropriate.
6. Define release gates by slice, not only aggregate score.
7. Review the eval set with product, engineering, operations, policy, and domain owners.
8. Feed production incidents and drift samples back into the set.

For consequence-weighted coverage, group synthetic cases into contrast families and grade workflow route, execution trajectory, and final state. See the [Synthetic Boundary Case Guide](../../17_synthetic_boundary_case_guide.md).

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

For a complete project review, run:

```bash
openevalgate validate eval_cases.yaml
openevalgate check .
openevalgate report . --format card
```

Use JSON for automation and the card for a review agenda. A card summarizes
evidence; it does not grant approval.

## PM Review Checklist

- [ ] Stakeholders agree on in-scope, out-of-scope, prohibited, and
  escalation-required behavior.
- [ ] High-impact slices have cases, explicit expected routes, and named
  owners.
- [ ] The set combines production-shaped, synthetic, incident, and fresh
  sample evidence without mislabeling synthetic cases as production evidence.
- [ ] Deterministic checks are used where available; qualitative grading has a
  rubric and calibration plan.
- [ ] Blocking slices, exception owners, rollback triggers, and re-review
  conditions are explicit.
- [ ] Incidents and material changes produce new evidence rather than informal
  exceptions.

## Practitioner Rule

Do not start with “which model is best?”

Start with:

> What behavior must this GenAI product demonstrate before we trust it with users?
