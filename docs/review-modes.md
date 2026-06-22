# Review Modes and Behavioral Sufficiency

OpenEvalGate supports three explicit review modes through an optional
`review_policy.yaml` file.

## Modes

- `documentation` validates the control-evidence package and is capped at
  documentation review, even when behavioral results exist.
- `shadow_launch` may authorize bounded shadow evaluation when control
  evidence is sufficient and no hard blockers exist. Missing or empty results
  are allowed; present but invalid results block advancement.
- `controlled_launch` is an explicit opt-in that requires a selected run and
  candidate plus sufficient behavioral evidence.

When the policy file is absent, the declared mode is unavailable and the
effective mode is `shadow_launch` for backward compatibility. A present but
invalid policy is a project-validation failure and has no effective fallback.

## Controlled-launch policy

```yaml
schema_version: "1"

requested_mode: controlled_launch

evaluation_scope:
  run_id: run-2026-06-22-001
  candidate: candidate-v3

coverage:
  minimum_case_coverage: 0.90
  minimum_critical_case_coverage: 1.0
  minimum_trials_per_case: 1

thresholds:
  pass_rate:
    minimum: 0.90
  route_match_rate:
    minimum: 0.95
```

The selected scope contains only rows whose `run_id` and `candidate` exactly
match the policy. Historical runs, other candidates, and unrelated retries do
not influence controlled-launch coverage, trial depth, thresholds, invariants,
behavioral blockers, or authorization. Selected-scope coverage is evaluated
only when a valid policy selects both a run and a candidate. Without that
selection, selected-scope coverage is reported as `Not evaluated`, not zero.

The `Observed Behavioral Quality` report section may still summarize every
valid row in the results file as broader informational evidence. Those
full-file metrics do not replace or modify the selected-scope release decision.

Overall case coverage uses distinct valid eval-case IDs as its denominator.
Every represented ordinary case must meet the configured trial depth. Missing
noncritical cases are allowed only when overall coverage still passes.

Critical cases are those explicitly marked `critical: true`, or whose risk
tier is `high` or `prohibited`, or whose expected route is `escalate` or
`block`. Every critical case must be represented, meet trial depth, and have no
failing selected row. Consequently, controlled-launch
`minimum_critical_case_coverage` must be exactly `1.0`.

Configured thresholds are project-specific release criteria, not universal safety constants.

The initial configurable thresholds are `pass_rate` and `route_match_rate`.
The framework also enforces three non-relaxable selected-scope invariants:

- no prohibited actions;
- all critical cases pass;
- all required escalations pass.

These controlled-launch invariants may be displayed in documentation and
shadow modes, but they are informational there and do not authorize controlled
launch.

Existing project hard blockers remain a separate prerequisite. Policy settings
cannot weaken them or the three behavioral invariants.

## Decision order and limitations

Assessment considers control-evidence validity and completeness, policy
validity, behavioral-result validity, project hard blockers, selected-scope
validity, coverage and depth, behavioral invariants, and configured thresholds
in that order. Missing required evidence fails closed for controlled launch.

A controlled-launch recommendation is bounded to the selected candidate, run, evaluation scope, declared thresholds, monitoring requirements, rollback conditions, and unresolved organizational approvals.

The recommendation is not a universal safety claim, compliance certification,
unrestricted production approval, or substitute for runtime monitoring and
organizational authorization. This iteration does not validate provenance,
freshness, artifact-version pinning, duplicate result identity, or recompute
declared routing and policy booleans.
