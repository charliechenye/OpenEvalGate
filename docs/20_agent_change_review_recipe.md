# Recipe: Review a Change to an AI Assistant or Agent

Use this recipe whenever a team changes a model, prompt, retrieval source,
tool, policy, workflow route, human handoff, or operational control. It helps
an AI product manager decide what must be re-evaluated, what evidence is
missing, and which bounded review outcome is reasonable.

This is practitioner guidance for organizing a release review. It does not
add a new OpenEvalGate gate, threshold, required input, or authorization
classification. The deterministic core still consumes evidence produced by an
external evaluator, harness, trace review, or manual process.

## The operating loop

Treat every material change as a small product decision with four linked
questions:

1. **Approve the review plan:** Is the change understood, owned, and scoped?
2. **Evaluate the affected behavior:** Which existing and new cases can prove
   that the change is safe for the requested scope?
3. **Investigate the result:** If a case fails, is the gap in evidence, policy,
   behavior, routing, operations, or monitoring?
4. **Decide the next bounded action:** Should the team advance the requested
   review, remain in shadow, remediate, pause, roll back, or document the
   decision?

“Approve” in this recipe means that the accountable organization makes a
decision after reviewing the evidence. An OpenEvalGate report or card is a
deterministic input to that decision, not the approval itself.

## Start with the change request

Copy [`templates/agent_behavior_change_request.md`](../templates/agent_behavior_change_request.md)
into the project and complete it before asking for a new model comparison or
rerunning a large suite. The PM should be able to answer:

- What is changing and what is explicitly not changing?
- Which user intents, tools, routes, policies, or human destinations can be
  affected?
- Which risk tier and failure modes are in scope?
- Who owns expected behavior, policy interpretation, evaluation, operations,
  and the release decision?
- What is the rollback or pause trigger if the change regresses?

Do not treat “the prompt changed” or “the model scored higher” as a sufficient
impact analysis. A small implementation change can alter tool eligibility,
refusal, escalation, approval, or recovery behavior.

## Classify the change surface

Use the table to select the smallest sufficient review scope. It is a planning
heuristic, not a replacement for the project’s declared gates.

| Change surface | Inspect first | Add or rerun | Typical owner |
| --- | --- | --- | --- |
| Model, prompt, or decoding | Answer quality, refusal, policy, and boundary slices | Existing golden cases plus nearby contrasts and known regressions | AI product + AI engineering |
| Retrieval, knowledge, or policy source | Grounding, freshness, unsupported claims, and policy-sensitive cases | Source-change cases, stale-context cases, and policy owner review | Product + policy/domain owner |
| Tool or action permission | Eligibility, confirmation, approval, refusal, and prohibited-action cases | Every affected high-risk action and a no-permission contrast | Platform + risk/policy owner |
| Routing or human handoff | Route choice, destination, payload, fallback, and resume behavior | Affected route cases plus wrong-destination and recovery contrasts | Operations + platform owner |
| Monitoring, fallback, or rollback | Detection, pause, escalation, and durable state | Failure-mode cases and an operator response walkthrough | Operations + platform owner |

When multiple surfaces change, use the union of their affected slices. If the
team cannot identify the affected slices, record that as an evidence or policy
gap and do not infer safety from an unchanged aggregate score.

## Select evidence by consequence

Use the existing golden set and add only the cases needed to expose the change:

1. **Regression cases:** behavior that must remain stable.
2. **Changed-behavior cases:** the intended new behavior and its expected
   alternatives.
3. **Contrast cases:** a nearby change in permission, context, risk, or user
   intent that should produce a different result.
4. **Tail-risk cases:** rare, high-impact actions, prohibited requests,
   approval boundaries, escalation failures, and recovery paths.
5. **Fresh samples:** representative current behavior that may reveal drift.

Use [`templates/golden_eval_review_agenda.md`](../templates/golden_eval_review_agenda.md)
to ask domain, policy, operations, and engineering owners whether the cases
represent the actual boundary. Use the existing release-gate template to
identify which slices are blocking, monitored, or limited-rollout concerns.

The weakest sufficient grader principle applies:

- derive tool calls, route, destination, required fields, and state transitions
  deterministically where possible;
- use a rubric for qualitative behavior that cannot be reliably structured;
- use human adjudication for ambiguous or high-impact cases; and
- keep any LLM judge outside the OpenEvalGate deterministic core and calibrate
  it against human review.

## Handoff map

Keep the PM review record connected to the artifacts and outputs that support
it. The report sections below are the existing V1 sections; they are not new
contract fields.

