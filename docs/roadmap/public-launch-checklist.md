# OpenEvalGate Public Launch Checklist

Use this checklist for the final decision to change repository visibility from private to public.

This checklist distinguishes implemented repository capabilities from checks that must run on the exact public-release commit. Release-artifact inspection, clean-wheel installation, installed CLI execution, and installed-wheel report reproduction are implemented.

## 1. Release Semantics

- [x] The report labels document coverage as evidence completeness rather than launch readiness.
- [x] Evidence completeness, behavioral evidence, and critical-control status are separate.
- [ ] The final launch recommendation is derived from review mode, empirical evidence, thresholds, and blockers.
- [x] A project without eval results cannot receive a controlled-launch recommendation.
- [ ] Critical metrics display thresholds and denominators.
- [ ] Insufficient evidence is reported explicitly for behavioral thresholds and denominators.
- [x] `partial` critical gates block advancement.
- [x] `not_applicable` is permitted only by documented hard-gate policy.
- [x] Hard-blocker messages match implementation behavior.
- [x] Unknown conditional applicability is fail-closed.
- [x] Invalid action-risk evidence remains diagnostic-only and cannot satisfy policy.

## 2. Evidence Integrity

- [ ] Mandatory result fields cannot be blank.
- [ ] Derived match fields are recomputed or consistency-checked.
- [ ] Duplicate result records are rejected.
- [ ] Run timestamps and artifact versions are recorded.
- [ ] Output references are validated.
- [ ] Evaluator type and reviewer identity are recorded.
- [x] Blank or placeholder hard-gate evidence cannot satisfy an applicable centralized hard gate.
- [ ] Broader artifact-depth validation is implemented.
- [ ] Evidence provenance is visible in reports.
- [ ] Evidence freshness requirements are defined.

## 3. Tests and CI

- [x] The consolidated `CI` job passes on Python 3.10.
- [x] The consolidated `CI` job passes on Python 3.11.
- [x] The consolidated `CI` job passes on Python 3.12.
- [x] The consolidated `CI` job passes on Python 3.13.
- [x] Full `pytest` runs on Python 3.10 and Python 3.13; Python 3.11 and Python 3.12 run lightweight install, compile, import, and CLI checks.
- [x] Node 24-compatible GitHub Actions are used.
- [ ] Linting passes.
- [ ] Formatting checks pass.
- [ ] Type checks pass.
- [x] Source and wheel package builds pass.
- [x] Wheel installation passes in a clean environment.
- [x] CLI smoke tests pass for all canonical examples.
- [x] All canonical examples pass structural validation.
- [x] Generated reports match committed examples byte-for-byte through the installed wheel.
- [x] Dependabot configuration is present.
- [ ] Dependency review and security scanning pass or have documented accepted findings.
- [ ] Branch protection requires the consolidated `CI` check.

## 4. Package and Release

- [x] Package version remains intentionally `0.1.1` until a release bump is approved.
- [x] `openevalgate --version` matches installed package metadata.
- [x] Source distribution contents are inspected and correct.
- [x] Wheel contents are inspected and correct.
- [x] Installation does not require an editable checkout.
- [x] `CHANGELOG.md` contains an `[Unreleased]` section.
- [ ] Stable release notes describe all user-visible changes.
- [ ] A release tag is prepared from the verified release commit.
- [ ] Rollback instructions exist for a broken package release.
- [ ] Release and deprecation policy is documented.

## 5. Authorship and Provenance

- [x] Package author and maintainer identify Chenye Zhu.
- [x] Copyright reads `Chenye Zhu and OpenEvalGate contributors`.
- [x] `CITATION.cff` is present and syntactically valid.
- [ ] `AUTHORS.md` exists.
- [x] Contribution-credit expectations are documented.
- [x] Canonical repository, documentation, issues, homepage, and changelog URLs are present.
- [x] The README contains maintainer and citation instructions.

## 6. Open-Source Infrastructure

- [x] `LICENSE` is present and intentionally MIT.
- [x] `CONTRIBUTING.md` is expanded and current.
- [x] `SECURITY.md` is present.
- [x] `CODE_OF_CONDUCT.md` is present.
- [ ] `GOVERNANCE.md` is present.
- [ ] `SUPPORT.md` is present.
- [x] Structured bug and feature issue forms are present.
- [x] A pull-request template is present.
- [x] Dependabot configuration is present.
- [ ] Release, deprecation, and schema-change policies are documented.
- [x] Maintainer contact and private security-reporting instructions are documented.
- [ ] GitHub private vulnerability reporting is enabled.
- [ ] Repository labels and support boundaries are configured.

