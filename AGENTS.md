# AGENTS.md

## Project Purpose

OpenEvalGate is a local, deterministic release-assurance framework for evidence-backed launch decisions for production AI assistants and agents.

It is not an eval runner, hosted governance platform, runtime guardrail, or compliance certification product. The deterministic core must not execute LLM APIs.

## Non-Negotiable Trust Invariants

- Missing, invalid, duplicated, ambiguous, or contradictory evidence must fail closed.
- When provenance or freshness is evaluated, stale evidence must not authorize launch.
- Diagnostic values must not silently become policy inputs.
- Critical-control failures and hard blockers override aggregate scores.
- A documentation score alone cannot authorize launch.
- Synthetic examples must not be presented as external production evidence.
- Changes must preserve deterministic and reproducible outputs unless a semantic contract intentionally changes.

## Default Agent Workflow

1. Verify branch, HEAD, and clean working-tree state.
2. Read this file.
3. Use [docs/architecture/code-map.md](docs/architecture/code-map.md) to identify the smallest relevant source and test set.
4. Read only directly relevant files.
5. Implement one coherent change.
6. Run focused validation while iterating.
7. Run broader validation once, near completion, only when required by [docs/development/validation-matrix.md](docs/development/validation-matrix.md).
8. Run `git diff --check` and fix all reported whitespace errors before inspecting the final diff; commit only when explicitly requested.

## Context And Token Discipline

- Start with `AGENTS.md`, the relevant code-map row, and two to five task-specific files.
- Use `rg`, `git grep`, file listings, and targeted line ranges before opening large files.
- Do not scan all documentation, examples, tests, or generated reports by default.
- Do not print entire large files or full successful command logs.
- Use quiet focused tests; add verbosity only to diagnose a failure.
- Do not run the full test suite repeatedly.
- Keep one coding-agent thread scoped to one coherent PR.
- Expand context only when an import, dependency, failing test, or contract boundary requires it.

These defaults save context; they are not excuses to omit evidence necessary for correctness.

## Scope And Dependency Guards

- No unrelated refactoring.
- No new production dependency unless explicitly requested.
- No schema, blocker-ID, exit-code, report, scoring, or compatibility change outside the task.
- No generated-report update unless semantic output intentionally changes.
- No roadmap or release-status update unless explicitly included.
- Do not create or amend a commit unless the task explicitly requests it.
- No pushing unless explicitly requested.
- If the branch, expected HEAD, or working-tree state is unexpected, stop and report it.
- Do not reset, rebase, amend, discard, or overwrite unrelated work.

## Validation Routing

Use [docs/development/validation-matrix.md](docs/development/validation-matrix.md) instead of duplicating the full command matrix here.

Core principle: run focused checks during iteration, then the smallest sufficient broader validation once before completion. Documentation-only changes do not require the full Python test suite unless they alter executable examples, commands, packaging metadata, or CI behavior.

## Generated Artifacts

- Checked-in canonical reports are generated artifacts.
- Never edit canonical reports manually.
- Regenerate only affected examples after an intentional report-semantic change.
- Verify byte-for-byte reproduction.
- Avoid reading canonical reports when the task does not affect report content.

## Final Response Contract

Report only:

- files changed;
- behavior changed;
- focused and broader validation run;
- generated artifacts changed or unchanged;
- remaining risks or deferred work;
- commit status.

Do not repeat long command transcripts or summarize every file inspected.

## Navigation Links

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [.github/pull_request_template.md](.github/pull_request_template.md)
- [docs/architecture/code-map.md](docs/architecture/code-map.md)
- [docs/development/validation-matrix.md](docs/development/validation-matrix.md)
