# OpenEvalGate Roadmap

This roadmap tracks the work required to make OpenEvalGate technically credible, easy to adopt, and ready for public release.

OpenEvalGate should be positioned as an **evidence-backed release-assurance framework for production AI assistants and agents**. It should not claim to be a complete AI governance platform, eval runner, observability system, runtime guardrail, or compliance certification product.

> **Repository state:** Iteration 1 hard-gate semantics and the core public-repository infrastructure are complete. Release-artifact inspection, clean-wheel installation, installed CLI execution, and installed-wheel report reproduction are implemented. Verification on the exact public-release commit, repository protection, governance and support documentation, release metadata, behavioral-sufficiency policy, and independent external review remain open.

## Status Legend

- [ ] Not started
- [~] Partially implemented or in progress
- [x] Complete
- [!] Blocked

## Operating Rules

1. Correctness comes before feature breadth.
2. A launch recommendation must be supported by execution evidence, not document presence alone.
3. Critical-control failures override aggregate scores.
4. Every public claim must be reproducible from repository artifacts.
5. New templates are lower priority than independent adoption of the existing framework.
6. Public repository content should focus on practitioner value. Immigration-specific evidence packaging belongs outside the repository.

## Iteration Order

1. [Iteration 1: Correctness and Release Semantics](docs/roadmap/iteration-01-correctness-and-release-semantics.md)
2. [Iteration 2: Public Repository and Release Readiness](docs/roadmap/iteration-02-public-repository-readiness.md)
3. [Iteration 3: Adoption and External Validation](docs/roadmap/iteration-03-adoption-and-external-validation.md)
4. [Public Launch Checklist](docs/roadmap/public-launch-checklist.md)

## P0: Must Complete Before Public Release

### Correct the readiness model

- [x] Rename the current weighted score to `Evidence Completeness Score`.
- [x] Add a separate `Observed Behavioral Quality` section derived from `eval_results.csv`.
- [x] Add a separate `Critical-Control Status` that distinguishes known failure, unevaluated behavior, and absence of currently detected blockers.
- [x] Prevent the CLI from recommending `Ready for controlled launch` without empirical eval results.
- [x] Define configurable result coverage for controlled-launch reviews.
- [x] Add configurable initial pass-rate and route-match thresholds.
- [x] Make every required critical-case failure override aggregate scores.

### Fix hard-gate semantics

- [x] Treat `partial`, `fail`, and missing as blocking for gates that require a full pass.
- [x] Define the complete list of hard gates in code rather than distributing the logic across conditionals.
- [x] Define when `not_applicable` is permitted for each gate.
- [x] Add tests for all supported statuses and missing declarations across every hard gate.
- [x] Ensure blocker messages match the actual implementation.
- [x] Keep invalid action-risk evidence diagnostic-only and unavailable to policy decisions.

### Require execution evidence

- [x] Introduce explicit review modes: `documentation`, `shadow_launch`, and `controlled_launch`.
- [x] Prevent missing, empty, or invalid `eval_results.csv` from producing a controlled-launch recommendation.
- [x] Require complete critical eval-slice coverage before controlled launch.
- [ ] Recompute route-match and policy-compliance fields rather than trusting user-entered booleans where possible.
- [ ] Validate output references, timestamps, evaluator metadata, run metadata, and duplicate result keys.
- [ ] Pin framework, eval-case, routing-policy, and escalation-contract versions in each run.
- [ ] Define evidence provenance and freshness requirements.

### Continuous integration and repository verification

- [x] Add one consolidated GitHub Actions check covering Python 3.10 through 3.13.
- [x] Run the full test suite on Python 3.10 and Python 3.13.
- [x] Run lightweight install, compile, import, and CLI checks on Python 3.11 and Python 3.12.
- [x] Build source and wheel distributions.
- [x] Install the built wheel in a clean environment and exercise the installed CLI.
- [x] Run CLI smoke tests against all canonical examples.
- [x] Verify committed generated reports match current CLI output byte-for-byte, including reproduction through the installed wheel.
- [x] Inspect wheel and source-distribution contents and metadata.
- [x] Use Node 24-compatible GitHub Actions.
- [ ] Add linting, formatting, and type checking.
- [x] Add dependency maintenance through Dependabot.
- [ ] Add dependency review and a lightweight security scan.
- [ ] Configure branch protection to require the consolidated `CI` check.

### Establish clear authorship and citation

- [x] Identify Chenye Zhu as project author and maintainer in package metadata.
- [x] Update the copyright line to `Chenye Zhu and OpenEvalGate contributors`.
- [x] Add `CITATION.cff` with Chenye Zhu and the Charlie Zhu alias.
- [ ] Add `AUTHORS.md` with contribution-credit rules.
- [x] Add project URLs and maintainer metadata to `pyproject.toml`.
- [x] Add README maintainer and citation guidance.
- [ ] Create a tagged release and stable release notes before public launch.

