# Launch Gates and Evidence Scoring

This document records OpenEvalGate's launch gates, evidence-completeness scoring, evidence bands, and hard-gate policy semantics. Evidence completeness is separate from observed behavioral quality and does not determine a launch recommendation by itself.

## Launch Gates

OpenEvalGate uses the following 23 gates in this order:

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

## Evidence Completeness Scoring

OpenEvalGate uses a 100-point trust-weighted evidence completeness score. It measures how completely a project has documented and reviewed its declared launch controls and governance evidence. It is not a behavioral quality score and does not determine launch readiness by itself.

- Scope readiness: 5
- Trust preservation readiness: 8
- Business behavior contract readiness: 7
- Golden eval readiness: 10
- Tail-risk / P0 failure readiness: 10
- Model selection / arena readiness: 7
- Grounding readiness: 6
- SOP/policy compilation readiness: 5
- Tool/action safety readiness: 8
- Automation boundary readiness: 6
- Human escalation readiness: 5
- Input/output perimeter readiness: 6
- Domain-owner feedback loop readiness: 4
- Observability readiness: 5
- Cost/latency readiness: 3
- Journey/business metrics readiness: 5

Evidence package bands:

- 85-100: Substantially complete
- 50-84: Material gaps
- Below 50: Incomplete

These bands describe evidence completeness only. They do not grant a deployment stage. The final recommendation is determined separately from project validity, behavioral-evidence state, and known hard blockers. Missing, empty, or invalid `eval_results.csv` cannot produce a controlled-launch recommendation.

Explicit review modes, selected-run coverage, critical-case sufficiency, and initial behavioral thresholds are documented in [Review Modes and Behavioral Sufficiency](review-modes.md). Controlled-launch recommendations remain bounded and do not replace provenance, freshness, runtime monitoring, or organizational approval.

Behavioral evidence is reported as one of:

- `Not evaluated — no results provided.`
- `Not evaluated — results file contains no rows.`
- `Invalid — results could not be validated.`
- `Evaluated — valid empirical rows are available.`

`Control evidence completeness threshold met` means only that the evidence score is at least 85, required project artifacts are present, and non-result project validation has no errors. Meeting this threshold does not override hard blockers or grant permission to begin shadow evaluation.

`openevalgate check` validates whether project artifacts and gate declarations are structurally usable. A supported `partial` or `fail` declaration is structurally valid, so it does not make `check` fail; it does create a launch-policy blocker in the report. Unsupported statuses, duplicate standard gates, prohibited `not_applicable` declarations, and malformed required artifacts fail `check`.

## Hard Blockers

Eight centralized hard gates are evaluated independently from the evidence-completeness score:

- Scope and golden eval are always applicable.
- Tail-risk/P0 and human escalation are applicable to high-impact projects.
- Tool/action safety is applicable when the validated action matrix contains actions.
- Observability, rollback, and owner signoff are always applicable.

An applicable hard gate requires `pass`, a meaningful evidence cell, and any gate-specific artifact evidence. `partial`, `fail`, missing, or prohibited `not_applicable` declarations block advancement. When conditional applicability cannot be established because source evidence is missing or invalid, the gate is blocked rather than treated as non-applicable.

Independent blockers, such as an ungated high-risk action or a behavioral escalation regression, remain separate from the eight policy-gate blocker IDs.

For every populated `action_risk_matrix.csv` row, `action` must be nonblank, `risk_tier` must be `low`, `medium`, `high`, or `prohibited`, and `human_review_required` must be `true` or `false`. A row is populated when any cell contains a non-whitespace value. If any row is invalid, the entire matrix fails validation and none of its rows influence action applicability, impact classification, or unsafe-action blockers.
