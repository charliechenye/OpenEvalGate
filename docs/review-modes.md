# Review Modes and Behavioral Sufficiency

OpenEvalGate supports three explicit review modes through an optional
`review_policy.yaml` file.

The three canonical projects under `examples/` include editable policies that
demonstrate different review modes::

- customer support requests controlled launch but remains blocked;
- education requests shadow launch review but remains blocked from shadow evaluation;;
- presales requests documentation review.

These examples teach review-mode semantics without manufacturing a passing
controlled-launch project.

## Modes

- `documentation` validates the control-evidence package and is capped at
  documentation review, even when behavioral results exist.
- `shadow_launch` may authorize bounded shadow evaluation when control
  evidence is sufficient and no hard blockers exist. Missing or empty results
  are allowed; present but invalid results block advancement. A conventional
  `eval_results.csv` without an authoritative `run_manifest.yaml` is unbound
  provenance evidence and fails validation before its rows can be used.
- `controlled_launch` is an explicit opt-in that requires a selected run and
  candidate, complete manifest-backed eval-run identity, non-failed lifecycle,
  and sufficient behavioral evidence.

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

When a review policy selects a run, OpenEvalGate uses the matching run-scoped
manifest when present, or a root manifest only when it declares the selected
run. A root result file bound to another run's valid root manifest is not
treated as unbound merely because a different run is selected.

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

## Core eval-result integrity contract

Every result row requires non-empty `run_id`, `case_id`, `candidate`,
`evaluator`, `actual_route`, `expected_route`, `route_match`, `passed`,
`score`, `reviewed_by`, and `reviewed_at` values. `trial_id`, failure details,
`observed_output_path`, notes, and optional enriched fields may remain blank
unless an existing conditional rule requires them.

Result identity is `(run_id, candidate, trial_id, case_id)`, with whitespace
trimmed from every component. A blank trial ID remains part of the identity,
so repeated trials must use distinct non-empty trial IDs.

`reviewed_at` accepts `YYYY-MM-DD` or an ISO datetime with a mandatory `T`
separator and explicit `Z` or `+HH:MM`/`-HH:MM` offset. Fractional seconds are
allowed. Date-only values preserve the reviewer's recorded local date with
day-level precision. Offset-aware values preserve the recorded local time;
UTC normalization is internal and used only to compare explicit instants.
OpenEvalGate does not rewrite stored or displayed timestamps to UTC.
Timezone-naive datetimes are rejected because the project declares no default
timezone.

A supplied output path must be project-relative, remain inside the resolved
project root, and identify an existing regular file. Absolute paths, URLs,
Windows drive and UNC paths, parent traversal, directories, missing files, and
symlink escapes are invalid. Both slash forms are treated as separators on
every operating system. These checks establish reference safety, not artifact
provenance.

`eval_cases.yaml` owns `expected_route`. Each result-row value must agree with
the referenced case, and declared `route_match` must agree with the value
derived from `actual_route` and the case route. Route-match metrics are derived;
`passed` remains evaluator- or harness-declared. Any invalid row invalidates
the complete result file, including selected-scope summaries.

Whole-file `latest_run_id` is informational. It uses each run's greatest
recorded review value, compares calendar dates first, compares explicit
instants on the same date, and uses the lexically greatest run ID for a final
tie. It never selects controlled-launch scope: controlled launch continues to
use the exact `run_id` and `candidate` in `review_policy.yaml`.

## Decision order and limitations

Assessment considers control-evidence validity and completeness, policy
validity, behavioral-result validity, project hard blockers, selected-scope
validity, coverage and depth, behavioral invariants, and configured thresholds
in that order. Missing required evidence fails closed for controlled launch.

A controlled-launch recommendation is bounded to the selected candidate, run, evaluation scope, declared thresholds, monitoring requirements, rollback conditions, and unresolved organizational approvals.

The recommendation is not a universal safety claim, compliance certification,
unrestricted production approval, or substitute for runtime monitoring and
organizational authorization.

This iteration validates runtime eval-run identity, selected-scope result
identity, supplied output references, recognized output metadata, and optional
artifact-index identity. It does not yet verify provenance digests, freshness,
recency, `review_context.yaml`, enriched workflow-route or handoff claims, or
every routing and model-policy field.
