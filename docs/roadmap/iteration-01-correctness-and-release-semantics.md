# Iteration 1: Correctness and Release Semantics

## Objective

Make OpenEvalGate's launch recommendations semantically honest, empirically grounded, and resistant to self-attested evidence inflation.

The iteration is complete only when a project with strong documentation but weak observed behavior cannot appear highly ready for launch.

## P0.1 Separate Evidence Coverage from Behavioral Readiness

- [x] Rename the current weighted score to `Evidence Completeness Score`.
- [x] Add `Observed Behavioral Quality` as a separate report section.
- [x] Add a separate `Critical-Control Status` that distinguishes known failure, unevaluated behavior, and absence of currently detected blockers.
- [x] Keep `Final Launch Recommendation` independent from the evidence-completeness score.
- [x] Update README, guides, templates, examples, and tests to use the new terminology.

### Acceptance Criteria

- A report may show high evidence completeness and still show low behavioral quality without contradiction.
- The first report screen displays all three dimensions:
  - Evidence completeness.
  - Observed behavioral quality.
  - Critical-control status.
- No code path refers to the evidence-completeness score as overall launch readiness.

## P0.2 Introduce Review Modes

Add a project-level review mode:

```yaml
review_mode: documentation
```

Supported values:

- `documentation`
- `shadow_launch`
- `controlled_launch`

- [ ] Documentation mode validates the evidence package but does not issue a user-facing launch recommendation.
- [ ] Shadow-launch mode requires empirical eval results and critical-slice coverage.
- [ ] Controlled-launch mode requires empirical results, passing hard controls, observability, rollback, and owner signoff.
- [ ] Reject unknown review modes.
- [ ] Add migration behavior for existing projects without an explicit mode.

### Acceptance Criteria

- A project without `eval_results.csv` cannot receive `Ready for controlled launch`.
- Documentation mode reports `Launch determination: not evaluated`.
- Controlled-launch mode fails clearly when required execution evidence is absent.

## P0.3 Centralize Hard-Gate Policy

Create one explicit policy table in code instead of distributing critical-gate semantics across helper functions.

Suggested shape:

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

- [ ] Treat `partial`, `fail`, and missing as blocking when a full pass is required.
- [ ] Define gate-specific `not_applicable` rules.
- [ ] Reject unsupported gate statuses.
- [ ] Remove contradictory blocker wording.
- [ ] Expose the hard-gate policy in generated reports.

### Required Tests

For every hard gate, test:

- [ ] `pass`
- [ ] `partial`
- [ ] `fail`
- [ ] missing
- [ ] `not_applicable`

### Acceptance Criteria

- No partial critical gate can silently avoid a hard blocker.
- Reported blocker reasons match code behavior.

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

- [ ] Define which metrics are informational, gating, or blocking.
- [ ] Support per-project threshold overrides.
- [ ] Support stricter thresholds by risk tier.
- [ ] Define minimum denominators before a rate is considered meaningful.
- [ ] Report `insufficient evidence` instead of treating missing values as good or bad performance.

### Acceptance Criteria

- A critical-slice failure produces a named blocker.
- A metric with insufficient samples cannot be presented as a reliable percentage.
- Threshold values and evidence denominators appear in the report.

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

- User-entered derived booleans cannot contradict source fields.
- Duplicate or stale result records fail validation.
- The report identifies the exact artifact versions used for a launch decision.

## P0.6 Distinguish Evidence Provenance

Introduce evidence provenance categories:

- `self_attested`
- `tool_validated`
- `externally_generated`
- `human_approved`

- [ ] Add provenance to structured gate evidence.
- [ ] Report counts by provenance category.
- [ ] Require stronger provenance for controlled-launch hard gates.
- [ ] Do not award full evidence credit for a path that exists but contains no validated evidence.

### Acceptance Criteria

- A blank Markdown file cannot satisfy a hard gate.
- A self-attested gate is visibly different from a tool-validated or human-approved gate.

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

- [ ] Reports separate evidence completeness, observed behavior, and critical-control status.
- [ ] Controlled-launch recommendations require empirical evidence.
- [ ] Partial critical gates block launch.
- [ ] Critical metrics have explicit thresholds and denominators.
- [ ] Eval results are internally consistent and versioned.
- [ ] Blank or superficial artifacts cannot receive full readiness credit.
- [ ] All new semantics are covered by regression tests.
- [ ] Canonical examples regenerate without undocumented manual edits.
