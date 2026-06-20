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

- `pass`: Evidence is sufficient.
- `partial`: Evidence exists but a mitigation remains.
- `fail`: Evidence is missing or unacceptable.
- `not_applicable`: Gate is intentionally not scored for this launch.

## Evidence completeness bands

The 100-point score measures completeness of declared launch-control and governance evidence. It does not measure observed behavioral quality and must not be interpreted as launch readiness by itself.

- 85-100: Substantially complete.
- 50-84: Material gaps.
- Below 50: Incomplete.

The final recommendation is produced by a separate deterministic assessment. It considers whether the evidence package is sufficient, whether behavioral evidence is missing, empty, invalid, or available, and whether known hard blockers exist.

The sufficiency field is named `Control evidence package sufficient for shadow evaluation`. It does not imply behavioral sufficiency or launch readiness.

Owner signoff is a non-scored launch blocker. High evidence completeness does not replace accountable approval or observed behavioral evidence.

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

## Hard Blockers

Regardless of score, known hard blockers prevent controlled launch when:

- Scope is missing or failed.
- Golden eval set is missing or invalid.
- Tail-risk/P0 review is missing or failed for high-impact workflows.
- A high-risk action lacks deterministic enforcement or human approval.
- High-risk or low-confidence cases lack an escalation path.
- Rollback is missing or not passing.
- Owner signoff is missing or not passing.
- Observability/monitoring is missing or failed.
