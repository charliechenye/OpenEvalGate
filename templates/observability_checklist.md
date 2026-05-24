# Observability Checklist

| Signal | Required before launch | Owner | Notes |
| --- | --- | --- | --- |
| Request and response IDs | yes | platform | Needed for incident review. |
| Retrieved context IDs | yes | platform | Needed for grounding audits. |
| Tool calls and outcomes | yes | platform | Needed for action safety review. |
| Output critic decision | yes | ai_quality | show, revise, escalate, block. |
| Human escalation reason | yes | operations | Needed for workflow improvement. |
| User feedback | yes | product | Explicit and implicit feedback. |
| Latency and token cost | yes | engineering | Track p50, p95, and outliers. |
| Drift samples | yes | ai_quality | Review fresh production samples. |
