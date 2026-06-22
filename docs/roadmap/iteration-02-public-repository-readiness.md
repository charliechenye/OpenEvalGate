# Iteration 2: Public Repository Readiness

## Status

**Core infrastructure and public positioning complete; public-visibility review remains open.** Bounded release-assurance claims, explicit non-claims, illustrative scenario labeling, continuous integration, Python 3.10–3.13 compatibility coverage, package builds, artifact inspection, clean-wheel installation, installed CLI execution, canonical-report reproduction, security and conduct policies, contribution templates, citation metadata, changelog, maintainer attribution, issue forms, pull-request guidance, and dependency automation are implemented.

This iteration now ends when the repository can safely change from private to public. It does not require the full `0.2.0` product release or stable `1.0.0` compatibility guarantees.

## Objective

Make OpenEvalGate safe, bounded, reproducible, attributable, and understandable for public inspection while preserving its explicit pre-1.0 status.

This iteration should not expand product scope. It should harden the public surface, claims, examples, governance, CI, repository settings, and disclosure posture.

## Planned PR Sequence

1. Public positioning and limitations.
2. Eval-result integrity.
3. Run provenance and version pinning.
4. Passing and blocked reference examples.
5. Governance, support, attribution, and compatibility policies.
6. CI quality and security hardening.
7. Disclosure and Git-history audit.
8. Public-launch freeze.

See [Release Milestones](release-milestones.md) for the dependency map.

## P0.1 Public Positioning and Claim Safety

Recommended README order:

1. One-sentence release-assurance definition.
2. Production problem.
3. Concrete blocked-launch output.
4. Relationship to eval, observability, and runtime-control tools.
5. Core primitives.
6. Quickstart.
7. Passing and blocked examples.
8. Limitations and non-goals.
9. Contribution and citation.

- [x] Lead with `release assurance`, not a broad governance claim.
- [x] Replace `proof` wording for maintainer-authored examples with `examples` or `reference scenarios`.
- [x] Put a blocked-launch result in the first screenful.
- [x] Add a dedicated limitations and non-claims section.
- [x] State that OpenEvalGate does not certify compliance, guarantee safe deployment, execute candidate systems, or establish a universal standard.
- [x] Move the full 23-gate list and score weights to methodology documentation.
- [x] Remove duplicated definitions and repetitive FAQ content.
- [ ] Review every standards and competitive reference for exact wording, version, review date, and primary source.
- [x] Ensure the repository can explain its category and value in under one minute.

## P0.2 Reference Example Integrity

Maintain two flagship narratives.

### Passing controlled-launch example

- [ ] Complete selected-run and critical-case coverage.
- [ ] Passing configured thresholds and behavioral invariants.
- [ ] No unresolved hard blocker or prohibited action.
- [ ] Passing observability, rollback, and owner signoff.
- [ ] Valid selected-run provenance.
- [ ] Deterministic controlled-launch recommendation.

### Blocked controlled-launch example

- [x] High evidence completeness.
- [x] Failed observed behavioral metrics.
- [x] At least one critical-control blocker.
- [x] Clear mitigation and rerun path.
- [x] Deterministic `Not ready` recommendation.

### Example integrity

- [x] Label all repository-authored data, metrics, and outputs as synthetic or illustrative.
- [x] Avoid presenting illustrative metrics as external adoption evidence.
- [ ] Add a concise passing-versus-blocked comparison.
- [x] Generate canonical reports from committed inputs without undocumented manual edits.
- [x] Reproduce canonical reports byte-for-byte through the installed wheel.

## P0.3 Continuous Integration and Security Gates

Implemented foundation:

- [x] Python 3.10 through 3.13 compatibility coverage.
- [x] Full tests on Python 3.10 and 3.13.
- [x] Lightweight install, compile, import, and CLI checks on Python 3.11 and 3.12.
- [x] Source and wheel builds.
- [x] Distribution-content inspection.
- [x] Clean-wheel installation.
- [x] Installed CLI smoke tests.
- [x] Canonical-report reproduction.
- [x] Node 24-compatible GitHub Actions.
- [x] Dependency update automation.

Remaining public-repository gates:

- [ ] Add linting and formatting checks.
- [ ] Add an enforceable type-checking baseline.
- [ ] Add dependency review.
- [ ] Add a lightweight static-security scan.
- [ ] Add documentation-link validation.
- [ ] Document and accept any unresolved security-tool finding before visibility.

### Acceptance criteria

