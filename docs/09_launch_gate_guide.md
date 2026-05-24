# Launch Gate Guide

OpenEvalGate uses launch gates to convert product, engineering, safety, and operations concerns into evidence-based launch decisions.

## Required gates

1. Scope gate
2. Golden eval gate
3. Model selection gate
4. Model arena gate
5. Grounding gate
6. SOP/policy compilation gate
7. Tool/action safety gate
8. Input filter gate
9. Output critic gate
10. Human escalation gate
11. Observability gate
12. Cost/latency gate
13. Drift monitoring gate
14. Rollback gate
15. Owner signoff gate

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
