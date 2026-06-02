# Human Escalation Recertification Checklist

High-risk escalation contracts should be recertified as policies, tools, queue capacity, and user behavior change.

| Review area | Questions to answer | Pass / fail | Notes |
| --- | --- | --- | --- |
| Workflow scope | Has the user journey changed? |  |  |
| Policy | Have eligibility rules, authorization limits, or compliance requirements changed? |  |  |
| Trigger quality | Are triggers still precise and complete? |  |  |
| Clarification budget | Are users being asked unnecessary questions? |  |  |
| Routing | Are cases reaching the right destination? |  |  |
| Queue capacity | Can each destination meet its SLA under normal and peak load? |  |  |
| Fallback behavior | Do fallback paths still work? |  |  |
| Payload schema | Does the schema transfer minimum sufficient context? |  |  |
| Privacy | Are unrelated sensitive fields excluded? |  |  |
| Durable state | Can workflows pause and resume safely? |  |  |
| Idempotency | Are duplicate actions prevented? |  |  |
| Metrics | Are dashboards and alerts still meaningful? |  |  |
| Eval slices | Do evals cover recent incidents and emerging failure modes? |  |  |
| Release gates | Are thresholds still appropriate? |  |  |
| Ownership | Are owners and reviewers still current? |  |  |
| Rollback | Can the team revert policy and routing changes quickly? |  |  |

| Risk tier | Suggested cadence | Minimum reviewers |
| --- | --- | --- |
| Low | Every 6-12 months | Product and engineering |
| Medium | Every 6 months | Product, engineering, and operations |
| High | Every 90 days | Product, engineering, operations, and risk |
| Prohibited or critical path | Every 30-90 days and after every material incident | Product, engineering, operations, risk, and policy or compliance owner |
