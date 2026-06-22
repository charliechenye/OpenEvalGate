# OpenEvalGate Public Repository Checklist

Use this checklist for the final decision to change repository visibility from private to public.

Public visibility is not the same as publishing OpenEvalGate `0.2.0`, releasing to PyPI, or declaring stable `1.0.0` compatibility. This checklist covers safe disclosure, bounded claims, reproducibility, governance, repository protection, and exact-commit verification.

## 1. Release Semantics

- [x] Evidence completeness, behavioral evidence, and critical-control status are separate.
- [x] The final recommendation is derived from review mode, empirical evidence, thresholds, and blockers.
- [x] Missing or invalid eval results cannot authorize controlled launch.
- [x] Initial controlled-launch thresholds and denominators are explicit.
- [x] Critical failures override aggregate scores.
- [x] `partial` critical gates block advancement.
- [x] `not_applicable` is governed by documented policy.
- [x] Unknown conditional applicability is fail-closed.
- [x] Invalid action-risk evidence cannot satisfy policy.
- [x] Core eval-result identity, expected-route, duplicate, timestamp, and supplied-output-reference errors cannot silently influence a controlled-launch decision.
- [ ] Enriched workflow, handoff, provenance, freshness, and artifact-version claims are validated for controlled launch.

## 2. Public Positioning and Non-Claims

- [x] The first paragraph defines OpenEvalGate primarily as release assurance.
- [x] Repository-authored scenarios are described as examples or reference scenarios, not external proof.
- [x] Synthetic and illustrative examples are labeled clearly.
- [x] A dedicated limitations and non-claims section exists.
- [x] The README states that OpenEvalGate does not certify compliance.
- [x] The README states that OpenEvalGate does not guarantee safe deployment.
- [x] The README states that OpenEvalGate does not execute candidate systems or replace runtime guardrails.
- [x] The README states that OpenEvalGate does not establish a universal industry standard.
- [x] The README avoids unsupported `first`, `standard`, `industry-leading`, or universal claims.
- [x] The README explains the category and value in under one minute.
- [x] The full gate list, scoring weights, and extended methodology are moved out of the main README where appropriate.
- [ ] Standards and competitive references use precise wording and primary sources.

## 3. Reference Examples

### Passing controlled-launch example

- [ ] Selected-run and critical-case coverage meet configured requirements.
- [ ] Behavioral thresholds and invariants pass.
- [ ] No unresolved hard blocker or prohibited action exists.
- [ ] Observability, rollback, and owner signoff pass.
- [ ] The report produces a deterministic controlled-launch recommendation.

### Blocked controlled-launch example

- [x] Has high evidence completeness.
- [x] Fails observed behavioral or critical-control evidence.
- [x] Shows named hard blockers.
- [x] Produces a deterministic `Not ready` recommendation.
- [x] Includes mitigation and rerun guidance.

### Example integrity

- [x] All repository-authored data, model outputs, and metrics are labeled synthetic or illustrative.
- [x] No example metric is presented as external adoption evidence.
- [x] Generated outputs reproduce from committed inputs.
- [x] Canonical reports reproduce byte-for-byte through the installed wheel.
- [ ] The README links directly to passing and blocked reports.

## 4. Tests, Packaging, and Security Checks

- [x] Consolidated CI covers Python 3.10 through 3.13.
- [x] Full tests run on Python 3.10 and Python 3.13.
- [x] Lightweight install, compile, import, and CLI checks run on Python 3.11 and Python 3.12.
- [x] Source and wheel builds pass.
- [x] Distribution contents and metadata are inspected.
- [x] The wheel installs in a clean environment.
- [x] The installed CLI reports the package version.
- [x] Canonical CLI smoke tests pass through the installed wheel.
- [x] Dependabot configuration is present.
- [ ] Linting passes.
- [ ] Formatting checks pass.
- [ ] An enforceable type-checking baseline passes.
- [ ] Dependency review passes or accepted findings are documented.
- [ ] Lightweight static-security scanning passes or accepted findings are documented.
- [ ] Documentation links resolve on the public-visibility commit.

## 5. Governance, Support, and Attribution

