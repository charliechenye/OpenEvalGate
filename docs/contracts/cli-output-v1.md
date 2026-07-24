# CLI Output Contract v1

OpenEvalGate can emit deterministic JSON for automation and a compact Markdown
decision card for CI summaries and cross-functional launch reviews.

JSON is the machine-readable compatibility path. Default text, Markdown, and
the decision card are deterministic within a release but non-parseable. JSON
is opt-in with `--format json`; the decision card is opt-in with
`openevalgate report <project> --format card`.

## Commands

```text
openevalgate validate <eval_cases> --format json
openevalgate check <project> --format json
openevalgate report <project> --format json
openevalgate report <project> --format card
```

Every JSON document has:

- `schema_version`, currently the string `"1"`;
- `tool.name` and `tool.version`;
- `command`;
- `status`;
- `issues` where applicable;
- project-relative paths only.

Report JSON additionally contains `assessment`, `behavioral_sufficiency`,
`run_identity`, `blockers`, `limitations`, and recommended next actions.
Existing validation and blocker identifiers are preserved as stable identifiers;
consumers must not infer policy from diagnostic prose alone.

The serializer emits UTF-8 JSON with sorted keys, two-space indentation, LF
line endings, and no generated timestamps. This makes output suitable for
review, hashing, and reproducibility checks.

## Exit behavior

| Command | Default result | Exit `0` | Exit `1` | Exit `2` |
| --- | --- | --- | --- | --- |
| `validate` | text or JSON validation | Eval cases valid | Eval cases invalid | CLI usage/internal error |
| `check` | text or JSON structural check | Project valid | Project invalid | CLI usage/internal error |
| `report` | Markdown, card, or JSON report | Report generated | Only with `--fail-on-blocked`, the recommendation is blocked | CLI usage/internal error |

Without `--fail-on-blocked`, a report may describe a blocked recommendation
and still exit `0`; report generation is intentionally distinct from a CI gate.

## Decision card

The card is designed for `$GITHUB_STEP_SUMMARY`, pull requests, tickets, and
review agendas. It includes the recommendation, review mode, evidence score,
behavioral and critical-control status, provenance freshness and recency,
blockers, next actions, and the limitation that the result is not deployment
authorization or compliance certification.

## Compatibility

The JSON schema is stable for Core Compatibility v1. Consumers must pin
`schema_version`, tolerate additive fields, and use blocker and provenance
finding IDs rather than matching human-readable report text. See
[Core Compatibility v1](core-compatibility-v1.md).
