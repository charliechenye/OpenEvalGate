# Right-Sized Intelligence Framework

The best production route is not always the strongest model. It is the route where additional capability produces enough outcome lift to justify the latency, interaction effort, operational cost, and risk controls it adds.

Use this framework per scenario or specialist workflow, not only in aggregate.

## Operating Principle

Allocate model capability only when marginal quality lift justifies marginal user friction and system cost.

More intelligence is useful when it changes the user outcome. If it mainly adds delay, longer answers, more clarification, or more operational complexity, it is product friction.

## Decision Dimensions

| Dimension | Question | Evidence to collect |
| --- | --- | --- |
| Task fit | What capability does the task actually require? | Complexity, ambiguity, grounding needs, tool depth, structured-output requirements |
| User friction | What burden does the route impose on the user? | Time to first token, time to resolution, turns to resolution, clarification count, answer length, abandonment |
| Risk envelope | What controls remain mandatory regardless of model capability? | Eligibility checks, approvals, confirmations, blocked actions, audit trails, escalation rate |
| Outcome economics | Did the route improve the end-to-end outcome efficiently? | Resolution rate, repeat contacts, downstream rework, human-review burden, full system cost |

## Quality-Adjusted Cost Per Resolved Task

Use raw inference cost as an input, not the final decision metric.

```text
Quality-adjusted cost per resolved task
= Total system cost / Number of tasks resolved at the required quality bar
```

The numerator should include the real operating cost of the route:

- Model inference and reasoning tokens.
- Retrieval and tool calls.
- Cascade calls and retries.
- Human review.
- Escalation handling.
- Downstream rework.
- Repeat contacts.
- Operational incident cost, where measurable.

The denominator should count tasks resolved at the required quality bar. A low-cost response that creates another support contact, manual workaround, incorrect action, or trust failure is not actually cheap.

## Experiment Interpretation

A routing experiment should separate quality lift from the cost of waiting.

| Arm | Execution path | Purpose |
| --- | --- | --- |
| Arm A | Serve the smaller or faster route immediately | Establish the efficient baseline |
| Arm B | Serve the stronger or slower route with its real response time | Measure net product impact |
| Arm C | Generate with the baseline route but delay delivery to match Arm B | Isolate the user-facing latency penalty |

| Comparison | What it reveals |
| --- | --- |
| Arm A vs. Arm C | Pure latency penalty |
| Arm B vs. Arm C | Whether stronger output compensates for the wait |
| Arm A vs. Arm B | Net impact of the stronger route |

Run the analysis by scenario, workflow, language, risk tier, and complexity slice. A stronger model may matter for conflicting records, exceptions, or policy ambiguity while adding little value to routine status lookup.

## Scorecard

Track routing outcomes with product, safety, and operational metrics together:

- Task success and durable resolution rate.
- Time to first token and time to resolution.
- Turns and clarification questions per resolved task.
- Repeat-contact and escalation rate.
- Tool-selection and tool-argument accuracy.
- Policy compliance.
- Human-review acceptance rate.
- User satisfaction and abandonment.
- Quality-adjusted cost per resolved task.

## Launch Implication

Use the smallest reliable route for the scenario. Escalate to stronger reasoning, fallback, approval, or human review only when the expected outcome lift clears the friction, cost, and risk threshold defined for that workflow.
