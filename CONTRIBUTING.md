# Contributing to OpenEvalGate

OpenEvalGate is a launch-readiness framework, not another eval platform. Contributions should help teams make better launch decisions before a GenAI assistant or agent reaches real users.

## Good contributions

- Better launch review templates.
- Clearer golden eval schema guidance.
- Example projects for real assistant categories.
- Domain-specific escalation contracts and handoff examples.
- Incident-derived cases for under-escalation, wrong destination, missing context, late escalation, or failed resume.
- Queue, SLA, fallback, and durable-state patterns that remain framework-neutral.
- Small CLI improvements that keep the project local-first.
- Tests that make validation and reporting behavior more predictable.

## Non-goals for V1

- Web UI.
- Hosted service.
- Authentication.
- Telemetry.
- LLM API calls.
- Tracing or observability backends.
- Runtime guardrail enforcement.

## Development

```bash
python -m pip install -e ".[dev]"
python -m pytest
```

Try the example workflow:

```bash
openevalgate validate examples/customer_support_assistant/eval_cases.yaml
openevalgate check examples/customer_support_assistant/
openevalgate report examples/customer_support_assistant/ --output examples/customer_support_assistant/generated_launch_report.md
```

Cross-domain escalation contributions are especially useful. A good example should name the stopping boundary, accountable human destination, minimum handoff context, fallback behavior, expected workflow route, and evidence that the workflow resumes safely.

## Style

Use plain language. Avoid hype. Templates should be specific enough for a launch review meeting and simple enough for a startup team to adopt in an afternoon.
