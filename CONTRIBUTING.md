# Contributing to OpenEvalGate

OpenEvalGate is a launch-readiness framework, not another eval platform. Contributions should help teams make better launch decisions before a GenAI assistant or agent reaches real users.

By participating, you agree to follow the [Code of Conduct](CODE_OF_CONDUCT.md). Suspected vulnerabilities must be reported privately according to [SECURITY.md](SECURITY.md).

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

## Development setup

OpenEvalGate supports Python 3.10 through 3.13.

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Run the complete local validation set before opening a pull request:

```bash
python -m pytest
python -m compileall -q openevalgate
python -m build
git diff --check
```

Run `git diff --check` before every commit or pull request. Fix all reported trailing whitespace and other whitespace errors before handoff; GitHub's whitespace validation should be a final confirmation, not the first detection.

Try the canonical workflow:

```bash
openevalgate validate examples/customer_support_assistant/eval_cases.yaml
openevalgate check examples/customer_support_assistant/
openevalgate report examples/customer_support_assistant/ --output /tmp/customer_support_report.md
diff -u examples/customer_support_assistant/generated_launch_report.md /tmp/customer_support_report.md
```

Repeat report-reproducibility checks for presales and education examples when a change affects validation, scoring, policy, or reporting.

## Design expectations

OpenEvalGate treats missing, invalid, duplicated, stale, and ambiguous evidence conservatively. A contribution that changes policy behavior should explain:

- the launch-readiness problem being solved;
- the trusted evidence source;
- the fail-closed behavior;
- the blocker or report output affected;
- compatibility with existing scores, blocker IDs, constructors, templates, and CLI behavior;
- the deterministic tests that prove permissive and blocking paths.

Diagnostic information must not silently become policy input. A high score must not override a hard blocker.

## Tests and generated artifacts

Tests should cover malformed and boundary inputs, not only successful examples. When generated reports change intentionally:

1. explain why the semantic output changed;
2. regenerate every affected canonical report;
3. verify byte-for-byte reproducibility;
4. keep manually maintained copies out of the repository.

When editing any evidence file covered by a SHA-256 digest, including removing trailing whitespace, recompute the file digest and update every dependent artifact index or manifest digest before running validation. Treat whitespace cleanup as a byte change, not a prose-only change.

## Evidence hygiene

Use synthetic or fully redacted examples. Do not commit:

- credentials or API keys;
- private customer or employee data;
- proprietary prompts or internal policy text;
- confidential evaluation traces;
- production incident details that identify an organization or user.

## Pull requests

Keep each pull request focused on one coherent policy, validation, documentation, or adoption change. Complete the pull request template, document intentional non-goals, and update user-facing documentation when behavior changes.

Cross-domain escalation contributions are especially useful. A good example should name the stopping boundary, accountable human destination, minimum handoff context, fallback behavior, expected workflow route, and evidence that the workflow resumes safely.

## Style

Use plain language. Avoid hype. Templates should be specific enough for a launch review meeting and simple enough for a startup team to adopt in an afternoon.
