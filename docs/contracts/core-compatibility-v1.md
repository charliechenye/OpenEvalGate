# Core Compatibility v1

OpenEvalGate `0.1.0` is stable for this defined, local core. This is not a
claim that every repository template, playbook, adapter, or future integration
is stable.

## Covered surface

The Core Compatibility v1 promise covers:

- the `openevalgate validate`, `check`, `report`, `init`, and `--version` CLI
  commands; their documented options; and exit behavior;
- JSON output selected with `--format json`, as defined by
  [CLI Output Contract v1](cli-output-v1.md) and
  `schemas/cli-output-v1.schema.json`;
- assessment states, recommendation semantics, and hard-blocker identifiers;
- V1 evidence inputs and their schemas: eval cases, review policy, routing
  policy, escalation contract, run manifest, review context, artifact index,
  eval results, and action-risk matrix;
- provenance finding identifiers registered in
  [Eval-Run Provenance Contract v1](eval-run-provenance-v1.md); and
- Python 3.10 through 3.14.

Only `openevalgate.__version__` is a supported Python API. Other imports,
dataclasses, and module internals are implementation details.

## Compatibility rules

V1 inputs require the exact string `schema_version: "1"`. A missing,
malformed, duplicated, unsupported, or unnamespaced policy field is invalid.
YAML `extensions` objects and CSV headers beginning `x_` are the only reserved
places for non-policy producer metadata; extensions cannot authorize a launch.
There is no legacy parser mode or migration command.

V1 semantics, blocker IDs, provenance finding IDs, JSON fields, CLI options,
and exit behavior will not be silently removed or changed. A later major
contract may add V2, but V1 remains available for its stated support period.
Any intentional V1 change requires an explicit compatibility decision,
fixture update, and changelog entry.

JSON is the sole machine-readable compatibility surface. Default text,
decision cards, and Markdown reports remain deterministic within a release,
but are not parseable contracts and may evolve in a later release.

## Stable decision vocabulary

Assessment and recommendation values emitted in V1 JSON are contractual. A
blocked hard control always overrides aggregate evidence scoring. A
documentation score alone never authorizes launch.

The stable hard-blocker IDs are:

- `missing_scope`
- `missing_golden_eval`
- `missing_tail_risk_review`
- `missing_tool_action_safety`
- `missing_escalation_path`
- `missing_monitoring`
- `missing_rollback`
- `missing_owner_signoff`
- `ungated_high_risk_action`
- `invalid_escalation_contract`
- `invalid_routing_policy`
- `missing_eval_run_provenance`
- `provenance_lifecycle_failed`
- `provenance_lifecycle_incomplete`
- `critical_escalation_regression`

When an ID is not applicable, it is absent; consumers must not infer an
authorization decision from diagnostic prose or extension metadata.

## Explicitly experimental

Rubrics, scorecards, templates, playbooks, vendor adapters, external-runner
examples, complete provenance authorization, and any future hosted or runtime
integration are experimental. They may inform a review only through the
validated V1 evidence fields and never become hidden policy inputs.
