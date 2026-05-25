# Getting Started For Practitioners

OpenEvalGate is not an app to deploy. It is a launch-readiness operating kit for production GenAI assistants and agents.

Use it to answer:

- What behavior are we willing to launch?
- What behavior would damage user trust?
- What must be evaluated before launch?
- What evidence says this system is ready?
- What must be escalated, blocked, or reviewed by a human?

## The Fastest Path

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

Start with the required launch-readiness files:

```text
assistant_prd.md
business_behavior_contract.md
trust_preservation_review.md
eval_cases.yaml
action_risk_matrix.csv
automation_boundary_matrix.md
human_escalation_design.md
output_critic_rubric.csv
chatbot_success_metric_stack.md
launch_gate_review.md
```

These files define what the assistant is allowed to do, what it must not do, when it should escalate, how tool risk is controlled, and how launch readiness will be judged.

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

- readiness score
- launch recommendation
- hard blockers
- trust preservation evidence
- business behavior contract evidence
- golden eval coverage
- tail-risk/P0 failure coverage
- automation boundary and escalation evidence
- tool/action safety evidence
- metric stack evidence
- required mitigations
- suggested next actions

## Required Mindset

Do not optimize only for containment.

Containment tells you whether the bot absorbed the session. Resolution tells you whether the user's problem was solved. Trust tells you whether the platform relationship survived.

OpenEvalGate is useful when teams treat launch readiness as a cross-functional decision, not a model-quality score.
