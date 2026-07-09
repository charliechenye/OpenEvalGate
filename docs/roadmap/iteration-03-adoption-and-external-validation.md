# Iteration 3: OpenEvalGate 0.2.0, Adoption, and Stabilization

## Status

**Not started as a public milestone.** This iteration begins after the repository is public. It covers the first substantive public-alpha release, external practitioner validation, ecosystem integration, and the compatibility work required before `1.0.0`.

## Objective

Establish that OpenEvalGate solves a real practitioner problem outside the maintainer's own examples, while stabilizing evidence, onboarding, machine-readable, and migration contracts.

Additional templates are not a substitute for independent use. Public interest is not the same as adoption, and adoption is not the same as stable compatibility.

## Phase 1: OpenEvalGate 0.2.0 Public Alpha

The `0.2.0` theme is **evidence integrity and minimal adoption**.

### Evidence integrity

- [x] Require non-empty mandatory eval-result fields.
- [x] Recompute and consistency-check core route-match evidence against authoritative eval-case routes.
- [ ] Derive or independently consistency-check workflow-route, destination, handoff, and model-policy claims where source evidence exists.
- [x] Reject duplicate result records.
- [x] Validate timestamps, selected scope, candidate references, and observed-output references.
- [x] Add explicit run provenance and evaluator type. Runtime identity, local digest verification, freshness, recency, and assurance classification are implemented.
- [x] Define framework, input, result, and artifact descriptor rules. Runtime identity, local digest verification, and optional artifact-index identity are implemented.
- [x] Define stale-evidence and recency behavior. Contract and local runtime comparison are implemented.
- [~] Require versioned, non-stale selected evidence for controlled-launch authorization. Manifest-backed identity, non-failed lifecycle, and local freshness/recency classifications are available; complete authorization enforcement remains deferred.

### Minimal onboarding

- [ ] Add `openevalgate init <project> --profile minimal`, or an equivalently deterministic packaged scaffold.
- [ ] Keep the initial profile set small until repeated user demand justifies additional profiles.
- [x] Add a five-minute quickstart from an installed checkout package.
- [ ] Add Linux/macOS and Windows PowerShell instructions.
- [x] Allow a user to produce a useful first report through a documented copy-and-report path.

### Machine-consumable output

- [ ] Add versioned JSON output for `validate`, `check`, and `report`.
- [ ] Define stable finding and blocker IDs in machine output.
- [ ] Document validation, blocked-launch, and internal-error exit behavior.
- [ ] Add an opt-in CI mode that fails when launch is blocked.
- [ ] Defer SARIF until the JSON finding contract is stable.

### Release execution

- [ ] Update package, citation, changelog, and documentation versions consistently.
- [ ] Document breaking changes, migrations, limitations, and deferred work.
- [ ] Verify the exact release commit and artifacts.
- [ ] Create a Git tag and GitHub Release.
- [ ] Publish wheel and source artifacts with checksums.
- [ ] Publish to PyPI only after clean installation and smoke tests pass.
- [ ] Describe `0.2.0` as public alpha, not stable.

## Phase 2: Recruit Design Partners

Target three to five practitioners after the repository is public.

Preferred participants:

- AI product or platform leaders;
- ML or AI engineers shipping assistants or agents;
- AI quality and evaluation practitioners;
- trust, safety, legal, compliance, or operations owners;
- maintainers of adjacent eval or agent tooling.

- [ ] Prepare a one-page design-partner brief.
- [ ] Define the pilot scope and time commitment.
- [ ] Provide a sanitized example and onboarding guide.
- [ ] Collect permission preferences before recording names or organizations.
- [ ] Schedule one structured review with each participant.
- [ ] Ask each participant to identify one confusing concept, one missing control, and one useful output.

### Acceptance criteria

- [ ] At least two participants complete an end-to-end review.
- [ ] Feedback includes specific evidence about usability or launch-decision value.
- [ ] At least one participant completes the workflow without the maintainer operating the CLI for them.
- [ ] No pilot is represented publicly without permission.

## Phase 3: Capture Structured Adoption Evidence

For every pilot, record outside the public repository:

- participant role and relevant expertise;
- organization or domain when disclosure is permitted;
- system or workflow reviewed;
- date and OpenEvalGate version;
- artifacts used;
- setup time and time to first report;
- issues or evidence gaps discovered;
- launch or mitigation decision affected;
- feedback received;
- follow-up change or contribution;
- permission for attribution, anonymized publication, or private use only.

- [ ] Create a repeatable pilot-feedback form.
- [ ] Create a sanitized case-study template.
- [ ] Separate participant statements from maintainer interpretation.
- [ ] Preserve source evidence without committing confidential material.
- [ ] Track repeat use and project upgrades, not only first-time interest.

### Acceptance criteria

- [ ] Every public adoption claim has a traceable source.
- [ ] Private evidence is not accidentally committed.
- [ ] Interest, usage, and adoption are reported as different signals.

## Phase 4: Independent Contributions

