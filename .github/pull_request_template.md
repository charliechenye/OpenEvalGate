## Summary

Describe the problem and the smallest coherent change in this pull request.

## Launch-readiness impact

Explain which evidence, policy, blocker, score, CLI, report, template, or contributor workflow changes.

## Trust-boundary review

- What happens when evidence is missing, invalid, duplicated, stale, or ambiguous?
- Can this change make an unsafe or unsupported state appear permissive?
- Are diagnostic values clearly separated from policy inputs?

## Compatibility

Describe any effect on:

- CLI commands or exit codes;
- scoring weights or canonical scores;
- blocker IDs or launch recommendations;
- schemas, templates, or generated reports;
- public dataclasses or positional constructors;
- existing example projects.

## Validation

List the commands and focused tests run.

- [ ] `python -m pytest`
- [ ] `python -m compileall -q openevalgate`
- [ ] Canonical `validate`, `check`, and `report` smoke tests
- [ ] Canonical generated reports reproduce without diffs
- [ ] `git diff --check`
- [ ] `python -m build` when packaging or metadata changes

## Documentation and evidence hygiene

- [ ] User-facing behavior is documented.
- [ ] Tests cover permissive and fail-closed paths.
- [ ] Examples contain only synthetic or redacted evidence.
- [ ] No credentials, private customer data, proprietary prompts, or confidential traces are included.
- [ ] Attribution and reused material are documented where applicable.

## Deferred work

List intentional non-goals or follow-up issues so the PR does not imply broader readiness than it implements.
