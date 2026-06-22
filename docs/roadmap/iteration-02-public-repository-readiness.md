# Iteration 2: Public Repository and Release Readiness

## Status

**Release-artifact verification implemented.** Continuous integration, Python 3.10–3.13 compatibility coverage, package builds, artifact inspection, clean-wheel installation, installed CLI execution, canonical-report reproducibility, security and conduct policies, contribution templates, citation metadata, changelog, maintainer attribution, issue forms, pull-request guidance, and dependency automation are implemented. Verification on the exact public-release commit remains pending.

Iteration 2 remains open for branch protection, governance and support documents, release and deprecation policy, security scanning, and final public-release verification.

## Objective

Make OpenEvalGate reproducible, attributable, secure, understandable, and easy to adopt before the repository becomes public.

This iteration should not expand product scope. It should make the existing framework trustworthy to engineers, practitioners, contributors, and reviewers.

## P0.1 Add Continuous Integration

The required GitHub Actions workflow covers:

- [x] Python 3.10.
- [x] Python 3.11.
- [x] Python 3.12.
- [x] Python 3.13.
- [x] Full `pytest` suite on Python 3.10 and Python 3.13.
- [x] Lightweight install, compile, import, and CLI checks on Python 3.11 and Python 3.12.
- [x] One consolidated `CI` status check for branch protection.
- [x] Node 24-compatible GitHub Actions.
- [x] Source and wheel package builds.
- [x] Wheel installation in a clean environment.
- [x] CLI smoke tests for all canonical examples.
- [x] Canonical-example validation.
- [x] Generated-report byte-for-byte reproducibility.
- [x] Package compilation.
- [x] Whitespace validation.
- [ ] Linting and formatting.
- [ ] Type checking.
- [ ] Dependency review.
- [ ] CodeQL or an equivalent lightweight security scan.

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

The build, supported-version checks, artifact inspection, clean-wheel installation, installed CLI commands, canonical validation, and byte-for-byte report comparison are implemented. The report comparison is reproduced through the installed wheel. Verification on the exact public-release commit remains pending.

### Acceptance Criteria

- [x] Every pull request runs the consolidated `CI` workflow.
- [ ] The default branch cannot merge with a failed required check.
- [x] Committed generated reports match current CLI output.
- [x] A wheel installed in a clean environment exposes a working CLI.

## P0.2 Configure Repository Protection

- [ ] Require pull requests for changes to the default branch.
- [ ] Require the consolidated `CI` status check.
- [ ] Require branches to be up to date before merge.
- [ ] Disable force pushes to the default branch.
- [ ] Enable secret scanning and dependency alerts where available.
- [x] Prefer squash merging for a readable public history.
- [x] Use `main` as the default branch.
- [ ] Enable private vulnerability reporting before public visibility.

These settings require manual repository configuration after PR #5 is merged.

## P0.3 Establish Authorship and Citation

- [x] Set package authorship to Chenye Zhu.
- [x] Update copyright to `Chenye Zhu and OpenEvalGate contributors`.
- [x] Add maintainer and homepage metadata.
- [x] Add `CITATION.cff` with the Charlie Zhu alias.
- [ ] Add `AUTHORS.md`.
- [x] Define contribution-credit expectations in `CONTRIBUTING.md` and the Code of Conduct.
- [x] Add repository, documentation, issues, and changelog URLs to `pyproject.toml`.
- [x] Add a citation section to the README.
- [ ] Create a stable tagged release before public visibility.

### Acceptance Criteria

- [x] GitHub can display citation metadata.
- [x] Installed package metadata identifies the creator and canonical repository.
- [x] The license preserves permissive reuse while maintaining clear provenance.

## P0.4 Add Open-Source Project Infrastructure

- [x] Add `SECURITY.md` with supported versions and private reporting instructions.
- [x] Add `CODE_OF_CONDUCT.md`.
- [x] Add `CHANGELOG.md` beginning with `[Unreleased]`.
- [ ] Add `GOVERNANCE.md` describing maintainer authority and decision rules.
- [ ] Add `SUPPORT.md` explaining support boundaries.
- [x] Add a pull-request template.
- [x] Add structured bug and feature issue forms.
- [ ] Add dedicated documentation, integration, and example issue forms only when contribution volume justifies them.
- [ ] Add labels for `good first issue`, `help wanted`, `schema`, `docs`, `integration`, and `example`.
- [ ] Document release, deprecation, and schema-change policy.
- [x] Add automated dependency update configuration.

## P0.5 Tighten Package and Release Metadata

- [x] Confirm the distribution name `openevalgate` and import package are intentional.
- [x] Add package classifiers appropriate to alpha maturity and Python 3.10–3.13.
- [x] Add project URLs.
- [x] Pin minimum supported Python versions in documentation and CI.
- [ ] Add a package-data strategy if schemas or templates are included at runtime.
- [x] Inspect source distribution and wheel contents for intended files.
- [x] Build source and wheel distributions successfully.
- [x] Add an `[Unreleased]` changelog for user-visible changes.
- [ ] Add stable tagged release notes.
- [ ] Add a release checklist and rollback procedure for broken package releases.

### Acceptance Criteria

- [x] `pip install` from the built wheel is sufficient for documented CLI workflows.
- [x] Release artifacts do not depend on an editable repository checkout.
- [~] Version output matches installed package metadata; release-tag verification remains pending.

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
- [x] Put a blocked-launch result in the first screenful.
- [ ] Move the 23-gate list to detailed documentation.
- [ ] Move scoring weights to methodology documentation.
- [ ] Remove duplicated definitions and FAQs.
- [x] Retain a concise architecture block.
- [~] Add explicit non-claims. Several are present; compliance-certification and universal-readiness wording should be made more explicit.
- [x] Add CI, license, Python, maintainer, citation, security, contribution, and changelog links.

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

For every primitive, document required fields, semantics, validation rules, failure behavior, versioning, and relationships to other artifacts.

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
- [ ] Add a five-minute quickstart from an installed wheel.

### Acceptance Criteria

A new user can install the package, initialize a project, edit one or two sample cases, run `check`, and generate a useful report without copying the full customer-support example.

## P1.4 Improve CLI Ergonomics

- [x] Add `openevalgate --version`.
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
- [x] Deterministic controlled-launch recommendation semantics.

### Blocked example

- [x] High evidence completeness.
- [x] Failed observed behavioral metrics.
- [x] At least one critical-control blocker.
- [x] Clear mitigation and rerun path.

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

- [x] The consolidated CI workflow is present and green across Python 3.10–3.13.
- [ ] Branch protection is configured.
- [x] Source and wheel package builds succeed.
- [x] Clean-wheel installation succeeds.
- [x] Authorship and citation are explicit.
- [x] Security, conduct, contribution, changelog, issue-template, and dependency-maintenance infrastructure exist.
- [ ] Governance and support files exist.
- [ ] The README communicates the category and value in under one minute.
- [ ] A minimal new-user flow works without copying a large example.
- [x] A blocked example is reproducible.
- [ ] A controlled-launch passing example exists after behavioral-sufficiency semantics are implemented.
- [ ] Public claims are reviewed, bounded, and supportable on the exact release commit.
