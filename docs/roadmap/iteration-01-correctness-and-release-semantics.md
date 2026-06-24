# Iteration 1: Correctness and Release Semantics

## Status

**Core semantics and runtime eval-run identity enforcement are complete; provenance freshness remains open.** Review modes, controlled-launch behavioral sufficiency, centralized hard-gate policy, fail-closed applicability, deterministic reporting, the proposed eval-run provenance contract, and runtime identity enforcement are documented. Remaining work is to verify provenance digests, compare freshness and recency against current release context, and make empirical evidence attributable to exact artifact versions beyond the implemented identity envelope.

This iteration supports two milestones:

- the final correctness work required before public visibility; and
- the evidence-integrity foundation for OpenEvalGate `0.2.0`.

## Objective

Make OpenEvalGate's launch recommendations semantically honest, empirically grounded, and resistant to evidence inflation or ambiguity.

A project with strong documentation but weak behavior must not appear ready. A controlled-launch recommendation must identify the selected run, candidate, evidence scope, thresholds, critical failures, and the artifact versions that produced the result.

## Completed Foundations

### Separate evidence coverage from behavioral readiness

- [x] Rename the weighted score to `Evidence Completeness Score`.
- [x] Add `Observed Behavioral Quality` as a separate report section.
- [x] Add `Critical-Control Status`.
- [x] Keep the final recommendation independent from evidence completeness.
- [x] Display evidence completeness, behavioral evidence, and critical-control status separately.

### Introduce review modes

Supported modes:

- `documentation`
- `shadow_launch`
- `controlled_launch`

- [x] Documentation mode is capped at documentation review.
- [x] Shadow mode permits bounded shadow evaluation.
- [x] Controlled-launch mode requires selected empirical evidence and passing controls.
- [x] Missing or invalid results cannot authorize controlled launch.
- [x] Unknown review modes are rejected.
- [x] Legacy projects without explicit mode receive bounded backward-compatible behavior.

### Centralize hard-gate policy

The centralized policy covers Scope, Golden eval, Tail-risk/P0, Tool/action safety, Human escalation, Observability, Rollback, and Owner signoff.

- [x] Treat `partial`, `fail`, and missing as blocking when a full pass is required.
- [x] Define gate-specific `not_applicable` rules.
- [x] Reject unsupported statuses and duplicate declarations.
- [x] Require meaningful evidence for applicable hard gates.
- [x] Treat unknown conditional applicability as blocking.
- [x] Keep invalid action-risk evidence diagnostic-only.
- [x] Cover supported, missing, duplicate, placeholder, and fail-closed paths with tests.

### Define initial behavioral sufficiency

- [x] Support project-configured pass-rate and route-match thresholds.
- [x] Require selected rows and explicit case-coverage denominators.
- [x] Require complete critical-case coverage.
- [x] Preserve critical-case failure overrides.
- [x] Report unavailable evidence rather than substituting zero.
- [ ] Support stricter default threshold profiles by risk tier after pilot evidence exists.
- [ ] Prevent small or insufficient samples from being presented as reliable percentages without qualification.

## Public-Visibility Correctness Work

These items protect the central public claim that OpenEvalGate produces deterministic, evidence-backed release recommendations.

### Validate result integrity

- [x] Require non-empty values for mandatory result fields.
- [x] Validate `expected_route` against the referenced eval case.
- [x] Consistency-check `route_match` and derive route-match metrics.
- [ ] Recompute or consistency-check workflow-route match where possible.
- [ ] Recompute or consistency-check destination match where structured handoff evidence exists.
- [ ] Validate candidate registries and pin case, workflow, model, and artifact versions.
- [x] Validate `reviewed_at` as an ISO date or offset-aware datetime.
- [x] Reject duplicate result keys `(run_id, candidate, trial_id, case_id)`.
- [x] Validate supplied output references and reject unsafe, missing, non-file, or escaping paths.
- [x] Remove CSV row order as an implicit source of run chronology.

### Acceptance criteria

- [x] Core route-match booleans cannot contradict authoritative source fields.
- [ ] Enriched workflow, destination, handoff, and model-policy booleans are derived where possible.
- [x] Duplicate records cannot inflate coverage or pass rates.
- [x] Broken output references fail validation.
- [x] Invalid core result evidence cannot influence behavioral metrics, blockers, or recommendations.
- [x] Existing valid canonical examples remain reproducible.