## 7. README and Documentation

- [ ] The first paragraph defines OpenEvalGate primarily as release assurance.
- [x] A concrete blocked-launch example appears near the top.
- [x] The relationship to eval runners, observability tools, and runtime guardrails is clear.
- [ ] Core primitives are concise and linked to a versioned specification.
- [ ] The five-minute quickstart works from a clean wheel installation.
- [ ] The README does not repeat the full documentation set.
- [~] Limitations and non-goals are present, but a dedicated limitations section remains open.
- [ ] Explicit non-claims cover compliance certification, safe-deployment guarantees, and universal readiness.
- [ ] No unsupported `first`, `standard`, `industry-leading`, or universal claim appears.
- [ ] External standards references include exact versions or review dates where necessary.
- [ ] All documentation links resolve on the release commit.
- [x] CI, license, Python, maintainer, citation, changelog, contribution, and security links are present.

## 8. Examples

### Controlled-launch passing example

- [ ] Behavioral evidence sufficiency is implemented.
- [ ] Empirical result coverage meets configured requirements.
- [ ] Critical thresholds and denominators pass.
- [ ] No unresolved hard blocker exists.
- [ ] Observability, rollback, and owner signoff pass.
- [ ] The report produces a controlled-launch recommendation.

A controlled-launch passing example is intentionally blocked on unfinished review-mode and behavioral-sufficiency policy. It must not be manufactured before those semantics exist.

### Blocked example

- [x] Has high evidence completeness.
- [x] Fails observed behavioral controls.
- [x] Shows named hard blockers.
- [x] Produces a `Not ready` recommendation.
- [x] Includes clear mitigation and rerun guidance.

### Example integrity

- [ ] Illustrative data and outputs are labeled as illustrative.
- [x] No example metric is presented as external adoption evidence.
- [x] Generated outputs reproduce from committed inputs.

## 9. Onboarding

- [ ] A minimal project can be initialized without copying the full flagship example.
- [ ] Standard, high-risk, and multi-agent paths are documented or explicitly deferred.
- [ ] Linux/macOS clean-install commands work.
- [ ] Windows PowerShell clean-install commands work.
- [x] Error messages identify failing artifact paths.
- [ ] JSON output is available and documented.
- [x] `openevalgate --version` is available.

## 10. External Validation

- [ ] Three to five private-beta design partners have been contacted.
- [ ] At least one independent practitioner has completed an end-to-end review or pilot.
- [ ] Substantive feedback has been recorded with permission settings.
- [ ] At least one external issue, review, or contribution exists, or the absence is explicitly accepted as a launch risk.
- [ ] No private participant information is committed without permission.
- [ ] Public adoption claims are source-backed.

## 11. Repository Settings

- [ ] Repository description is concise and accurate.
- [ ] Repository topics are relevant and not keyword spam.
- [ ] Social preview image is correct.
- [x] Default branch is `main`.
- [ ] Pull requests are required for `main`.
- [ ] The consolidated `CI` check is required.
- [ ] Branches must be up to date before merge.
- [ ] Force pushes to `main` are disabled.
- [x] Squash merging is supported and used for major changes.
- [ ] Dependency alerts and security updates are enabled.
- [ ] Secret scanning and private vulnerability reporting are enabled where available.
- [ ] Discussions are enabled only if there is a moderation plan.
- [ ] Issue labels are configured.
- [ ] Repository visibility change has been reviewed by the maintainer.

## 12. Final Release Review

- [x] PR #5 public-readiness infrastructure is merged.
- [ ] The exact public-release commit hash is recorded.
- [ ] All required CI checks are green on that exact commit.
- [ ] The public package and repository versions agree.
- [ ] The built wheel installs and the installed CLI run from scratch on the exact public-release commit.
- [ ] No secrets, confidential examples, internal employer material, or private pilot data are present.
- [ ] No unresolved required P0 item remains in [TODO.md](../../TODO.md), or each exception is explicitly accepted and documented.
- [ ] Release notes identify known limitations.
- [ ] The repository can be made public without relying on claims that are not yet evidenced.

## Launch Decision

- [ ] **Approved for public release**

Approved by:

- Maintainer: ____________________
- Release commit: ____________________
- Release version: ____________________
- Review date: ____________________
