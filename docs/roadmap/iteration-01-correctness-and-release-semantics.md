# Iteration 1: Correctness and Release Semantics

## Status

**Core semantics and runtime provenance classification are complete for the implemented local contract subset.** Review modes, controlled-launch behavioral sufficiency, centralized hard-gate policy, fail-closed applicability, deterministic reporting, the proposed eval-run provenance contract, runtime identity enforcement, local digest verification, freshness and recency comparison, review-context validation, and assurance classification are implemented. Remaining work covers complete authorization classification, enriched workflow and handoff claims, and broader artifact-version policy beyond the implemented identity envelope.

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
- [x] Projects without explicit mode receive bounded behavior according to review-policy defaults.

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

Introduce explicit run evidence through the proposed eval-run provenance contract. The contract wraps an existing compatible `eval_results.csv`; runtime identity parsing, local digest verification, assurance, freshness, recency, and `review_context.yaml` comparison are implemented for selected evidence.

Required concepts:

- run ID, lifecycle, and optional timestamps;
- candidate ID and version;
- evaluator type and version where applicable;
- selected eval-set, review-policy, routing-policy, escalation-contract, or action-risk evidence when applicable;
- result CSV and optional artifact-index references;
- current release context for freshness and recency comparison.

- [x] Define evaluator type: human, deterministic, model judge, or hybrid and enforce evaluator identity at runtime.
- [x] Define candidate identity, lifecycle, descriptors, artifact indexing, freshness, recency, and assurance. Runtime validation covers the local digest, lifecycle, assurance, freshness, and recency subset.
- [x] Parse and enforce selected run evidence against current project result rows, output identity, and declared artifact index identity.
- [x] Surface stale and expired evidence classifications in reports.
- [~] Require versioned evidence for controlled-launch authorization. Complete runtime identity, non-failed lifecycle, and local freshness/recency classifications are available; complete authorization classification remains deferred.
- [x] Require manifest-backed result evidence; manifestless conventional result files fail provenance validation while their rows are excluded from behavioral processing and launch decisions.

### Distinguish evidence provenance

Initial contract categories are manifest presence, validity, freshness, recency, assurance, lifecycle, and authorization. Signed attestation and richer review provenance are reserved for future contracts.

- [x] Add runtime identity and lifecycle classifications where they change interpretation.
- [x] Report identity and lifecycle for the selected controlled-launch evidence.
- [~] Require stronger provenance for controlled-launch hard controls. Complete runtime identity, non-failed lifecycle, local assurance, freshness, and recency are enforced where implemented; complete authorization remains deferred.
- [~] Prevent blank or placeholder hard-gate evidence from satisfying centralized hard gates; broader artifact-depth validation remains open.

### Acceptance criteria

- [x] The report identifies runtime identity status, lifecycle, run, candidate, evaluator, framework, results path, and artifact-index path used for the decision when available.
- [x] Contract fixtures define stale candidate, stale input, recency, lifecycle, artifact, unsafe-path, optional artifact-identity, and invalidity branches; runtime projections cover freshness, recency, and assurance.
- [x] Missing, complete, and invalid identity are visibly different, and unbound or invalid evidence cannot be used as behavioral evidence. Declared and verified assurance are distinguished.
- [~] Controlled launch cannot be authorized using unversioned selected-run identity or failed/incomplete lifecycle. Freshness and recency are classified and surfaced; complete authorization enforcement for those classifications remains deferred.

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
- [~] Controlled-launch provenance and freshness contract is proposed; runtime identity, digest, freshness, recency, and assurance classification are implemented while complete authorization remains pending.
- [x] Selected evidence identity vocabulary is visible in reports.
- [x] Centralized gate semantics are covered by regression tests.
- [x] Canonical examples regenerate without undocumented manual edits.
