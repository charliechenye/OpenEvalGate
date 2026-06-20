# Iteration 2: Public Repository and Release Readiness

## Objective

Make OpenEvalGate reproducible, attributable, secure, understandable, and easy to adopt before the repository becomes public.

This iteration should not expand product scope. It should make the existing framework trustworthy to engineers, practitioners, contributors, and reviewers.

## P0.1 Add Continuous Integration

Add a required GitHub Actions workflow covering:

- [ ] Python 3.10
- [ ] Python 3.11
- [ ] Python 3.12
- [ ] Python 3.13
- [ ] Full `pytest` suite
- [ ] Package build
- [ ] Wheel installation in a clean environment
- [ ] CLI smoke tests
- [ ] Canonical-example validation
- [ ] Generated-report reproducibility
- [ ] Linting and formatting
- [ ] Type checking
- [ ] Dependency review
- [ ] CodeQL or an equivalent lightweight security scan

### Required Smoke Tests

```bash
python -m build
python -m pip install dist/*.whl
openevalgate --version
openevalgate validate examples/customer_support_assistant/eval_cases.yaml
openevalgate check examples/customer_support_assistant/
openevalgate report examples/customer_support_assistant/
openevalgate check examples/presales_assistant/
openevalgate check examples/education_assistant/
```

### Acceptance Criteria

- Every pull request runs required CI checks.
- The release branch cannot merge with failed required checks.
- Committed generated reports match current CLI output.
- A wheel installed in a clean environment exposes a working CLI.

## P0.2 Configure Repository Protection

- [ ] Require pull requests for changes to the default branch.
- [ ] Require CI status checks.
- [ ] Require branches to be up to date before merge.
- [ ] Disable force pushes to the default branch.
- [ ] Enable secret scanning and dependency alerts where available.
- [ ] Prefer squash merging for a readable public history.
- [ ] Decide whether to rename the default branch from `master` to `main` before public launch.

## P0.3 Establish Authorship and Citation

- [ ] Set the package author to `Chenye (Charlie) Zhu`.
- [ ] Update copyright to `Chenye Zhu and OpenEvalGate contributors`.
- [ ] Add maintainer contact metadata.
- [ ] Add `CITATION.cff`.
- [ ] Add `AUTHORS.md`.
- [ ] Define how contributors are credited.
- [ ] Add repository, documentation, issues, and changelog URLs to `pyproject.toml`.
- [ ] Add a citation section to the README.
- [ ] Create a stable tagged release before public visibility.

### Acceptance Criteria

- GitHub displays a valid citation entry.
- Installed package metadata identifies the creator and canonical repository.
- The license preserves permissive reuse while maintaining clear provenance.

## P0.4 Add Open-Source Project Infrastructure

- [ ] Add `SECURITY.md` with supported versions and private reporting instructions.
- [ ] Add `CODE_OF_CONDUCT.md`.
- [ ] Add `CHANGELOG.md` beginning with `[Unreleased]`.
- [ ] Add `GOVERNANCE.md` describing maintainer authority and decision rules.
- [ ] Add `SUPPORT.md` explaining support boundaries.
- [ ] Add a pull-request template.
- [ ] Add bug, documentation, integration, and example issue templates.
- [ ] Add labels for `good first issue`, `help wanted`, `schema`, `docs`, `integration`, and `example`.
- [ ] Document release and deprecation policy.

## P0.5 Tighten Package and Release Metadata

- [ ] Confirm the distribution name and import package are intentional.
- [ ] Add package classifiers appropriate to release maturity.
- [ ] Add project URLs.
- [ ] Pin minimum supported Python versions in documentation and CI.
- [ ] Add a package-data strategy if schemas or templates are included at runtime.
- [ ] Verify source distribution and wheel contain the intended files.
- [ ] Add release notes for every user-visible schema or behavior change.
- [ ] Add a release checklist.

### Acceptance Criteria

- `pip install` from the built wheel is sufficient for documented CLI workflows.
- Release artifacts do not depend on an editable repository checkout.
- Version output matches package and release tags.

## P1.1 Simplify the README

Recommended top-level order:

