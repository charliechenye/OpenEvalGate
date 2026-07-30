# Investigation Recipe: Turn an Incident Into a Regression Case

Use this recipe after a production incident, user complaint, human override,
appeal, policy change, or trace review reveals that an assistant or agent may
have crossed an unsafe or unacceptable boundary.

The objective is not merely to replay the failure. The objective is to create
reviewable evidence that explains what happened, whether the existing gate
should have caught it, what changes, and when the release decision must be
reopened.

## Start with the incident record

Copy the [incident-ingestion template](playbooks/golden-eval-set-playbook/templates/incident_ingestion_template.md)
and preserve the original evidence outside the repository when it contains
confidential user or customer information.

Record:

- the affected workflow, candidate, and approximate time window;
- user and business impact, including whether a human intervened;
- the input context, retrieved context, tool calls, route, handoff, and final
  state that can be safely retained;
- the expected behavior and the observed behavior;
- whether the case was represented in the selected eval scope;
- the report, run ID, candidate ID/version, and blocker or finding IDs relevant
  to the review.

Do not write a conclusion before recording the evidence. “The model was weak”
is not an investigation classification.

## Classify the control gap

Choose the smallest primary category that explains the failure:

| Category | Diagnostic question | Typical next action |
| --- | --- | --- |
| Evidence gap | Was the needed evidence missing, invalid, stale, or excluded? | Repair the evidence package and rerun the review. |
| Policy gap | Was the business rule, risk tier, boundary, or expected route unclear? | Update the behavior contract, scope, or policy owner review. |
| Behavior failure | Did the agent answer, act, refuse, or stop incorrectly? | Fix the candidate and add a regression or contrast case. |
| Routing/escalation failure | Did it choose the wrong route, destination, or handoff? | Repair routing/escalation controls and test the trajectory. |
| Operational failure | Did a tool, dependency, fallback, resume, or rollback path fail? | Repair the control path and add a failure-mode case. |
| Monitoring gap | Could the team observe and respond to the failure in time? | Improve signals, alerting, ownership, or review cadence. |

Multiple categories may apply, but keep one primary category so ownership and
release impact remain clear.

## Decide whether the gate should have caught it

Compare the incident with the selected evidence package:

1. Was the exact case present, or was there a meaningful contrast family?
2. Did the expected route, tool behavior, stopping boundary, and final state
   match the incident’s risk?
3. Did the selected run and candidate actually cover the case?
4. Were the result rows valid, sufficiently repeated, and current for the
   review?
5. Did a hard blocker, threshold, or critical invariant apply?
6. Was the failure visible to the report, or did the evidence contract omit it?

If the case was represented and passed, explain whether the miss came from
insufficient sampling, a weak expected-behavior contract, an incorrect route
expectation, a rubric limitation, or an operational condition absent from the
eval. If it was not represented, add the case and expand the surrounding
decision boundary rather than only replaying the original prompt.

## Draft the regression case

Use the template’s Proposed Eval Case table. The case should include:

- realistic user input and relevant context;
- expected and unacceptable behavior;
- expected tool and admission behavior;
- expected workflow route and human destination where applicable;
- risk tier and policy reference;
- a named owner;
- whether failure blocks release, limits rollout, or is monitored.

For a high-impact boundary, add nearby contrast cases: a safe case, the
incident case, and a case where a small context or permission change should
produce a different decision. This tests the boundary instead of rewarding
memorization of one example.

## Choose the release disposition

Record exactly one immediate disposition:

- **Re-evaluate:** the candidate or evidence changed and the affected scope
  needs new results.
- **Re-approve:** the behavior is acceptable only after a scope, policy, or
  owner decision is revisited.
- **Roll back or pause:** the risk is active and the existing control boundary
  is not sufficient.
- **Document only:** no release-control change is needed, but the decision and
  rationale must be preserved.

Every disposition needs an owner, a due date or trigger, and a statement of
what evidence closes the follow-up. A regression case without a re-evaluation
decision is incomplete operationally.

## Close the loop

After the case and mitigation are ready:

```bash
openevalgate validate eval_cases.yaml
openevalgate check .
openevalgate report . --format card
```

Compare the new report with the incident record. Confirm that the selected
scope, blocker status, and next action changed for the intended reason. Keep
the original incident evidence and the new evaluation evidence separately
traceable; do not rewrite history by replacing the original result.

