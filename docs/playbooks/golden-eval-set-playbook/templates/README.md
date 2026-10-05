# Golden template catalog

The only generic **V1 CLI input template** is
[templates/golden_eval_case.yaml](../../../../templates/golden_eval_case.yaml).
It needs completion; see the [fill-in requirements](../../../../templates/README.md).
The [domain case examples](../README.md#example-categories) are complete V1
case documents that can be validated directly, but contain no run results.

All files below are **human design and review worksheets**. The CLI does not
read them, including YAML files named `release_gate` or `decision_record`.
All filled policies, limits, rubric values, counts, and outcomes are synthetic
teaching examples, not default standards or production evidence.

| Worksheet | Purpose |
| --- | --- |
| [Stakeholder alignment](stakeholder_alignment_brief.md) | Define scope, sources of authority, prohibited behavior, and owners. |
| [Comparison and grading](comparison-and-grading.md) | Freeze baseline/candidate, cases, fixtures, graders, and policy; isolate trials; adjudicate unknown checks. |
| [Release gate design](release_gate_template.yaml) | Design required slices and blocking rules; translate only supported controls into `review_policy.yaml`. |
| [Decision record](decision_record_template.yaml) | Separate acceptance of a repair from organizational rollout authorization. |
| [Review agenda](eval_review_agenda.md) | Review completeness, operational readiness, and stop/rollback conditions. |
| [Incident intake](incident_ingestion_template.md) | Turn production failures into versioned cases and runner assertions. |

The website starter kit's version/trial protocol, trust-preserving rubric,
missing-evidence rules, and repair-versus-release decision record have been
adapted into these worksheets. Existing alignment and intake papers remain
the maintained equivalents; no second case or schema template is needed.