- [x] Every pull request runs the consolidated `CI` workflow.
- [ ] The default branch cannot merge with failed required checks.
- [x] A wheel installed in a clean environment exposes a working CLI.
- [x] Committed generated reports match installed CLI output.
- [ ] No unresolved high-severity dependency or static-analysis finding remains.

## P0.4 Repository Protection and Public Settings

- [ ] Require pull requests for `main`.
- [ ] Require the consolidated `CI` status check.
- [ ] Require branches to be current before merge.
- [ ] Disable force pushes and branch deletion on `main`.
- [ ] Restrict bypass of required checks.
- [ ] Enable dependency alerts and security updates.
- [ ] Enable secret scanning and push protection where available.
- [ ] Enable private vulnerability reporting.
- [x] Prefer squash merging for readable public history.
- [x] Use `main` as the default branch.
- [ ] Configure a concise repository description.
- [ ] Configure restrained repository topics.
- [ ] Configure issue labels and public support boundaries.
- [ ] Verify the social preview image.
- [ ] Enable Discussions only if a moderation plan exists.

These settings are applied manually after the final CI check names are stable and before the public-launch freeze PR merges.

## P0.5 Governance, Support, and Attribution

Implemented foundation:

- [x] `SECURITY.md`.
- [x] `CODE_OF_CONDUCT.md`.
- [x] `CHANGELOG.md`.
- [x] Expanded `CONTRIBUTING.md`.
- [x] Structured issue forms and pull-request template.
- [x] Maintainer and package attribution.
- [x] `CITATION.cff`.

Remaining work:

- [ ] Add `GOVERNANCE.md` describing maintainer authority and decision rules.
- [ ] Add `SUPPORT.md` explaining support boundaries and absence of an SLA.
- [ ] Add `AUTHORS.md` and contribution-credit rules.
- [ ] Document release, deprecation, and schema-change policy.
- [ ] Add a broken-release rollback procedure.
- [ ] Modernize setuptools license metadata.
- [ ] Link contribution guidance to governance and compatibility rules.

### Acceptance criteria

- [ ] Users know what support is available and what is out of scope.
- [ ] Contributors know who decides scope and compatibility policy.
- [ ] Attribution remains clear under the MIT license.
- [ ] Pre-1.0 breaking-change expectations are explicit.

## P0.6 Disclosure and History Audit

Review the current tree and all retained Git history for:

- secrets and credentials;
- confidential employer, customer, or pilot material;
- proprietary prompts or policies;
- private email or contact information that should not be public;
- absolute local paths and unsafe generated metadata;
- unlicensed images, icons, text, or copied assets;
- deleted sensitive files that remain in history;
- stale private branches or tags.

- [ ] Record the audit scope, tools, findings, remediation, and residual risks privately.
- [ ] Rewrite history before visibility if sensitive material is found.
- [ ] Remove or explicitly review retained branches and tags.
- [ ] Confirm all public assets are owned, generated, or appropriately licensed.
- [ ] Confirm no private audit details are placed in public PR descriptions.

## P0.7 Exact-Commit Public-Launch Freeze

- [ ] Update roadmap and checklist statuses without overstating completion.
- [ ] Record intentionally deferred work and accepted public-alpha risks.
- [ ] Record the exact public-visibility commit.
- [ ] Confirm required checks are green on that commit.
- [ ] Re-run clean-wheel installation and canonical-report reproduction on that commit.
- [ ] Verify documentation links and public metadata.
- [ ] Confirm no claim depends on unpublished external validation.
- [ ] Complete the [Public Launch Checklist](public-launch-checklist.md).
- [ ] Change repository visibility to public.

## Explicit Deferrals Until OpenEvalGate 0.2.0

The following are valuable but do not block public visibility:

- `openevalgate init` and profile scaffolding;
- versioned JSON output;
- SARIF output;
- stable automation exit codes beyond current behavior;
- vendor-specific adapters;
- a PyPI release;
- published external case studies.

## Exit Criteria

Iteration 2 is complete when:

- [x] Public claims are bounded and limitations are explicit.
- [ ] Passing and blocked examples are reproducible and labeled illustrative.
- [ ] Required CI quality and security checks pass.
- [ ] Branch protection and repository security settings are enabled.
- [ ] Governance, support, attribution, and compatibility policies are present.
- [ ] Tree and history disclosure review is complete.
- [ ] The exact public-visibility commit passes required verification.
- [ ] The maintainer approves the visibility change.
- [ ] The repository is public and still explicitly pre-1.0.