### Establish public repository governance

- [x] Add `SECURITY.md`, `CODE_OF_CONDUCT.md`, and `CHANGELOG.md`.
- [x] Expand `CONTRIBUTING.md` with validation, trust-boundary, and evidence-hygiene requirements.
- [x] Add structured issue forms and a pull-request template.
- [x] Add Dependabot configuration.
- [ ] Add `GOVERNANCE.md` and `SUPPORT.md`.
- [ ] Document release, deprecation, and schema-change policy.
- [ ] Modernize setuptools license metadata before its February 18, 2027 deprecation deadline.
- [ ] Configure repository labels and public support boundaries.
- [ ] Enable private vulnerability reporting and applicable security features.

## P1: Required for a Strong Public Launch

### Improve onboarding

- [ ] Add `openevalgate init <project>`.
- [ ] Support `minimal`, `standard`, `high-risk`, and `multi-agent` profiles.
- [ ] Add a five-minute quickstart using the minimal profile.
- [ ] Add a concise example that passes all controlled-launch gates after controlled-launch semantics exist.
- [x] Retain a deliberately blocked example that demonstrates why aggregate scores are insufficient.
- [ ] Add JSON output for `check` and `report`.
- [x] Add `openevalgate --version`.

### Formalize the methodology

- [ ] Add a versioned `SPECIFICATION.md`.
- [ ] Define behavioral contracts, contrast families, safe stopping boundaries, escalation contracts, capability allocation, hard blockers, evidence provenance, and controlled-launch authorization.
- [ ] Mark normative requirements separately from practitioner guidance.
- [ ] Document schema versioning and backward-compatibility policy.
- [ ] Explain the basis and limitations of default weights and thresholds.
- [ ] Avoid presenting initial practitioner defaults as scientifically validated constants.

### Tighten public positioning

- [ ] Lead with `release assurance`, not broad `AI governance` claims.
- [ ] Reduce repetition in the README.
- [x] Put a concrete blocked-launch output near the top of the README.
- [ ] Move the full gate list, score weights, and extended FAQ into documentation.
- [ ] Add a dedicated limitations section.
- [x] State that OpenEvalGate does not execute models, replace runtime guardrails, or guarantee safe deployment.
- [ ] Add explicit non-claims covering compliance certification and universal readiness.
- [ ] Review every standards reference for version, date, and precise wording.

### Improve release and integration ergonomics

- [x] Add clean-wheel installation validation.
- [x] Add `openevalgate --version` and ensure it matches package metadata.
- [ ] Add JSON output for CI and external integrations.
- [ ] Add SARIF output for GitHub-native findings.
- [ ] Package project templates or add a deterministic scaffolding command.
- [x] Inspect source and wheel contents in CI.

## P2: Adoption and Ecosystem Growth

- [ ] Recruit three to five private-beta design partners.
- [ ] Capture structured feedback from each design partner.
- [ ] Publish at least two sanitized external case studies.
- [ ] Obtain at least one externally authored issue, example, or pull request.
- [ ] Build one integration adapter for an established eval or observability tool.
- [ ] Publish a citable technical report describing the methodology and reference implementation.
- [ ] Present the framework in at least two practitioner communities.
- [ ] Track meaningful adoption evidence rather than vanity metrics.
- [ ] Maintain an external evidence log for pilots, citations, talks, integrations, and independent endorsements.

## Explicit Non-Goals Before Public Release

- [ ] Do not add a hosted service.
- [ ] Do not add authentication or a web UI.
- [ ] Do not add LLM API execution to the core CLI.
- [ ] Do not add more broad playbooks unless requested by real users.
- [ ] Do not claim NIST, ISO, OWASP, or regulatory compliance.
- [ ] Do not claim OpenEvalGate is an industry standard.
- [ ] Do not optimize the roadmap around GitHub stars.

## Public-Ready Definition

OpenEvalGate is ready to become public only when:

- [ ] All remaining P0 work is complete or explicitly accepted as a documented launch risk.
- [x] The core public-readiness changes from PR #5 are merged.
- [ ] CI is green on the exact public-release commit.
- [ ] Branch protection requires the consolidated `CI` check.
- [x] The built wheel installs and the installed CLI runs in a clean environment.
- [ ] A blocked example is reproducible and the limitations of the current shadow-only ceiling are explicit.
- [x] The report cleanly separates evidence completeness, observed behavior, and critical-control status.
- [x] Authorship, citation, security, contribution, changelog, issue-template, and dependency-maintenance infrastructure are present.
- [ ] Governance, support, release-process, and deprecation documentation are present.
- [ ] At least one independent practitioner has completed a structured pilot or review, or the absence is explicitly accepted and disclosed as a launch risk.
- [ ] The README explains the category and value in under one minute.
- [ ] The public-launch checklist has no unresolved required item.
