# Iteration 1: Correctness and Release Semantics

## Status

**Core semantics complete; provenance contract proposed; runtime evidence integrity remains open.** Review modes, controlled-launch behavioral sufficiency, centralized hard-gate policy, fail-closed applicability, deterministic reporting, and the proposed eval-run provenance contract are documented. The remaining work is to parse and verify provenance at runtime, make empirical evidence attributable to exact artifact versions, and prevent stale or self-contradictory inputs from authorizing launch.

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

Introduce explicit run evidence through the proposed eval-run provenance contract. The contract wraps an existing compatible `eval_results.csv`; runtime parsing and enforcement remain pending.

Required concepts:

- run ID, lifecycle, and optional timestamps;
- candidate ID and version;
- evaluator type and version where applicable;
- selected eval-set, review-policy, routing-policy, escalation-contract, or action-risk evidence when applicable;
- result CSV and optional artifact-index references;
- current release context for freshness and recency comparison.

- [~] Define evaluator type: human, deterministic, model judge, or hybrid. Contract proposed; runtime validation pending.
- [~] Define candidate identity, lifecycle, descriptors, artifact indexing, freshness, recency, and assurance. Contract proposed; runtime validation pending.
- [ ] Parse and verify selected run evidence against current project artifacts.
- [ ] Surface stale or mismatched evidence in reports.
- [ ] Require versioned, non-stale evidence for controlled-launch authorization.
- [~] Retain bounded legacy support for documentation and shadow review. Contract proposed; runtime behavior pending.

### Distinguish evidence provenance

Initial contract categories are manifest presence, validity, freshness, recency, assurance, lifecycle, and authorization. Signed attestation and richer review provenance are reserved for future contracts.

- [~] Add provenance classifications to structured evidence where they change interpretation. Contract proposed; runtime integration pending.
- [ ] Report provenance for the selected controlled-launch evidence.
- [ ] Require stronger provenance for controlled-launch hard controls.
- [~] Prevent blank or placeholder hard-gate evidence from satisfying centralized hard gates; broader artifact-depth validation remains open.

### Acceptance criteria

- [ ] The report identifies the exact run, candidate, framework, and artifact versions used for the decision.
- [~] Contract fixtures define stale candidate and policy evidence; runtime reporting of stale or mismatched evidence remains pending.
- [ ] Declared evidence is visibly different from verified evidence, and invalid evidence cannot be treated as legacy evidence.
- [ ] Controlled launch cannot be authorized using an unpinned or stale selected run.

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
- [~] Controlled-launch provenance and freshness contract is proposed; runtime enforcement remains pending.
- [~] Selected evidence provenance vocabulary is proposed; report visibility remains pending.
- [x] Centralized gate semantics are covered by regression tests.
- [x] Canonical examples regenerate without undocumented manual edits.
