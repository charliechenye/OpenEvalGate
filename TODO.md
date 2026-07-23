# OpenEvalGate Roadmap

This roadmap separates four distinct milestones that should not be treated as one release event:

1. **Public repository:** the code, claims, examples, governance, and repository settings are safe for public inspection.
2. **OpenEvalGate 0.1.0:** the first public-alpha release with the implemented deterministic evidence and adoption foundation.
3. **0.x stabilization:** external adoption, integrations, schema refinement, and migration experience.
4. **OpenEvalGate 1.0.0:** stable public contracts for schemas, CLI behavior, blocker semantics, and compatibility.

OpenEvalGate should be positioned as an **evidence-backed release-assurance framework for production AI assistants and agents**. It is not a complete AI governance platform, eval runner, observability system, runtime guardrail, compliance certification product, or guarantee of safe deployment.

> **Current state:** Public positioning and limitations, deterministic review modes, behavioral sufficiency, centralized hard-gate policy, runtime eval-run identity enforcement, package builds, clean-wheel installation, installed CLI execution, and canonical-report reproduction are implemented. Governance and repository quality work is in place; repository protection, disclosure review, exact-commit verification, and the first public `0.1.0` release handoff remain.

See [Release Milestones](docs/roadmap/release-milestones.md) for the milestone definitions and dependency order.

## Status Legend

- [ ] Not started
- [~] Partially implemented or in progress
- [x] Complete
- [!] Blocked

## Operating Rules

1. Correctness comes before feature breadth.
2. Public visibility does not imply a stable release.
3. A launch recommendation must be supported by execution evidence, not document presence alone.
4. Critical-control failures override aggregate scores.
5. Every public claim must be reproducible or clearly labeled as illustrative, provisional, or externally unvalidated.
6. New templates and playbooks are lower priority than evidence integrity and independent adoption.
7. Backward compatibility becomes a stronger commitment as the project approaches `1.0.0`.
8. Immigration-specific evidence packaging and private professional records remain outside the public repository.

## Milestone A: Make the Repository Public

The repository may become public while remaining pre-1.0 and before publishing `0.1.0`. This milestone is about safe disclosure, bounded claims, governance, reproducibility, and repository protection—not feature completeness.

### A1. Public positioning and limitations

- [x] Lead with `release assurance`, not broad `AI governance` claims.
- [x] Replace unsupported proof language with `examples`, `reference scenarios`, or similarly bounded wording.
- [x] Label repository-authored metrics, outputs, and examples as synthetic or illustrative.
- [x] Add a dedicated limitations and non-claims section.
- [x] State explicitly that OpenEvalGate does not certify compliance, guarantee safe deployment, execute candidate systems, or establish a universal standard.
- [x] Reduce README repetition and move the full gate list, scoring weights, and extended methodology into documentation.
- [x] Review standards and competitive references for precise wording, source version, and review date.

### A2. Public example integrity

- [x] Retain a reproducible blocked example showing that strong documentation cannot override failed behavioral or critical-control evidence.
- [x] Add a reproducible passing controlled-launch reference example.
- [x] Ensure every canonical example is generated from committed inputs without undocumented manual edits.
- [x] Ensure no repository example is presented as production adoption evidence.
- [x] Add a concise comparison between the passing and blocked outcomes.

### A3. Governance, support, and attribution

- [x] Add `SECURITY.md`, `CODE_OF_CONDUCT.md`, `CHANGELOG.md`, contribution guidance, issue forms, and a pull-request template.
- [x] Add maintainer attribution and `CITATION.cff`.
- [x] Add `GOVERNANCE.md`.
- [x] Add `SUPPORT.md`.
- [x] Add `AUTHORS.md` and contribution-credit rules.
- [x] Document release, deprecation, schema-change, and broken-release rollback policies.
- [x] Modernize setuptools license metadata.

### A4. Repository quality and protection