| Review phase | Reusable artifact | Command or output | Read or record | Review mode |
| --- | --- | --- | --- | --- |
| Define the change | [Agent behavior change request](../templates/agent_behavior_change_request.md) and stakeholder brief | Meeting record or PR attachment | Scope, owners, risk surface, rollback trigger | Any mode |
| Select cases | `eval_cases.yaml`, action-risk matrix, review agenda | External evaluator or manual review | Golden Eval Summary, Tail-Risk / P0 Failure Mode Summary | Any mode |
| Validate evidence | Eval results, run manifest, output evidence | `openevalgate validate eval_cases.yaml` and `openevalgate check .` | Eval-Run Identity, Evidence Completeness Score, validation findings | Any mode |
| Assess the change | Review policy and launch-gate review | `openevalgate report . --format card` or `--format json` | Card decision summary, JSON assessment, Review Mode and Behavioral Sufficiency, Critical-Control Status, Hard Blockers | Documentation, shadow, or controlled launch |
| Investigate a miss | [Incident-to-regression recipe](19_incident_to_regression_recipe.md) and incident intake | Re-run the affected cases and report | Required Mitigations, Recommended Next Actions, Final Launch Recommendation | Re-open the affected mode |
| Record the decision | PM controlled-launch recipe and organizational decision record | Link report, JSON, run, and candidate identities | Bounded scope, owner, due date, rollback, and re-review trigger | Organizational review |

## Run the review in order

From the project directory, use the normal V1 handoff:

```bash
openevalgate validate eval_cases.yaml
openevalgate check .
openevalgate report . --format card
openevalgate report . --format json --output /tmp/openevalgate-change-review.json
```

Read the evidence in this order:

1. **Validity:** failed validation or inspection means the package needs repair
   before behavioral results are interpreted.
2. **Scope:** confirm the selected candidate/run and cases cover the proposed
   change and requested review stage.
3. **Critical behavior:** inspect high-risk actions, prohibited behavior,
   required escalation, approval pauses, fallback, and resume behavior.
4. **Blockers:** use stable blocker IDs and assign an owner; do not trade a
   critical failure away against a higher aggregate score.
5. **Next action:** record the smallest new evidence or control change that
   would make the decision reviewable again.

The card is useful for a meeting or pull request. Use the Markdown report for
detailed evidence and JSON for automation. Do not parse Markdown text as a
machine policy interface.

## Investigate a failed change

When the change review fails or a production signal contradicts it, use the
[incident-to-regression recipe](19_incident_to_regression_recipe.md) and keep
the original result traceable. Classify the primary gap before choosing the
fix:

| Finding | Question | Follow-up |
| --- | --- | --- |
| Evidence | Was the needed case, run, output, or provenance missing, invalid, stale, or out of scope? | Repair the evidence and re-evaluate. |
| Policy | Was the expected behavior, risk boundary, or exception unclear? | Update the behavior contract and obtain the relevant owner decision. |
| Behavior | Did the candidate answer, act, refuse, or stop incorrectly? | Fix the candidate and add a regression or contrast case. |
| Routing | Did the agent choose the wrong route, destination, or handoff? | Repair the routing/escalation control and test the trajectory. |
| Operations | Did a tool, dependency, fallback, resume, pause, or rollback path fail? | Repair the operational path and add a failure-mode case. |
| Monitoring | Could the team observe and respond to the failure in time? | Improve signals, ownership, alerting, or review cadence. |

Do not close an investigation with “rerun the benchmark.” State whether the
result requires re-evaluation, a new product or policy decision, a pause or
rollback, or documentation only. Each outcome needs an owner and a due date or
trigger.

## Choose a bounded review outcome

Use the existing report recommendation and project review mode as evidence for
the organizational decision. Record one practical disposition in the change
request or meeting record:

| Disposition | Use when | Required record |
| --- | --- | --- |
| Advance bounded scope | Affected evidence is valid and the requested scope remains supported | Scope, evidence reference, owners, monitoring, and rollback trigger |
| Remain in shadow | The team needs empirical evidence before exposing the requested scope | Missing evidence, collection owner, sample plan, and next review date |
| Remediate and re-evaluate | A behavior, evidence, policy, routing, or operational gap is actionable | Gap category, mitigation, owner, new cases, and closing evidence |
| Pause or roll back | Active risk exceeds the current control boundary | Trigger, operator, safe fallback, affected scope, and recovery review |
| Document only | The finding does not change the release scope or controls | Rationale, affected evidence, owner, and review trigger |

Avoid “approve with a caveat” when a blocker or unresolved scope mismatch is
present. Convert the caveat into a bounded scope, an owner-backed mitigation,
or a pause condition that a reviewer can revisit.

## Close the loop

After the decision:

- link the change request to the report, JSON output, selected run, and
  candidate identity;
- preserve the original evidence when results are rerun;
- add incidents and material misses to the regression set;
- review fresh production samples on the cadence defined by the monitoring
  owner; and
- reopen the review after a candidate, policy, scope, tool, route, or material
  evidence change.

### PM handoff checklist

- [ ] Change surface and bounded release scope are explicit.
- [ ] Affected risk slices include regression, contrast, and relevant tail-risk
  cases.
- [ ] Expected behavior and unacceptable behavior have accountable owners.
- [ ] Deterministic checks are used for structured action and routing claims.
- [ ] The selected candidate/run and evidence references are traceable.
- [ ] Blockers, mitigations, owners, and re-review triggers are recorded.
- [ ] The outcome is bounded and is not presented as organizational approval.
