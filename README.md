# OpenEvalGate

Launch gates, not vibe checks, for production GenAI.

OpenEvalGate is an open-source launch-readiness framework for GenAI assistants and agents. It helps teams define expected behavior, build golden eval sets, feed back candidate eval results, compare models, classify action risk, design output critics, and generate launch-readiness reports.

Most GenAI demos answer: “Can the model do this once?”

Production teams need to answer: “Can this system do this reliably, safely, cost-effectively, and observably across real users?”

OpenEvalGate provides practical templates and lightweight tooling for that second question.

## What problem this solves

Teams often adopt eval, tracing, and observability tools before they have agreed on the launch gates those tools should support. OpenEvalGate sits one layer above tools such as LangSmith, Braintrust, Arize Phoenix, Langfuse, Promptfoo, DeepEval, and Guardrails AI.

Those tools help run evals, observe traces, compare prompts, monitor production, or enforce runtime checks. OpenEvalGate helps teams decide what must be true before launch.

## Who it is for

- AI product managers turning product scope into testable behavior.
- ML and AI engineers building assistant and agent eval suites.
- GenAI platform teams standardizing launch review across teams.
- Trust, safety, legal, and compliance teams reviewing product risk.
- Startup founders who need a practical launch checklist before real users arrive.

## What it is not

OpenEvalGate is not a full eval platform, tracing system, agent framework, model benchmark, prompt library, or guardrails runtime. It does not call LLM APIs. It does not send telemetry. It does not require cloud services.

## Core concepts

- **Golden eval set as behavioral PRD:** The golden eval set is the clearest executable description of expected assistant behavior.
- **Historical production cases:** Real user cases that represent recurring demand and known failure modes.
- **Synthetic boundary cases:** Designed cases that test policy edges, escalation thresholds, and unsafe shortcuts.
- **Fresh drift samples:** Recently observed cases that keep launch readiness honest as users, products, and policies change.
- **Model garden and internal arena:** Compare candidate models on your product behavior, not only public benchmarks.
- **Reasoning vs deterministic enforcement:** Use LLMs for reasoning; use deterministic systems for enforcement.
- **SOP/context compilation:** Compile the policy context the model needs instead of dumping the whole SOP into the prompt.
- **Input filter:** Decide what the assistant should accept, refuse, route, or escalate before generation.
- **Output critic:** Review proposed responses for grounding, policy alignment, safety, helpfulness, and escalation judgment.
- **Response admission gate:** The main LLM proposes; the output critic decides whether to show, revise, escalate, or block.
- **Eval result feedback:** Candidate assistant outputs and grading results are saved in `eval_results.csv` and optional `eval_runs/` files.
- **Action risk taxonomy:** Classify tool and agent actions by harm potential before allowing execution.
- **Launch readiness report:** Convert evidence into a launch recommendation, score, mitigations, and owner signoff.

## Quickstart

```bash
python -m pip install -e ".[dev]"
openevalgate validate examples/customer_support_assistant/eval_cases.yaml
openevalgate check examples/customer_support_assistant/
openevalgate report examples/customer_support_assistant/ --output examples/customer_support_assistant/generated_launch_report.md
```

## Example workflow

1. Start from `templates/ai_assistant_prd.md` and define supported and unsupported behavior.
2. Build `eval_cases.yaml` from historical production cases, synthetic boundary cases, adversarial cases, and regression cases.
3. Run the candidate assistant externally using Braintrust, Promptfoo, DeepEval, LangSmith, an internal harness, or manual review.
4. Save result rows in `eval_results.csv` and optional observed outputs under `eval_runs/`.
5. Use the model arena scorecard to compare candidate models on product-specific behavior.
6. Use the action risk matrix to classify tool calls and agent actions.
7. Define output critic criteria and human escalation thresholds.
8. Fill out the launch gate review.
9. Run the CLI to generate a launch readiness report.

## Repo structure

```text
docs/       Opinionated guides for production GenAI launch readiness.
templates/  Copyable Markdown, YAML, and CSV launch review templates.
examples/   Example assistant projects users can adapt.
openevalgate/  Small local Python CLI.
tests/      Schema, project check, scoring, and report tests.
```

## CLI usage

Validate a golden eval YAML file:

```bash
openevalgate validate examples/customer_support_assistant/eval_cases.yaml
```

Check required launch gate files:

```bash
openevalgate check examples/customer_support_assistant/
```

Generate a Markdown launch readiness report:

```bash
openevalgate report examples/customer_support_assistant/ --output examples/customer_support_assistant/generated_launch_report.md
```

OpenEvalGate does not execute candidate LLM systems in V1. It ingests outputs and grades from external eval runners through `eval_results.csv`.

## How to contribute

Start with templates, examples, and docs. The best contributions make the framework more useful in a real launch review meeting. Keep the CLI small, deterministic, local-first, and dependency-light.

See `CONTRIBUTING.md` for development setup and project boundaries.

## Roadmap

- More assistant examples across regulated and operational domains.
- Stronger CSV and Markdown validation.
- Optional export formats for launch review artifacts.
- Mappings to common eval and observability tools without becoming one.
- Versioned readiness schemas for teams that need stricter governance.