- [x] Run consolidated CI across Python 3.10 through 3.14.
- [x] Build and inspect source and wheel artifacts.
- [x] Install the wheel in a clean environment and exercise the installed CLI.
- [x] Reproduce canonical reports byte-for-byte through the installed wheel.
- [x] Add linting and formatting checks.
- [x] Add an enforceable scoped type-checking baseline; full-package typing remains deferred.
- [x] Add dependency review and lightweight security scanning.
- [ ] Require pull requests and the consolidated `CI` check on `main`.
- [ ] Require branches to be current before merge.
- [ ] Disable force pushes and branch deletion on `main`.
- [ ] Enable dependency alerts, secret scanning, push protection where available, and private vulnerability reporting.
- [ ] Configure repository description, restrained topics, labels, and social preview.

### A5. Disclosure and exact-commit review

- [ ] Audit the current tree and Git history for secrets, confidential material, private pilot evidence, proprietary prompts, unlicensed assets, and unsafe metadata.
- [ ] Remove or rewrite history before public visibility if sensitive material is found.
- [ ] Record the exact public-visibility commit.
- [ ] Confirm all required checks are green on that exact commit.
- [ ] Re-run clean-wheel installation and canonical-report reproduction on that exact commit.
- [ ] Record any accepted public-alpha risks and known limitations.
- [ ] Complete the [Public Launch Checklist](docs/roadmap/public-launch-checklist.md).
- [ ] Change repository visibility to public.

### Explicit deferrals for public visibility

The following are not required merely to make the repository public:

- SARIF output
- external eval-tool adapters
- a hosted service or web UI
- a tagged `0.2.0` release
- published external case studies
- `1.0.0` compatibility guarantees

## Milestone B: Post-release hardening for OpenEvalGate 0.2.0

`0.2.0` is the next substantive public-alpha release after `0.1.0`. Its primary theme is **evidence integrity and minimal adoption**, not feature breadth.

### B1. Strengthen eval-result integrity

- [x] Require non-empty values for mandatory result fields.
- [x] Validate expected routes against referenced eval cases.
- [x] Consistency-check declared route matches and derive route-match metrics.
- [ ] Derive workflow-route, destination, handoff, and model-policy claims where source evidence exists.
- [x] Reject duplicate result keys `(run_id, candidate, trial_id, case_id)`.
- [x] Validate result timestamps and remove CSV row order from informational run chronology.
- [x] Validate supplied output references as safe, contained, existing regular files.
- [ ] Validate candidate registries and pin case, workflow, model, and artifact versions.
- [x] Validate referenced output artifact identity and local SHA-256 digests.
- [x] Prevent invalid core result evidence from influencing summaries or launch decisions.

### B2. Add run provenance and freshness

- [x] Define evaluator kinds and minimum evidence in the v1 contract and enforce evaluator identity at runtime.
- [x] Define candidate identity, run lifecycle, timestamps, and resource descriptors. Runtime identity, digest verification, and freshness resource comparison are implemented.
- [~] Define provenance presence, validity, freshness, recency, assurance, lifecycle, and authorization classifications. Runtime identity, lifecycle, freshness, recency, verified assurance, and `review_context.yaml` enforcement are implemented; complete authorization classification remains deferred.
- [x] Define stale-evidence behavior when current candidate or policy state differs from valid historical evidence. Contract and local runtime comparison are implemented.
- [x] Parse and enforce selected run identity against manifests and compatible result CSVs.
- [x] Validate at runtime that referenced output-artifact metadata and directory identity agree with result rows when optional artifact identity fields are supplied.
- [x] Display runtime identity and lifecycle status in reports.
- [~] Enforce controlled-launch provenance requirements for complete versioned identity, lifecycle, and acceptable local freshness/recency; complete authorization output and broader artifact-version policy remain deferred.

### B3. Provide a minimal adoption path

