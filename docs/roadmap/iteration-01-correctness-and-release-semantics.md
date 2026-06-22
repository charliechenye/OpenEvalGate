# Iteration 1: Correctness and Release Semantics

## Status

**Partially complete.** Review modes, controlled-launch behavioral sufficiency, centralized hard-gate policy, fail-closed gate applicability, and deterministic reporting are complete. Result integrity, version pinning, and evidence provenance remain open.

## Objective

Make OpenEvalGate's launch recommendations semantically honest, empirically grounded, and resistant to self-attested evidence inflation.

The iteration is complete only when a project with strong documentation but weak observed behavior cannot appear highly ready for launch, and when empirical evidence is sufficient—not merely present—for the requested review mode.

## P0.1 Separate Evidence Coverage from Behavioral Readiness

- [x] Rename the current weighted score to `Evidence Completeness Score`.
- [x] Add `Observed Behavioral Quality` as a separate report section.
- [x] Add a separate `Critical-Control Status` that distinguishes known failure, unevaluated behavior, and absence of currently detected blockers.
- [x] Keep `Final Launch Recommendation` independent from the evidence-completeness score.
- [x] Update README, guides, templates, examples, and tests to use the new terminology.

### Acceptance Criteria

- [x] A report may show high evidence completeness and still show low behavioral quality without contradiction.
- [x] The first report screen displays evidence completeness, observed behavioral quality, and critical-control status.
- [x] No code path refers to the evidence-completeness score as overall launch readiness.

## P0.2 Introduce Review Modes

Add a project-level review mode:

```yaml
review_mode: documentation
```

Supported values:

- `documentation`
- `shadow_launch`
- `controlled_launch`

- [x] Documentation mode is capped at documentation review.
- [x] Shadow-launch mode permits bounded shadow evaluation without requiring results.
- [x] Controlled-launch mode requires sufficient selected empirical results and passing hard controls.
- [x] Reject unknown review modes.
- [x] Add backward-compatible shadow behavior for projects without an explicit mode.

### Acceptance Criteria

- [x] A project without `eval_results.csv` cannot receive `Ready for controlled launch`.
- [ ] Documentation mode reports `Launch determination: not evaluated`.
- [ ] Controlled-launch mode fails clearly when required execution evidence is absent.

## P0.3 Centralize Hard-Gate Policy

The centralized policy covers:

```python
HARD_GATE_POLICY = {
    "scope gate": {"required_status": "pass"},
    "golden eval gate": {"required_status": "pass"},
    "tail-risk / p0 failure mode gate": {"required_status": "pass"},
    "tool/action safety gate": {"required_status": "pass"},
    "human escalation gate": {"required_status": "pass"},
    "observability gate": {"required_status": "pass"},
    "rollback gate": {"required_status": "pass"},
    "owner signoff gate": {"required_status": "pass"},
}
```

- [x] Treat `partial`, `fail`, and missing as blocking when a full pass is required.
- [x] Define gate-specific `not_applicable` rules.
- [x] Reject unsupported gate statuses.
- [x] Remove contradictory blocker wording.
- [x] Expose the hard-gate policy in generated reports.
- [x] Require meaningful evidence and gate-specific artifact evidence where applicable.
- [x] Treat unknown conditional applicability as blocking rather than permissive.
- [x] Keep invalid action-risk evidence diagnostic-only and outside policy decisions.

### Required Tests

For every hard gate, test:

- [x] `pass`
- [x] `partial`
- [x] `fail`
- [x] missing
- [x] `not_applicable`
- [x] duplicate declarations and aliases
- [x] unsupported statuses
- [x] blank and placeholder evidence
- [x] applicable, non-applicable, and unknown conditional contexts

### Acceptance Criteria

- [x] No partial critical gate can silently avoid a hard blocker.
- [x] Reported blocker reasons match code behavior.
- [x] Invalid structured evidence cannot create a trusted positive or permissive negative policy result.

## P0.4 Define Critical Behavioral Thresholds

Add a structured threshold policy. Defaults must be documented as practitioner defaults rather than scientific constants.

Candidate metrics:

