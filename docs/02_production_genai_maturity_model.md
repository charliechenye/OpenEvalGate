# Production GenAI Maturity Model

## Level 0 — Demo

Prompt + model + happy-path examples.

At this level, the team can show potential but cannot make a launch claim. There is no stable scope, no golden eval set, no known failure boundary, and no production evidence.

## Level 1 — Scoped assistant

Defined supported/unsupported use cases, input filters, basic grounding.

The assistant has a job. Users and reviewers can tell what it should and should not do. Launch is still risky because behavior is not yet systematically evaluated.

## Level 2 — Evaluated assistant

Golden eval set, regression tests, output critic, launch gates.

The team can test behavior against product-specific cases. This is the minimum level for a serious controlled launch.

## Level 3 — Governed assistant

Policy compiler, deterministic action gates, audit logs, human escalation.

The system separates model reasoning from enforcement. High-impact actions are gated, escalations are reviewable, and launch decisions have evidence.

## Level 4 — Adaptive platform

Model garden, internal arena, model routing, drift monitoring, cost controls.

The team can compare and route models based on actual product behavior, not public benchmark reputation. Fresh production samples continuously improve eval coverage.

## Level 5 — Enterprise GenAI operating system

Reusable infrastructure across teams, standardized evals, governance, observability, incident response.

Launch readiness becomes an organization-wide operating discipline. Teams share templates, gates, incident processes, and evidence standards.