- [x] `LICENSE` is present and intentionally MIT.
- [x] `CONTRIBUTING.md` is current.
- [x] `SECURITY.md` is present.
- [x] `CODE_OF_CONDUCT.md` is present.
- [x] `CHANGELOG.md` is present.
- [x] Structured issue forms and a pull-request template are present.
- [x] Package author and maintainer identify Chenye Zhu.
- [x] Copyright identifies Chenye Zhu and OpenEvalGate contributors.
- [x] `CITATION.cff` is present.
- [ ] `GOVERNANCE.md` defines maintainer authority and decision rules.
- [ ] `SUPPORT.md` defines support boundaries and absence of an SLA.
- [ ] `AUTHORS.md` defines contribution-credit rules.
- [ ] Release, deprecation, schema-change, and broken-release rollback policies are documented.
- [ ] Pre-1.0 compatibility expectations are explicit.
- [x] Setuptools license metadata is modernized.

## 6. Repository Settings

- [x] Default branch is `main`.
- [x] Squash merging is supported and used for major changes.
- [ ] Pull requests are required for `main`.
- [ ] The consolidated `CI` check is required.
- [ ] Branches must be current before merge.
- [ ] Force pushes and branch deletion on `main` are disabled.
- [ ] Bypass of required checks is restricted.
- [ ] Dependency alerts and security updates are enabled.
- [ ] Secret scanning and push protection are enabled where available.
- [ ] Private vulnerability reporting is enabled.
- [ ] Repository description is concise and accurate.
- [ ] Repository topics are relevant and restrained.
- [ ] Issue labels and support boundaries are configured.
- [ ] Social preview image is correct.
- [ ] Discussions are enabled only if a moderation plan exists.

## 7. Disclosure and History Audit

- [ ] The current tree has been reviewed for credentials and secrets.
- [ ] The current tree has been reviewed for confidential employer, customer, or pilot material.
- [ ] The current tree has been reviewed for proprietary prompts, policies, and private contact information.
- [ ] Repository assets have appropriate ownership, licensing, or attribution.
- [ ] Generated files contain no unsafe local paths or unexpected private metadata.
- [ ] Git history has been reviewed for deleted secrets, confidential files, private images, and large unexpected blobs.
- [ ] Retained branches and tags have been reviewed.
- [ ] Any required history rewrite is complete before visibility changes.
- [ ] Audit scope, findings, remediation, and residual risks are recorded privately.
- [ ] No sensitive audit detail is placed in a public PR description.

## 8. Exact-Commit Verification

- [ ] The exact public-visibility commit SHA is recorded.
- [ ] All required checks are green on that exact commit.
- [ ] The built wheel installs from scratch on that exact commit.
- [ ] Installed CLI smoke tests pass on that exact commit.
- [ ] Canonical reports reproduce on that exact commit.
- [ ] Package and repository versions are internally consistent.
- [ ] Documentation links and public metadata are verified.
- [ ] No unresolved required public-visibility item remains, or each exception is explicitly accepted and documented.
- [ ] Known limitations and accepted public-alpha risks are recorded.
- [ ] The repository can become public without relying on claims that are not evidenced.

## 9. Explicitly Deferred Until OpenEvalGate 0.2.0

These items do not block public repository visibility:

- [ ] `openevalgate init` or packaged project scaffolding.
- [ ] Minimal, standard, high-risk, or multi-agent profile breadth.
- [ ] Versioned JSON output.
- [ ] SARIF output.
- [ ] Vendor-specific integration adapters.
- [ ] PyPI publication.
- [ ] A tagged `0.2.0` release.
- [ ] Published external case studies.

They remain tracked in [TODO.md](../../TODO.md), [Release Milestones](release-milestones.md), and [Iteration 3](iteration-03-adoption-and-external-validation.md).

## 10. Public Visibility Decision

- [ ] **Approved to change repository visibility to public**

Approved by:

- Maintainer: ____________________
- Public-visibility commit: ____________________
- Package version: ____________________
- Review date: ____________________

## 11. Post-Visibility Actions

- [ ] Confirm public README, citation, issue, security, and contribution links render correctly.
- [ ] Confirm private vulnerability reporting remains available.
- [ ] Confirm repository topics, social preview, and package metadata appear correctly.
- [ ] Begin the OpenEvalGate `0.2.0` evidence-integrity and onboarding milestone.
