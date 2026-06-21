# OpenEvalGate Public Launch Checklist

Use this checklist for the final decision to change repository visibility from private to public.

A checked box means the condition has been verified on the exact release commit. `[~]` means the work is implemented or validated on draft PR #5 but must be reverified after merge. It does not count as final public-release approval.

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
- [~] Blank or placeholder hard-gate evidence cannot satisfy an applicable centralized hard gate; broader artifact-depth validation remains open.
- [ ] Evidence provenance is visible in reports.
- [ ] Evidence freshness requirements are defined.

## 3. Tests and CI

- [~] CI passes on Python 3.10 in PR #5.
- [~] CI passes on Python 3.11 in PR #5.
- [~] CI passes on Python 3.12 in PR #5.
- [~] CI passes on Python 3.13 in PR #5.
- [ ] Linting passes.
- [ ] Formatting checks pass.
- [ ] Type checks pass.
- [~] Source and wheel package builds pass in PR #5.
- [ ] Wheel installation passes in a clean environment.
- [~] CLI smoke tests pass for all canonical examples in PR #5.
- [~] All canonical examples pass structural validation in PR #5.
- [~] Generated reports match committed examples byte-for-byte in PR #5.
- [~] Dependabot configuration is present in PR #5.
- [ ] Dependency review and security scanning pass or have documented accepted findings.
- [ ] Branch protection requires the release checks.

## 4. Package and Release

- [x] Package version remains intentionally `0.1.1` until a release bump is approved.
- [ ] `openevalgate --version` matches the package version.
- [ ] Source distribution contents are inspected and correct.
- [ ] Wheel contents are inspected and correct.
- [ ] Installation does not require an editable checkout.
- [~] `CHANGELOG.md` contains an `[Unreleased]` section in PR #5.
- [ ] Stable release notes describe all user-visible changes.
- [ ] A release tag is prepared from the verified release commit.
- [ ] Rollback instructions exist for a broken package release.
- [ ] Release and deprecation policy is documented.

## 5. Authorship and Provenance

- [~] Package author and maintainer identify Chenye Zhu in PR #5.
- [~] Copyright reads `Chenye Zhu and OpenEvalGate contributors` in PR #5.
- [~] `CITATION.cff` is present and syntactically valid in PR #5.
- [ ] `AUTHORS.md` exists.
- [~] Contribution-credit expectations are documented in PR #5; formal authorship rules remain open.
- [~] Canonical repository, documentation, issues, homepage, and changelog URLs are present in PR #5.
- [~] The README contains maintainer and citation instructions in PR #5.

## 6. Open-Source Infrastructure

- [x] `LICENSE` is present and intentionally MIT.
- [~] `CONTRIBUTING.md` is expanded and current in PR #5.
- [~] `SECURITY.md` is present in PR #5.
- [~] `CODE_OF_CONDUCT.md` is present in PR #5.
- [ ] `GOVERNANCE.md` is present.
- [ ] `SUPPORT.md` is present.
- [~] Structured bug and feature issue forms are present in PR #5.
- [~] A pull-request template is present in PR #5.
- [~] Dependabot configuration is present in PR #5.
- [ ] Release, deprecation, and schema-change policies are documented.
- [~] Maintainer contact and private security-reporting instructions are documented in PR #5.
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
- [~] CI, license, Python, maintainer, citation, changelog, contribution, and security links are present in PR #5.

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
- [~] Generated outputs reproduce from committed inputs in PR #5.

## 9. Onboarding

- [ ] A minimal project can be initialized without copying the full flagship example.
- [ ] Standard, high-risk, and multi-agent paths are documented or explicitly deferred.
- [ ] Linux/macOS clean-install commands work.
- [ ] Windows PowerShell clean-install commands work.
- [x] Error messages identify failing artifact paths.
- [ ] JSON output is available and documented.
- [ ] `openevalgate --version` is available.

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
- [ ] Required CI checks are configured.
- [ ] Branches must be up to date before merge.
- [ ] Force pushes to `main` are disabled.
- [x] Squash merging is supported and used for major changes.
- [ ] Dependency alerts and security updates are enabled.
- [ ] Secret scanning and private vulnerability reporting are enabled where available.
- [ ] Discussions are enabled only if there is a moderation plan.
- [ ] Issue labels are configured.
- [ ] Repository visibility change has been reviewed by the maintainer.

## 12. Final Release Review

- [ ] PR #5 is merged.
- [ ] The release commit hash is recorded.
- [ ] All required CI checks are green on that exact commit.
- [ ] The public package and repository versions agree.
- [ ] The built wheel installs and the installed CLI runs from scratch.
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
