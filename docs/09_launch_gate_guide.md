# Launch Gate Guide

OpenEvalGate uses launch gates to convert product, engineering, safety, and operations concerns into evidence-based launch decisions.

This gate-based approach is aligned with AI risk-management and governance frameworks such as the [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework), [NIST AI RMF Generative AI Profile](https://www.nist.gov/itl/ai-risk-management-framework/ai-rmf-generative-ai-profile), and [ISO/IEC 42001](https://www.iso.org/standard/81230.html).

## Required gates

1. Scope gate
2. Trust preservation gate
3. Business behavior contract gate
4. Golden eval gate
5. Tail-risk / P0 failure mode gate
6. Model selection gate
7. Model arena gate
8. Routing / capability allocation gate
9. Grounding gate
10. SOP/policy compilation gate
11. Tool/action safety gate
12. Automation boundary gate
13. Human escalation gate
14. Input filter gate
15. Output critic gate
16. Domain-owner feedback loop gate
17. Observability gate
18. Cost/latency gate
19. Journey metric / durable resolution gate
20. Business trust metric gate
21. Drift monitoring gate
22. Rollback gate
23. Owner signoff gate

## Status values

- `pass`: The declaration claims completion. Applicable hard gates must also contain meaningful evidence and satisfy any required artifact checks.
- `partial`: Evidence exists but a mitigation remains.
- `fail`: Evidence is missing or unacceptable.
- `not_applicable`: A conditional gate is not required only when validated project context establishes non-applicability.

## Evidence completeness bands

The 100-point score measures completeness of declared launch-control and governance evidence. It does not measure observed behavioral quality and must not be interpreted as launch readiness by itself.

- 85-100: Substantially complete.
- 50-84: Material gaps.
- Below 50: Incomplete.

The final recommendation is produced by a separate deterministic assessment. It considers whether the evidence package is sufficient, whether behavioral evidence is missing, empty, invalid, or available, and whether known hard blockers exist.

The structural field is named `Control evidence completeness threshold met`. Meeting this threshold does not override hard blockers or grant permission to begin shadow evaluation.

Owner signoff is a non-scored launch blocker. High evidence completeness does not replace accountable approval or observed behavioral evidence.

## Validation versus launch policy

`openevalgate check` answers whether artifacts and declarations are structurally usable. Supported `partial` and `fail` values are valid declarations, so they do not fail structural validation. The report separately evaluates whether those declarations block advancement.

Unsupported statuses on any row, duplicate aliases that resolve to the same standard gate, malformed rows, and prohibited `not_applicable` declarations fail validation. Unknown custom gate names are allowed when they use the standard status vocabulary, but they are neither scored nor evaluated as hard gates.

## Launch decision outputs

The generated report independently states:

- Behavioral evidence status.
- Critical-control status.
- Maximum permitted stage.
- Final launch recommendation.
- Recommended next action.

Malformed results are `Invalid`, not missing evidence. Known blockers remain `Fail` even when behavioral evidence has not been provided.

Valid result rows with no known blockers use `No known blockers detected`, not `Pass`. The maximum permitted stage remains `Shadow evaluation`, and controlled-launch readiness remains undetermined until coverage and threshold policy is implemented.

The Routing / capability allocation gate shares the existing model-selection readiness category. It does not increase the 100-point total. Single-model systems without workflow-specific allocation may mark it `not_applicable`; multi-workflow systems should provide versioned assignments, eval evidence, fallbacks, observability, and rollback.

## Hard-Gate Policy

The generated report evaluates these gates in a stable order:

| Gate | Applicability | Additional evidence |
| --- | --- | --- |
| Scope | Always | Valid `assistant_prd.md` |
| Golden eval | Always | Valid `eval_cases.yaml` |
| Tail-risk / P0 failure mode | High-impact projects | `p0_failure_mode_checklist.md` |
| Tool/action safety | Projects with declared actions | Valid `action_risk_matrix.csv` |
| Human escalation | High-impact projects | `human_escalation_design.md` |
| Observability | Always | Meaningful declared evidence |
| Rollback | Always | Meaningful declared evidence |
| Owner signoff | Always | Meaningful declared evidence |

For an applicable gate, `partial`, `fail`, missing, and `not_applicable` are blocking. A `pass` with blank or placeholder evidence such as `none`, `n/a`, `TBD`, or `unknown` is also blocking. Conditional applicability is tri-state: true, false, or unknown. Unknown applicability is blocked because missing evidence must not create a permissive result.

A valid empty action matrix establishes that tool/action safety is not applicable. A missing or invalid matrix leaves applicability unknown and fails project validation independently. Unsafe high-risk rows continue to create the separate `ungated_high_risk_action` blocker even when the declared gate says `pass`.
