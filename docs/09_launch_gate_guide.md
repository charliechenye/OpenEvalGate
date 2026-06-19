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

## Recommendation bands

- 85-100: Ready for controlled launch.
- 70-84: Conditional launch.
- 50-69: Shadow launch only.
- Below 50: Not ready.

Owner signoff is a non-scored launch blocker. A high score does not replace accountable approval.

The Routing / capability allocation gate shares the existing model-selection readiness category. It does not increase the 100-point total. Single-model systems without workflow-specific allocation may mark it `not_applicable`; multi-workflow systems should provide versioned assignments, eval evidence, fallbacks, observability, and rollback.

## Hard Blockers

Regardless of score, the recommendation should be `Not ready` when:

- Scope is missing or failed.
- Golden eval set is missing or invalid.
- Tail-risk/P0 review is missing or failed for high-impact workflows.
- A high-risk action lacks deterministic enforcement or human approval.
- High-risk or low-confidence cases lack an escalation path.
- Rollback is missing or not passing.
- Owner signoff is missing or not passing.
- Observability/monitoring is missing or failed.