- Eval pass rate.
- Critical-slice pass rate.
- Required-escalation recall.
- Destination accuracy.
- Context-preservation rate.
- Resume success rate.
- Deterministic/no-model path compliance.
- Model-policy compliance.
- Prohibited-action rate.
- Contrast-family reliability.

- [x] Define initial pass-rate and route-match metrics as controlled-launch gates.
- [x] Support per-project threshold configuration.
- [ ] Support stricter thresholds by risk tier.
- [x] Require selected rows and explicit case-coverage denominators.
- [x] Report unavailable evidence instead of substituting zero.
- [x] Preserve critical-case failure overrides regardless of aggregate score.

### Acceptance Criteria

- [x] Every required critical-case failure prevents controlled launch.
- [ ] A metric with insufficient samples cannot be presented as a reliable percentage.
- [x] Threshold values and evidence denominators appear in the report.

## P0.5 Strengthen Eval-Result Integrity

- [ ] Require non-empty values for mandatory result columns.
- [ ] Validate `expected_route` against the referenced eval case.
- [ ] Recompute `route_match` from expected and actual routes.
- [ ] Recompute workflow-route match where possible.
- [ ] Validate `observed_output_path` exists when supplied.
- [ ] Validate `reviewed_at` as an ISO date or datetime.
- [ ] Add explicit evaluator type: human, deterministic, model judge, or hybrid.
- [ ] Add run timestamp and framework version.
- [ ] Add eval-set version, routing-policy version, and escalation-contract version.
- [ ] Reject duplicate result keys such as `(run_id, trial_id, case_id, candidate)`.
- [ ] Determine latest runs from timestamps, not CSV row order.
- [ ] Validate candidate and workflow references.

### Acceptance Criteria

- [ ] User-entered derived booleans cannot contradict source fields.
- [ ] Duplicate or stale result records fail validation.
- [ ] The report identifies the exact artifact versions used for a launch decision.

## P0.6 Distinguish Evidence Provenance

Introduce evidence provenance categories:

- `self_attested`
- `tool_validated`
- `externally_generated`
- `human_approved`

- [ ] Add provenance to structured gate evidence.
- [ ] Report counts by provenance category.
- [ ] Require stronger provenance for controlled-launch hard gates.
- [~] Prevent blank or placeholder gate evidence from satisfying applicable hard gates. Implemented for centralized hard gates; broader artifact-depth validation remains open.

### Acceptance Criteria

- [~] A blank or placeholder hard-gate evidence cell cannot satisfy an applicable hard gate.
- [ ] A self-attested gate is visibly different from a tool-validated or human-approved gate.

## P1.1 Add a Structured Project Manifest

Add a versioned project manifest such as `openevalgate.yaml`.

Suggested minimum fields:

```yaml
schema_version: "1.0"
framework_version: "0.2.0"
review_mode: controlled_launch
project:
  id: refund-assistant
  system_name: Customer Support Refund Assistant
  risk_class: high
artifacts:
  eval_cases: eval_cases.yaml
  eval_results: eval_results.csv
  launch_gate_review: launch_gate_review.yaml
```

- [ ] Use the manifest as the canonical source for project identity and artifact locations.
- [ ] Retain backward compatibility for existing canonical filenames during migration.
- [ ] Add clear migration warnings.

## P1.2 Replace Fragile Markdown Parsing

- [ ] Move normative launch-gate data into YAML or JSON.
- [ ] Keep Markdown as a generated or human-readable review format.
- [ ] Validate evidence references and owners structurally.
- [ ] Add schema tests and backward-compatibility fixtures.

## Exit Criteria

Iteration 1 is complete when:

- [x] Reports separate evidence completeness, observed behavior, and critical-control status.
- [x] Missing, empty, or invalid empirical results cannot produce a controlled-launch recommendation.
- [x] Partial critical gates block advancement.
- [x] Initial controlled-launch metrics have explicit thresholds and denominators.
- [ ] Eval results are internally consistent and versioned.
- [~] Blank or superficial hard-gate declarations cannot receive passing policy treatment; broader artifact-depth and provenance checks remain open.
- [x] Centralized gate semantics are covered by regression tests.
- [x] Canonical examples regenerate without undocumented manual edits.
- [x] Review modes and behavioral evidence sufficiency are implemented.
