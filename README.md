# OpenEvalGate

Launch gates, not vibe checks, for production GenAI.

OpenEvalGate is an open-source launch-readiness and trust-preservation framework for GenAI assistants and agents. It helps teams define expected behavior, build golden eval sets, feed back candidate eval results, compare models, classify action risk, design output critics, define automation boundaries, and generate launch-readiness reports.

Most GenAI demos answer: “Can the model do this once?”

Production teams need to answer: “Can this system do this reliably, safely, cost-effectively, observably, and trustworthily across real users?”

## Why Trust Preservation?

Production GenAI is ultimately a trust-preservation problem.

User trust is easier to break than earn. Containment is not resolution. Average performance is not launch readiness. The assistant is part of the platform relationship, not just a support surface.

Production AI should optimize for durable resolution, bounded downside, graceful escalation, and long-term user trust, not short-term dashboard wins.

See [Research Evidence And Competitive Landscape](docs/16_research_evidence_and_competitive_landscape.md) for supporting standards, guidance, and adjacent projects.

## What OpenEvalGate Is

- A launch-readiness framework.
- A trust-preservation framework.
- A cross-functional review system.
- A template library.
- A lightweight local CLI.
- A way to generate launch-readiness reports.

## What OpenEvalGate Is Not

OpenEvalGate is not a full eval platform, tracing system, monitoring platform, agent framework, model benchmark, prompt library, guardrails runtime, or replacement for existing LLMOps tools. It does not call LLM APIs. It does not send telemetry. It does not require cloud services.

You can use OpenEvalGate alongside LangSmith, Braintrust, Phoenix, Promptfoo, DeepEval, Guardrails AI, Langfuse, Helicone, or your internal LLMOps stack. OpenEvalGate defines launch-readiness evidence; your tool stack can execute, trace, monitor, or automate parts of that process.

For a detailed comparison, see [Research Evidence And Competitive Landscape](docs/16_research_evidence_and_competitive_landscape.md).

## Who It Is For

- AI Product Managers.
- ML / AI Engineers.
- GenAI Platform Teams.
- Trust, Safety, Legal, and Compliance Teams.
- Business / Operations / Policy Owners.
- Startup founders building AI assistants or agents.

## Core Concepts

- **Golden eval set as behavioral PRD:** The clearest executable description of expected assistant behavior.
- **Agent behavior as business contract:** Golden evals are the operating contract between business intent and agent execution.
- **Trust preservation:** The system should help users complete the task now while preserving future trust.
- **Tail-risk/P0 evaluation:** Rare does not mean acceptable; tail failures define trust.
- **Automation boundary:** Define where automation is appropriate and where it becomes risky.
- **Human escalation as control surface:** Escalation protects users, business operations, and platform trust.
- **Domain-owner feedback loop:** Domain owners review traces, propose evals, flag policy nuance, and approve high-risk behavior changes.
- **Metric stack beyond containment:** Track efficiency, quality, journey resolution, and business/trust outcomes.
- **Eval result feedback:** Candidate outputs and grading results are saved in `eval_results.csv` and optional `eval_runs/` files.

## Quickstart

New to the repo? Start with `docs/00_getting_started_for_practitioners.md`.

```bash
python -m pip install -e ".[dev]"
openevalgate validate examples/customer_support_assistant/eval_cases.yaml
openevalgate check examples/customer_support_assistant/
openevalgate report examples/customer_support_assistant/ --output examples/customer_support_assistant/generated_launch_report.md
```

## Example Workflow

1. Define assistant scope and unsupported use cases.
2. Complete the business behavior contract and trust-preservation review.
3. Build golden eval cases from historical, boundary, adversarial, tail-risk, regression, and drift samples.
4. Define automation boundaries, tool/action safety, output critic criteria, and human escalation design.
5. Run the candidate assistant externally using your eval or LLMOps stack.
6. Save results in `eval_results.csv` and observed outputs in `eval_runs/`.
7. Fill out the launch gate review.
8. Generate the launch readiness report.

## Launch Gates

1. Scope gate
2. Trust preservation gate
3. Business behavior contract gate
4. Golden eval gate
5. Tail-risk / P0 failure mode gate
6. Model selection gate
7. Model arena gate
8. Grounding gate
9. SOP/policy compilation gate
10. Tool/action safety gate
11. Automation boundary gate
12. Human escalation gate
13. Input filter gate
14. Output critic gate
15. Domain-owner feedback loop gate
16. Observability gate
17. Cost/latency gate
18. Journey metric / durable resolution gate
19. Business trust metric gate
20. Drift monitoring gate
21. Rollback gate
22. Owner signoff gate

## Readiness Scoring

OpenEvalGate uses a 100-point trust-weighted score:

- Scope readiness: 5
- Trust preservation readiness: 8
- Business behavior contract readiness: 7
- Golden eval readiness: 10
- Tail-risk / P0 failure readiness: 10
- Model selection / arena readiness: 7
- Grounding readiness: 6
- SOP/policy compilation readiness: 5
- Tool/action safety readiness: 8
- Automation boundary readiness: 6
- Human escalation readiness: 5
- Input/output perimeter readiness: 6
- Domain-owner feedback loop readiness: 4
- Observability readiness: 5
- Cost/latency readiness: 3
- Journey/business metrics readiness: 5

Recommendation bands:

- 85-100: Ready for controlled launch
- 70-84: Conditional launch
- 50-69: Shadow launch only
- Below 50: Not ready

## Hard Blockers

Regardless of score, OpenEvalGate recommends `Not ready` when:

- Scope is missing or failed.
- Golden eval set is missing or invalid.
- Tail-risk/P0 review is missing or failed for high-impact workflows.
- A high-risk action lacks deterministic enforcement or human approval.
- High-risk or low-confidence cases lack an escalation path.
- Rollback is missing or not passing.
- Owner signoff is missing or not passing.
- Observability/monitoring is missing or failed.

## Templates

The repo includes templates for assistant PRDs, golden eval cases, eval results, business behavior contracts, domain-owner feedback, behavior change requests, P0 failure modes, automation boundaries, human escalation design, chatbot metric stacks, trust-preservation reviews, launch gates, and launch readiness reports.

## Playbooks

- [Golden Eval Set Playbook](docs/playbooks/golden-eval-set-playbook/README.md): a practitioner guide for PMs and domain owners turning expected behavior into golden eval cases, release gates, and incident feedback loops.

## Repo Structure

```text
docs/       Opinionated guides for production GenAI launch readiness.
templates/  Copyable Markdown, YAML, and CSV launch review templates.
examples/   Example assistant projects users can adapt.
openevalgate/  Small local Python CLI.
tests/      Schema, project check, scoring, hard-blocker, and report tests.
```

## Business Owner Participation

Business and domain owners often know the ground truth better than the central AI team. They should review eval cases, define unacceptable behavior, approve risky behavior changes, own escalation thresholds, and monitor drift through controlled self-service workflows.

## CLI Usage

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

## How To Contribute

Start with templates, examples, and docs. The best contributions make the framework more useful in a real launch review meeting. Keep the CLI small, deterministic, local-first, and dependency-light.
