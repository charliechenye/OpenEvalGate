# OpenEvalGate Roadmap

This roadmap tracks the work required to make OpenEvalGate technically credible, easy to adopt, and ready for public release.

OpenEvalGate should be positioned as an **evidence-backed release-assurance framework for production AI assistants and agents**. It should not claim to be a complete AI governance platform, eval runner, observability system, runtime guardrail, or compliance certification product.

## Status Legend

- [ ] Not started
- [~] In progress
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

- [ ] Rename the current `Overall Readiness Score` to `Evidence Completeness Score` or `Launch-Control Coverage Score`.
- [ ] Add a separate `Observed Behavioral Quality` section derived from `eval_results.csv`.
- [ ] Add a separate `Critical-Control Status` with explicit pass/fail semantics.
- [ ] Prevent the CLI from recommending `Ready for controlled launch` without empirical eval results.
- [ ] Define minimum result coverage for shadow and controlled-launch reviews.
- [ ] Add configurable thresholds for critical metrics.
- [ ] Make critical-slice failures override all aggregate scores.

### Fix hard-gate semantics

- [ ] Treat `partial`, `fail`, and missing as blocking for gates that require a full pass.
- [ ] Define the complete list of hard gates in code rather than distributing the logic across conditionals.
- [ ] Define when `not_applicable` is permitted for each gate.
- [ ] Add tests for all gate statuses across every hard gate.
- [ ] Ensure blocker messages match the actual implementation.

### Require execution evidence

- [ ] Introduce explicit review modes: `documentation`, `shadow_launch`, and `controlled_launch`.
- [ ] Require `eval_results.csv` for shadow and controlled-launch recommendations.
- [ ] Require critical eval-slice coverage before controlled launch.
- [ ] Recompute route-match and policy-compliance fields rather than trusting user-entered booleans where possible.
- [ ] Validate output references, timestamps, evaluator metadata, run metadata, and duplicate result keys.
- [ ] Pin framework, eval-case, routing-policy, and escalation-contract versions in each run.

### Add continuous integration

- [ ] Add GitHub Actions for Python 3.10 through 3.13.
- [ ] Run the full test suite on every pull request.
- [ ] Build and install the wheel in a clean environment.
- [ ] Run CLI smoke tests against all canonical examples.
- [ ] Verify committed generated reports match current CLI output.
- [ ] Add linting, formatting, and type checking.
- [ ] Add dependency review and a lightweight security scan.
- [ ] Configure branch protection to require CI checks.

### Establish clear authorship and citation

- [ ] Replace anonymous package authorship with `Chenye (Charlie) Zhu`.
- [ ] Update the copyright line to `Chenye Zhu and OpenEvalGate contributors`.
- [ ] Add `CITATION.cff`.
- [ ] Add `AUTHORS.md` with contribution-credit rules.
- [ ] Add project URLs and maintainer metadata to `pyproject.toml`.
- [ ] Create a tagged release and stable release notes before public launch.

## P1: Required for a Strong Public Launch

### Improve onboarding

- [ ] Add `openevalgate init <project>`.
- [ ] Support `minimal`, `standard`, `high-risk`, and `multi-agent` profiles.
- [ ] Add a five-minute quickstart using the minimal profile.
- [ ] Add a concise example that passes all controlled-launch gates.
- [ ] Retain a deliberately blocked example that demonstrates why aggregate scores are insufficient.
- [ ] Add JSON output for `check` and `report`.
- [ ] Add `openevalgate --version`.

### Formalize the methodology

- [ ] Add a versioned `SPECIFICATION.md`.
- [ ] Define behavioral contracts, contrast families, safe stopping boundaries, escalation contracts, capability allocation, hard blockers, and evidence provenance.
- [ ] Mark normative requirements separately from practitioner guidance.
- [ ] Document schema versioning and backward-compatibility policy.
- [ ] Explain the basis and limitations of default weights and thresholds.
- [ ] Avoid presenting initial practitioner defaults as scientifically validated constants.

### Add open-source project infrastructure

- [ ] Add `SECURITY.md`.
- [ ] Add `CODE_OF_CONDUCT.md`.
- [ ] Add `CHANGELOG.md` with an `[Unreleased]` section.
- [ ] Add `GOVERNANCE.md`.
- [ ] Add `SUPPORT.md`.
- [ ] Add issue and pull-request templates.
- [ ] Define a release, deprecation, and schema-change process.
- [ ] Label contribution opportunities by scope and difficulty.

### Tighten public positioning

- [ ] Lead with `release assurance`, not broad `AI governance` claims.
- [ ] Reduce repetition in the README.
- [ ] Put a concrete blocked-launch output near the top of the README.
- [ ] Move the full gate list, score weights, and extended FAQ into documentation.
- [ ] Add a limitations section.
- [ ] Add explicit non-claims: no compliance certification, no runtime enforcement, and no claim of universal readiness.
- [ ] Review every standards reference for version, date, and precise wording.

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

- [ ] All P0 work is complete.
- [ ] CI is green on the release commit.
- [ ] The package installs and runs from a clean wheel.
- [ ] A passing example and a blocked example are reproducible.
- [ ] The report cleanly separates evidence completeness, observed behavior, and critical-control status.
- [ ] Authorship, citation, security, governance, and release metadata are present.
- [ ] At least one independent practitioner has completed a structured pilot or review.
- [ ] The README explains the category and value in under one minute.
- [ ] The public-launch checklist has no unresolved P0 item.
