# OpenEvalGate Public Launch Checklist

Use this checklist for the final decision to change repository visibility from private to public.

A checked box means the condition has been verified on the exact release commit. It does not mean the work merely exists on another branch.

## 1. Release Semantics

- [x] The report labels document coverage as evidence completeness rather than launch readiness.
- [x] Evidence completeness, behavioral evidence, and critical-control status are separate.
- [ ] The final launch recommendation is derived from review mode, empirical evidence, thresholds, and blockers.
- [x] A project without eval results cannot receive a controlled-launch recommendation.
- [ ] Critical metrics display thresholds and denominators.
- [ ] Insufficient evidence is reported explicitly.
- [ ] `partial` critical gates block launch.
- [ ] `not_applicable` is permitted only by documented policy.
- [ ] Hard-blocker messages match implementation behavior.

## 2. Evidence Integrity

- [ ] Mandatory result fields cannot be blank.
- [ ] Derived match fields are recomputed or consistency-checked.
- [ ] Duplicate result records are rejected.
- [ ] Run timestamps and artifact versions are recorded.
- [ ] Output references are validated.
- [ ] Evaluator type and reviewer identity are recorded.
- [ ] Blank or superficial artifacts cannot earn full evidence credit.
- [ ] Evidence provenance is visible in reports.

## 3. Tests and CI

- [ ] CI passes on Python 3.10.
- [ ] CI passes on Python 3.11.
- [ ] CI passes on Python 3.12.
- [ ] CI passes on Python 3.13.
- [ ] Linting passes.
- [ ] Formatting checks pass.
- [ ] Type checks pass.
- [ ] Package build passes.
- [ ] Wheel installation passes in a clean environment.
- [ ] CLI smoke tests pass.
- [ ] All canonical examples pass structural validation.
- [ ] Generated reports match committed examples.
- [ ] Dependency and security checks pass or have documented accepted findings.
- [ ] Branch protection requires the release checks.

## 4. Package and Release

- [ ] Package version is correct.
- [ ] `openevalgate --version` matches the package version.
- [ ] Source distribution contains the intended files.
- [ ] Wheel contains the intended files.
- [ ] Installation does not require an editable checkout.
- [ ] Release notes describe all user-visible changes.
- [ ] `CHANGELOG.md` has an `[Unreleased]` section and the release entry.
- [ ] A release tag is prepared from the verified commit.
- [ ] Rollback instructions exist for a broken package release.

## 5. Authorship and Provenance

- [ ] Package author is `Chenye (Charlie) Zhu`.
- [ ] Copyright reads `Chenye Zhu and OpenEvalGate contributors`.
- [ ] `CITATION.cff` is valid.
- [ ] `AUTHORS.md` exists.
- [ ] Contributor-credit rules are documented.
- [ ] Canonical repository and documentation URLs are present.
- [ ] The README contains citation instructions.

## 6. Open-Source Infrastructure

- [ ] `LICENSE` is present and intentional.
- [ ] `CONTRIBUTING.md` is current.
- [ ] `SECURITY.md` is present.
- [ ] `CODE_OF_CONDUCT.md` is present.
- [ ] `GOVERNANCE.md` is present.
- [ ] `SUPPORT.md` is present.
- [ ] Issue templates are present.
- [ ] Pull-request template is present.
- [ ] Release and deprecation policies are documented.
- [ ] Maintainer contact and private security-reporting paths are valid.

## 7. README and Documentation

- [ ] The first paragraph defines OpenEvalGate as release assurance.
- [ ] A concrete blocked-launch example appears near the top.
- [ ] The relationship to eval runners, observability tools, and runtime guardrails is clear.
- [ ] Core primitives are concise and linked to the specification.
- [ ] The five-minute quickstart works from a clean installation.
- [ ] The README does not repeat the full documentation set.
- [ ] Limitations and non-goals are explicit.
- [ ] No compliance-certification claim appears.
- [ ] No unsupported `first`, `standard`, `industry-leading`, or universal claim appears.
- [ ] External standards references include exact versions or review dates where necessary.
- [ ] All documentation links resolve.

## 8. Examples

### Passing example

- [ ] Includes empirical result coverage.
- [ ] Meets configured critical thresholds.
- [ ] Has no unresolved hard blocker.
- [ ] Includes observability, rollback, and owner signoff.
- [ ] Produces a controlled-launch recommendation.

### Blocked example

- [ ] Has high evidence completeness.
- [ ] Fails at least one critical behavioral threshold.
- [ ] Shows a named hard blocker.
- [ ] Produces a `Not ready` recommendation.
- [ ] Includes a clear mitigation and rerun path.

### Example integrity

- [ ] Illustrative data and outputs are labeled as illustrative.
- [ ] No example metric is presented as external adoption evidence.
- [ ] Generated outputs can be reproduced from committed inputs.

## 9. Onboarding

- [ ] A minimal project can be initialized without copying the full flagship example.
- [ ] Standard, high-risk, and multi-agent paths are documented or explicitly deferred.
- [ ] Linux/macOS commands work.
- [ ] Windows PowerShell commands work.
- [ ] Error messages identify the failing artifact and remediation.
- [ ] JSON output is documented if available.

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
- [ ] Default branch decision is final.
- [ ] Merge strategy is configured.
- [ ] Discussions are enabled only if there is a moderation plan.
- [ ] Issue labels are configured.
- [ ] Security features are enabled where available.
- [ ] Repository visibility change has been reviewed by the maintainer.

## 12. Final Release Review

- [ ] The release commit hash is recorded.
- [ ] All required CI checks are green on that commit.
- [ ] The public package and repository versions agree.
- [ ] The release can be installed and exercised from scratch.
- [ ] No secrets, confidential examples, internal employer material, or private pilot data are present.
- [ ] No open P0 item remains in [TODO.md](../../TODO.md).
- [ ] The release notes identify known limitations.
- [ ] The repository can be made public without relying on claims that are not yet evidenced.

## Launch Decision

- [ ] **Approved for public release**

Approved by:

- Maintainer: ____________________
- Release commit: ____________________
- Release version: ____________________
- Review date: ____________________
