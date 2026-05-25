# Launch Gate Guide

OpenEvalGate uses launch gates to convert product, engineering, safety, and operations concerns into evidence-based launch decisions.

## Required gates

1. Scope gate
2. Trust preservation gate
3. Business behavior contract gate
4. Golden eval gate
5. Tail-risk / P0 failure mode gate
6. Model selection gate
7. Model arena gate
8. Grounding gate
9. SOP/policy compilation gate
10. Tool/action safety gate
11. Automation boundary gate
12. Human escalation gate
13. Input filter gate
14. Output critic gate
15. Domain-owner feedback loop gate
16. Observability gate
17. Cost/latency gate
18. Journey metric / durable resolution gate
19. Business trust metric gate
20. Drift monitoring gate
21. Rollback gate
22. Owner signoff gate

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