- [ ] Create scoped `good first issue` and `help wanted` items from real user pain.
- [ ] Invite design partners to file genuine issues where appropriate.
- [ ] Seek one externally authored example, schema improvement, integration, or documentation pull request.
- [ ] Credit contributors in release notes and `AUTHORS.md`.
- [ ] Document decisions when external proposals are declined.

### Acceptance criteria

- [ ] At least one meaningful issue, review, or contribution is authored outside the maintainer account.
- [ ] Contribution history demonstrates real review and collaboration rather than manufactured activity.

## Phase 5: Ecosystem Integration

Prioritize one integration based on actual user demand.

Candidate paths:

- generic JSONL or CSV import contract;
- Promptfoo result export;
- DeepEval result export;
- Braintrust result export;
- LangSmith trace or evaluation export;
- Arize Phoenix evaluation export.

- [ ] Stabilize the generic internal ingestion schema first.
- [ ] Select one adapter based on repeated pilot demand.
- [ ] Build the adapter end to end with fixtures and integration tests.
- [ ] Document unsupported fields and lossy conversions.
- [ ] Avoid claiming an official partnership without approval.

### Acceptance criteria

- [ ] A user can convert external eval evidence into a valid OpenEvalGate report without manually reconstructing the canonical result format.

## Phase 6: Specification and Compatibility Stabilization

- [ ] Publish a versioned specification separating normative requirements from practitioner guidance.
- [ ] Define behavioral contracts, golden evals, contrast families, routes, stopping boundaries, escalation contracts, handoff payloads, durable resume, capability allocation, provenance, hard blockers, and release decisions.
- [ ] Document required fields, validation rules, failure behavior, and relationships for each primitive.
- [ ] Version public schemas.
- [ ] Define backward-compatibility and deprecation policy.
- [ ] Provide a documented or automated migration for at least one earlier schema version.
- [ ] Add compatibility fixtures covering supported prior schemas.
- [ ] Explain the basis and limitations of default weights and thresholds.
- [ ] Refine defaults only when pilot evidence supports the change.

## Phase 7: External Case Studies and Citable Work

### Case studies

- [ ] Publish one case where OpenEvalGate blocks launch or exposes a material evidence gap.
- [ ] Publish one case where evidence supports a bounded launch.
- [ ] Include reproducible sanitized artifacts when permission allows.
- [ ] State the exercise limitations.
- [ ] Avoid causal claims such as `prevented harm` without evidence.

### Technical report

Working topic:

> Evidence-Backed Release Assurance for Production AI Agents: Behavioral Contracts, Safe Stopping Boundaries, and Human Escalation Metrics

- [ ] Publish only after the methodology and schemas stabilize.
- [ ] Link the report to a tagged repository release.
- [ ] Include independent reviewers or acknowledgements where appropriate.
- [ ] Distinguish illustrative reference scenarios from production studies.

## Phase 8: Practitioner Participation

- [ ] Present the framework in at least two relevant practitioner communities.
- [ ] Run one structured workshop using a real or sanitized workflow.
- [ ] Ask participants to challenge thresholds and blocker semantics.
- [ ] Convert validated questions and feedback into issues or release notes.
- [ ] Contribute at least one substantive improvement to an adjacent project or public guidance process.
- [ ] Avoid promotional drive-by contributions.

## Meaningful Adoption Metrics

Track:

- completed pilots;
- organizations or domains represented;
- repeat users and project upgrades;
- externally authored issues and pull requests;
- integration users;
- approved case studies;
- citations or independent references;
- talks, workshops, and invited reviews;
- blockers or evidence gaps identified during pilots;
- release or mitigation decisions clarified.

Do not use stars, impressions, or page views as primary evidence of utility.

## Evidence Integrity Rules

- Do not create artificial issues, endorsements, or contributions.
- Do not ask reviewers to make claims they cannot independently support.
- Do not publish confidential employer or customer information.
- Do not equate interest with adoption.
- Do not claim prevention of harm without causal evidence.
- Do not store private professional or immigration records in the repository.
- Preserve dated, source-backed evidence outside the repository for legitimate documentation.

## 0.x Stabilization Exit Criteria

- [ ] `0.2.0` is published and explicitly labeled public alpha.
- [ ] Three to five design partners have been contacted.
- [ ] At least two end-to-end external reviews are complete.
- [ ] At least one external issue, review, or contribution exists.
- [ ] At least one sanitized case study is approved.
- [ ] One integration is selected from demonstrated demand and implemented or clearly scheduled.
- [ ] A versioned specification exists.
- [ ] At least one schema migration has been exercised.
- [ ] Adoption evidence is tracked with source integrity.

## OpenEvalGate 1.0.0 Entry Criteria

Begin the `1.0.0` release process only when:

- [ ] Public schemas and migration behavior are stable.
- [ ] CLI commands, exit codes, and machine-readable output are stable.
- [ ] Hard-blocker IDs, applicability rules, and recommendation meanings are stable.
- [~] Provenance and freshness rules are operational for the implemented local classification subset; complete authorization enforcement remains pending.
- [ ] Compatibility fixtures cover supported previous schemas.
- [ ] Multiple independent users have completed the workflow.
- [ ] At least one external contribution and one real integration exist.
- [ ] Upgrade and rollback procedures have been tested.
