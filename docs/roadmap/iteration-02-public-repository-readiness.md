# Iteration 2: Public Repository and Release Readiness

## Status

**In progress in draft PR #5.** Continuous integration, package builds, canonical-report reproducibility, security and conduct policies, contribution templates, citation metadata, changelog, maintainer attribution, and dependency automation are implemented and green on the PR branch. Clean-wheel installation, branch protection, governance/support documents, release policy, version output, and final public-release verification remain open.

## Objective

Make OpenEvalGate reproducible, attributable, secure, understandable, and easy to adopt before the repository becomes public.

This iteration should not expand product scope. It should make the existing framework trustworthy to engineers, practitioners, contributors, and reviewers.

## P0.1 Add Continuous Integration

Add a required GitHub Actions workflow covering:

- [~] Python 3.10 — implemented and green in PR #5.
- [~] Python 3.11 — implemented and green in PR #5.
- [~] Python 3.12 — implemented and green in PR #5.
- [~] Python 3.13 — implemented and green in PR #5.
- [~] Full `pytest` suite — implemented and green in PR #5.
- [~] Package build — source and wheel builds pass in PR #5.
- [ ] Wheel installation in a clean environment.
- [~] CLI smoke tests — implemented for all canonical examples in PR #5.
- [~] Canonical-example validation — implemented and green in PR #5.
- [~] Generated-report reproducibility — implemented and green in PR #5.
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

Current PR #5 coverage includes the build, canonical validation, checks, reports, and byte-for-byte report comparison. Clean-wheel installation and `--version` remain open.

### Acceptance Criteria

- [~] Every pull request runs required CI checks after PR #5 merges.
- [ ] The default branch cannot merge with failed required checks.
- [~] Committed generated reports match current CLI output in PR #5.
- [ ] A wheel installed in a clean environment exposes a working CLI.

## P0.2 Configure Repository Protection

- [ ] Require pull requests for changes to the default branch.
- [ ] Require CI status checks.
- [ ] Require branches to be up to date before merge.
- [ ] Disable force pushes to the default branch.
- [ ] Enable secret scanning and dependency alerts where available.
- [x] Prefer squash merging for a readable public history.
- [x] Use `main` as the default branch.
- [ ] Enable private vulnerability reporting before public visibility.

These settings require manual repository configuration after PR #5 merges.

## P0.3 Establish Authorship and Citation

- [~] Set package authorship to Chenye Zhu — implemented in PR #5.
- [~] Update copyright to `Chenye Zhu and OpenEvalGate contributors` — implemented in PR #5.
- [~] Add maintainer and homepage metadata — implemented in PR #5.
- [~] Add `CITATION.cff` with the Charlie Zhu alias — implemented in PR #5.
- [ ] Add `AUTHORS.md`.
- [~] Define contribution-credit expectations in `CONTRIBUTING.md` and the Code of Conduct — implemented in PR #5; a formal authors file remains open.
- [~] Add repository, documentation, issues, and changelog URLs to `pyproject.toml` — implemented in PR #5.
- [~] Add a citation section to the README — implemented in PR #5.
- [ ] Create a stable tagged release before public visibility.

### Acceptance Criteria

- [~] GitHub can display citation metadata after PR #5 merges.
- [~] Installed package metadata identifies the creator and canonical repository after PR #5 merges.
- [~] The license preserves permissive reuse while maintaining clear provenance after PR #5 merges.

## P0.4 Add Open-Source Project Infrastructure

- [~] Add `SECURITY.md` with supported versions and private reporting instructions — implemented in PR #5.
- [~] Add `CODE_OF_CONDUCT.md` — implemented in PR #5.
- [~] Add `CHANGELOG.md` beginning with `[Unreleased]` — implemented in PR #5.
- [ ] Add `GOVERNANCE.md` describing maintainer authority and decision rules.
- [ ] Add `SUPPORT.md` explaining support boundaries.
- [~] Add a pull-request template — implemented in PR #5.
- [~] Add structured bug and feature issue forms — implemented in PR #5.
- [ ] Add dedicated documentation, integration, and example issue forms only when contribution volume justifies them.
- [ ] Add labels for `good first issue`, `help wanted`, `schema`, `docs`, `integration`, and `example`.
- [ ] Document release, deprecation, and schema-change policy.
- [~] Add automated dependency update configuration — implemented in PR #5.

## P0.5 Tighten Package and Release Metadata

- [x] Confirm the distribution name `openevalgate` and import package are intentional.
- [~] Add package classifiers appropriate to alpha maturity and Python 3.10–3.13 — implemented in PR #5.
- [~] Add project URLs — implemented in PR #5.
- [~] Pin minimum supported Python versions in documentation and CI — implemented in PR #5.
- [ ] Add a package-data strategy if schemas or templates are included at runtime.
- [ ] Inspect source distribution and wheel contents for intended files.
- [~] Build source and wheel distributions successfully — implemented in PR #5.
- [~] Add release notes for user-visible changes through `CHANGELOG.md` — implemented in PR #5; tagged release notes remain open.
- [ ] Add a release checklist and rollback procedure for broken package releases.

### Acceptance Criteria

- [ ] `pip install` from the built wheel is sufficient for documented CLI workflows.
- [ ] Release artifacts do not depend on an editable repository checkout.
- [ ] Version output matches package and release tags.

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
- [~] Add explicit non-claims — several are present; compliance-certification and universal-readiness wording should be made more explicit.
- [~] Add CI, license, Python, maintainer, citation, security, contribution, and changelog links — implemented in PR #5.

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
- [ ] Controlled-launch recommendation after controlled-launch semantics exist.

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

- [~] Required CI is green on PR #5; it must be merged and required on the release commit.
- [ ] Branch protection is configured.
- [~] Package build succeeds; clean-wheel installation remains open.
- [~] Authorship and citation are explicit in PR #5.
- [~] Security, conduct, contribution, and changelog files exist in PR #5; governance and support files remain open.
- [ ] The README communicates the category and value in under one minute.
- [ ] A minimal new-user flow works without copying a large example.
- [~] A blocked example is reproducible; a controlled-launch passing example depends on unfinished behavioral-sufficiency semantics.
- [ ] Public claims are reviewed, bounded, and supportable on the exact release commit.