## OpenEvalGate 0.2.0 Evidence Work

### Add versioned run provenance

Introduce explicit run evidence through the proposed eval-run provenance contract. The contract wraps an existing compatible `eval_results.csv`; runtime identity parsing and enforcement are implemented for selected evidence, while digest verification, verified assurance, freshness, recency, and `review_context.yaml` comparison remain deferred.

Required concepts:

- run ID, lifecycle, and optional timestamps;
- candidate ID and version;
- evaluator type and version where applicable;
- selected eval-set, review-policy, routing-policy, escalation-contract, or action-risk evidence when applicable;
- result CSV and optional artifact-index references;
- current release context for freshness and recency comparison.

- [x] Define evaluator type: human, deterministic, model judge, or hybrid and enforce evaluator identity at runtime.
- [~] Define candidate identity, lifecycle, descriptors, artifact indexing, freshness, recency, and assurance. Runtime identity and lifecycle checks are implemented; digest verification, verified assurance, freshness, and recency remain deferred.
- [x] Parse and enforce selected run evidence against current project result rows, output identity, and declared artifact index identity.
- [ ] Surface stale evidence in reports after freshness comparison is implemented.
- [~] Require versioned evidence for controlled-launch authorization. Complete runtime identity and non-failed lifecycle are required; non-stale evidence waits on freshness and recency implementation.
- [x] Retain bounded legacy support for documentation and shadow review while blocking legacy evidence from controlled launch.

### Distinguish evidence provenance

Initial contract categories are manifest presence, validity, freshness, recency, assurance, lifecycle, and authorization. Signed attestation and richer review provenance are reserved for future contracts.

- [x] Add runtime identity and lifecycle classifications where they change interpretation.
- [x] Report identity and lifecycle for the selected controlled-launch evidence.
- [~] Require stronger provenance for controlled-launch hard controls. Complete runtime identity and non-failed lifecycle are enforced; verified assurance, freshness, and recency remain deferred.
- [~] Prevent blank or placeholder hard-gate evidence from satisfying centralized hard gates; broader artifact-depth validation remains open.

### Acceptance criteria

- [x] The report identifies runtime identity status, lifecycle, run, candidate, evaluator, framework, results path, and artifact-index path used for the decision when available.
- [~] Contract fixtures define stale candidate, stale input, recency, lifecycle, artifact, unsafe-path, optional artifact-identity, and invalidity branches; runtime identity projection is covered, while freshness and recency reporting remain pending.
- [~] Legacy, complete, and invalid identity are visibly different, and invalid evidence cannot be treated as legacy evidence. Declared-versus-verified assurance remains deferred until digest verification.
- [~] Controlled launch cannot be authorized using unversioned selected-run identity or failed/incomplete lifecycle. Stale-run blocking remains deferred until freshness comparison is implemented.

## Deferred Correctness Work

### Structured project manifest

A versioned project manifest such as `openevalgate.yaml` remains a likely pre-1.0 capability, but it is not required merely to make the repository public.

- [ ] Use a manifest as the canonical source for project identity and artifact locations.
- [ ] Retain backward compatibility for existing canonical filenames during migration.
- [ ] Add clear migration warnings.

### Replace normative Markdown parsing

- [ ] Move normative launch-gate data into YAML or JSON.
- [ ] Keep Markdown as generated or human-readable review output.
- [ ] Validate evidence references and owners structurally.
- [ ] Add backward-compatibility fixtures.

## Exit Criteria

Iteration 1 is complete when:

- [x] Reports separate evidence completeness, observed behavior, and critical-control status.
- [x] Missing, empty, or invalid empirical results cannot authorize controlled launch.
- [x] Partial critical gates block advancement.
- [x] Initial controlled-launch thresholds and denominators are explicit.
- [x] Core eval results are internally consistent and duplicate-safe.
- [~] Controlled-launch provenance and freshness contract is proposed; runtime identity enforcement is implemented while digest verification, freshness, recency, and verified assurance remain pending.
- [x] Selected evidence identity vocabulary is visible in reports.
- [x] Centralized gate semantics are covered by regression tests.
- [x] Canonical examples regenerate without undocumented manual edits.
