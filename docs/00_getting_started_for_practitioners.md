# Getting Started For Practitioners

OpenEvalGate is a local release-assurance toolkit for production AI assistants and agents. It is not an application runtime or an eval runner. It helps teams assemble, validate, and review evidence for a bounded review stage after candidate-system execution has happened elsewhere.

Use it to answer:

- What behavior are we willing to launch?
- What behavior would damage user trust?
- What must be evaluated before launch?
- What evidence supports the requested review stage?
- What must be escalated, blocked, or reviewed by a human?

## The Fastest Path

For a new review project, start with a minimal deterministic scaffold:

```bash
openevalgate init my_assistant --profile minimal
cd my_assistant
openevalgate validate eval_cases.yaml
openevalgate check .
openevalgate report . --format card
```

The scaffold contains synthetic placeholders, not production evidence. Replace
them before using the result in a release decision. The existing flagship
scenario remains useful when you want a complete reference package:

Start with the flagship example:

```text
examples/customer_support_assistant/
```

Copy it into a new project folder:

```bash
cp -r examples/customer_support_assistant examples/my_assistant
```

Then edit the copied files for your assistant.

On Windows PowerShell:

```powershell
Copy-Item -Recurse examples/customer_support_assistant examples/my_assistant
```

## What To Fill Out First

Start with the required release-review files:

```text
assistant_prd.md
business_behavior_contract.md
trust_preservation_review.md
eval_cases.yaml
action_risk_matrix.csv
automation_boundary_matrix.md
human_escalation_design.md
escalation_contract.yaml (optional structured evidence)
output_critic_rubric.csv
chatbot_success_metric_stack.md
launch_gate_review.md
```

These files define what the assistant is allowed to do, what it must not do, when it should escalate, how tool risk is controlled, and how evidence will be assessed for the requested review stage.

## Human Escalation Path

Use this path when the assistant can encounter ambiguity, high-impact actions, specialist risk, repeated failure, or an explicit request for a person.

1. Define `resolve`, `clarify`, `approval`, `escalate`, and `refuse` boundaries in `automation_boundary_matrix.md` and `human_escalation_design.md`.
2. Copy `templates/escalation_contract.yaml` into the project and define trigger IDs, destinations, SLAs, fallback behavior, payload requirements, ownership, and durable resume controls.
3. Add `expected_workflow_route` and `expected_handoff` to relevant eval cases.
4. Record actual destinations, payload completeness, fallback, resume, and late-escalation outcomes in `eval_results.csv`.
5. Run `openevalgate check` to validate contract references and `openevalgate report` to calculate escalation quality.
6. Treat high-risk under-escalation, wrong destination, missing context, or unsafe resume as launch blockers.

The fastest examples to inspect are:

```text
examples/customer_support_assistant/escalation_contract.yaml
examples/presales_assistant/escalation_contract.yaml
examples/education_assistant/escalation_contract.yaml
```

## Product / Business Owner Path

If you are a product manager, operations owner, policy owner, or trust/safety reviewer, focus first on the business behavior and trust artifacts:

```text
assistant_prd.md
business_behavior_contract.md
trust_preservation_review.md
automation_boundary_matrix.md
human_escalation_design.md
chatbot_success_metric_stack.md
launch_gate_review.md
```

Your job is to define:

- supported and unsupported use cases
- expected behavior
- unacceptable behavior
- escalation thresholds
- compensation or action policy
- user trust risks
- business metrics that should not be harmed
- hard blockers before launch

The most important question is:

> Would this assistant help users complete the task now while preserving trust for future interactions?

## Builder / Engineer Path

If you are an engineer or platform builder, focus on making the launch artifacts testable:

```text
eval_cases.yaml
action_risk_matrix.csv
output_critic_rubric.csv
eval_results.csv
eval_runs/
launch_gate_review.md
```

Every populated action-risk row must include a nonblank `action`, a
`risk_tier` of `low`, `medium`, `high`, or `prohibited`, and a
`human_review_required` value of `true` or `false`. Any invalid row makes the
whole matrix untrusted for policy decisions until the artifact is repaired.

For multi-workflow or multi-agent systems, optionally add:

```text
routing_policy.yaml
```

Use it to record each bounded workflow or subagent, its approved fixed or adaptive model assignment, deterministic or human no-model paths, mandatory controls, eval evidence, fallbacks, observability, and rollback. `openevalgate check` validates the policy when present.

Install locally:

```bash
python -m pip install -e ".[dev]"
```

Validate the golden eval set:

```bash
openevalgate validate examples/my_assistant/eval_cases.yaml
```

Check the project structure:

```bash
openevalgate check examples/my_assistant/
```

Generate a launch readiness report:

```bash
openevalgate report examples/my_assistant/ --output examples/my_assistant/generated_launch_report.md
```

Use `openevalgate report . --format json` for CI or internal tooling. Add
`--fail-on-blocked` when the report command should return exit code `1` for a
blocked recommendation. The default report command continues to generate a
report without changing its existing exit behavior.

## Where Eval Outputs Feed Back

OpenEvalGate does not run the model or call LLM APIs.

Run your candidate assistant externally using Braintrust, Promptfoo, DeepEval, LangSmith, Phoenix, Langfuse, Helicone, an internal harness, or manual review.

Then feed results back into the project:

```text
eval_results.csv
eval_runs/
```

The loop is:

```text
eval_cases.yaml
  -> external candidate assistant run
  -> eval_results.csv + eval_runs/
  -> openevalgate report
  -> launch gate mitigations / new eval cases
```

Use `eval_results.csv` for one row per evaluated case. Use `eval_runs/` to store important observed outputs, especially failures or disputed cases.

## What A Launch Review Should Produce

By the end of the process, your project should produce:

```text
generated_launch_report.md
```

The report should make clear:

- evidence completeness score
- evidence package band
- behavioral evidence status
- critical-control status
- maximum permitted stage
- final launch recommendation
- recommended next action
- hard blockers
- trust preservation evidence
- business behavior contract evidence
- golden eval coverage
- tail-risk/P0 failure coverage
- automation boundary and escalation evidence
- destination, SLA, fallback, context-preservation, and durable-resume evidence
- tool/action safety evidence
- metric stack evidence
- required mitigations
- suggested next actions

The evidence-completeness model and launch gates are documented in [Launch Gates and Evidence Completeness Scoring](launch-gates-and-evidence-scoring.md). The requirements for documentation, shadow-launch, and controlled-launch review are documented in [Review Modes and Behavioral Sufficiency](review-modes.md).

## Required Mindset

Do not optimize only for containment.

Containment tells you whether the bot absorbed the session. Resolution tells you whether the user's problem was solved. Trust tells you whether the platform relationship survived.

OpenEvalGate is useful when teams treat release review as a bounded cross-functional decision, not a universal readiness verdict or model-quality score.