1. One-sentence definition.
2. Production problem.
3. Concrete output example.
4. Relationship to eval and observability tools.
5. Core primitives.
6. Five-minute quickstart.
7. Passing and blocked examples.
8. Integrations.
9. Limitations and non-goals.
10. Contribution and citation.

- [ ] Lead with `release assurance`, not a broad governance claim.
- [ ] Put a blocked-launch result in the first screenful.
- [ ] Move the 23-gate list to detailed documentation.
- [ ] Move scoring weights to methodology documentation.
- [ ] Remove duplicated definitions and FAQs.
- [ ] Add a comparison diagram or concise architecture block.
- [ ] Add explicit non-claims.

### Required Non-Claims

OpenEvalGate does not:

- Certify NIST, ISO, OWASP, EU AI Act, or other regulatory compliance.
- Execute candidate LLM systems.
- Replace runtime guardrails.
- Guarantee safe deployment.
- Establish a universal industry standard.

## P1.2 Add a Versioned Specification

Create `SPECIFICATION.md` or a dedicated specification directory.

Define:

- [ ] Behavioral contract
- [ ] Golden eval case
- [ ] Contrast family
- [ ] Admission route
- [ ] Workflow route
- [ ] Safe stopping boundary
- [ ] Escalation contract
- [ ] Handoff payload
- [ ] Durable resume
- [ ] Capability allocation policy
- [ ] Evidence provenance
- [ ] Hard blocker
- [ ] Release decision

For every primitive, document:

- Required fields.
- Semantics.
- Validation rules.
- Failure behavior.
- Versioning.
- Relationship to other artifacts.

## P1.3 Add Minimal Onboarding

Add:

```bash
openevalgate init my-agent --profile minimal
```

Profiles:

- `minimal`
- `standard`
- `high-risk`
- `multi-agent`

- [ ] Minimal profile produces the smallest valid documentation-review project.
- [ ] Standard profile adds action controls, observability, rollback, and eval results.
- [ ] High-risk profile adds tail-risk and structured escalation requirements.
- [ ] Multi-agent profile adds routing and capability allocation.
- [ ] Add Windows PowerShell instructions.
- [ ] Add a five-minute quickstart.

### Acceptance Criteria

A new user can:

1. Install the package.
2. Initialize a project.
3. Edit one or two sample cases.
4. Run `check`.
5. Generate a useful report.

without copying the full customer-support example.

## P1.4 Improve CLI Ergonomics

- [ ] Add `openevalgate --version`.
- [ ] Add `--format markdown|json` to `report`.
- [ ] Add `--format text|json` to `check` and `validate`.
- [ ] Add stable exit codes for validation, blocker, and internal-error states.
- [ ] Add `--strict` for warnings that should fail CI.
- [ ] Add actionable error messages with paths and suggested fixes.
- [ ] Document machine-consumable outputs.

## P1.5 Improve Examples

Maintain two flagship narratives:

### Passing example

- [ ] Complete empirical result coverage.
- [ ] Passing critical controls.
- [ ] No prohibited actions.
- [ ] Valid rollback and owner signoff.
- [ ] Controlled-launch recommendation.

### Blocked example

- [ ] High evidence completeness.
- [ ] Failed observed behavioral metrics.
- [ ] At least one critical-control blocker.
- [ ] Clear mitigation and rerun path.

- [ ] Label all data and model outputs as illustrative unless produced by a reproducible public harness.
- [ ] Avoid presenting fabricated example metrics as real-world adoption evidence.

## P1.6 Review Standards and Competitive Claims

- [ ] Record the exact version and review date for every external framework.
- [ ] Replace `aligned with` language when the mapping is only conceptual.
- [ ] Avoid compliance or certification implications.
- [ ] Cite primary standards and official documentation.
- [ ] Add a limitations section to the competitive-landscape document.
- [ ] Review links before every tagged release.

## Exit Criteria

Iteration 2 is complete when:

- [ ] Required CI is green.
- [ ] Branch protection is configured.
- [ ] Package build and clean installation succeed.
- [ ] Authorship and citation are explicit.
- [ ] Security, governance, support, and changelog files exist.
- [ ] The README communicates the category and value in under one minute.
- [ ] A minimal new-user flow works without copying a large example.
- [ ] Passing and blocked examples are reproducible.
- [ ] Public claims are bounded and supportable.