- [ ] Add a provenance initialization command that generates a minimal run manifest and an optional artifact index from existing result evidence.
- [x] Add `openevalgate init <project> --profile minimal` with a deterministic placeholder scaffold.
- [ ] Keep the initial profile set small; defer speculative profile breadth until user demand is demonstrated.
- [x] Add a five-minute installed-wheel quickstart for Linux/macOS and Windows PowerShell.
- [x] Allow a user to produce a useful first report without copying the full customer-support example.

### B4. Add machine-consumable output

- [x] Add versioned JSON output for `check`, `validate`, and `report`.
- [x] Define stable finding and blocker identifiers in machine output.
- [x] Document exit codes for validation failures, launch blockers, and internal errors.
- [x] Add an opt-in CI mode that fails when launch is blocked.
- [ ] Defer SARIF until the finding model and JSON contract are stable.

### B5. Publish `0.2.0`

- [ ] Update package, citation, and changelog versions consistently.
- [ ] Document breaking changes, migrations, known limitations, and intentionally deferred work.
- [ ] Verify the exact release commit and artifacts.
- [ ] Create a Git tag and GitHub Release.
- [ ] Publish wheel and source artifacts with checksums.
- [ ] Publish to PyPI only after clean installation and smoke tests pass.
- [ ] Describe `0.2.0` as public alpha, not stable.

## Milestone C: 0.x Adoption and Stabilization

- [ ] Recruit three to five design partners after the repository is public.
- [ ] Complete at least two independent end-to-end reviews.
- [ ] Capture structured feedback and permission settings outside the public repository.
- [ ] Obtain at least one externally authored issue, review, example, schema improvement, or pull request.
- [ ] Publish at least one sanitized case study with source-backed claims.
- [ ] Stabilize a generic result-ingestion contract before building vendor-specific adapters.
- [ ] Build one integration selected from actual user demand.
- [ ] Add a versioned specification separating normative requirements from practitioner guidance.
- [ ] Add migration tooling or documented migrations for at least one earlier schema version.
- [ ] Revisit default thresholds and weights using pilot evidence; do not present practitioner defaults as scientific constants.
- [ ] Track completed pilots, repeat use, integrations, external contributions, citations, and decision-relevant gaps rather than vanity metrics.

## Milestone D: OpenEvalGate 1.0.0

`1.0.0` means users can rely on the public contract, not merely that the code runs.

### Stable contracts

- [ ] Project, eval-case, eval-result, review-policy, routing, and escalation schemas are versioned and documented.
- [ ] CLI commands, exit codes, and machine-readable output are stable.
- [ ] Hard-blocker identifiers, applicability rules, and recommendation meanings are stable.
- [ ] Deprecation and migration behavior are tested and documented.
- [ ] At least one previous schema version is supported or migratable.

### Methodology and adoption evidence

- [ ] A versioned specification defines the normative primitives and failure behavior.
- [~] Runtime eval-run identity rules are operational; digest verification, freshness, recency, and verified assurance remain deferred.
- [ ] Multiple independent users have completed end-to-end reviews.
- [ ] At least one external contribution and one real integration exist.
- [ ] At least one sanitized case study is published with explicit limitations.
- [ ] Release notes distinguish implementation evidence, illustrative examples, and external adoption evidence.

### Stable-release definition

- [ ] All `1.0.0` public contracts are covered by compatibility fixtures.
- [ ] No known issue allows malformed or stale evidence to produce a permissive launch recommendation.
- [ ] Upgrade and rollback instructions are tested.
- [ ] The exact `1.0.0` release commit, artifacts, checksums, and documentation are verified.
- [ ] The project is no longer labeled alpha in package metadata.

## Explicit Long-Term Non-Goals

- [ ] Do not make a hosted service a prerequisite for the core framework.
- [ ] Do not add LLM API execution to the deterministic core CLI without a separate, explicit design decision.
- [ ] Do not claim NIST, ISO, OWASP, EU AI Act, or regulatory certification.
- [ ] Do not claim OpenEvalGate is an industry standard.
- [ ] Do not treat stronger models as authorization or safety controls.
- [ ] Do not optimize the roadmap around GitHub stars, impressions, or other vanity metrics.
