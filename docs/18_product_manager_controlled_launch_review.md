# Product Manager Recipe: Review a Bounded Controlled Launch

Use this recipe when an assistant or agent is proposed for a limited production
release and the product manager needs a decision packet for a cross-functional
review. It is designed for the person accountable for the product decision, not
necessarily the person who ran the evaluations.

This recipe uses the current Core Compatibility v1 behavior. A report or
recommendation is evidence for an organizational decision; it is not approval,
compliance certification, or a guarantee of safe deployment.

## The decision to make

Decide whether the proposed change can advance to the declared review stage and
scope. Keep the scope concrete:

- which assistant or agent and candidate version;
- which users, workflow, geography, or traffic percentage;
- which actions are autonomous;
- which actions require approval, escalation, refusal, or a safe fallback;
- when the decision expires or must be revisited.

If the scope cannot be stated, stop the review and ask the team to define the
operating boundary before interpreting scores.

## Minimum review packet

Ask the builder or evaluator for:

1. the business behavior contract and assistant scope;
2. the golden eval cases, including critical, boundary, adversarial, and
   tail-risk cases relevant to the proposed scope;
3. the selected eval results and run manifest when empirical results exist;
4. the action-risk, routing, and escalation evidence;
5. observability, rollback, ownership, and launch-gate evidence;
6. the requested review mode and selected candidate/run identity.

Synthetic examples and documentation placeholders are useful for learning the
workflow, but they are not production evidence.

## Run the deterministic checks

From the project directory or checkout:

```bash
openevalgate validate eval_cases.yaml
openevalgate check .
openevalgate report . --format card
openevalgate report . --format json --output /tmp/openevalgate-decision.json
```

Use the Markdown report when the meeting needs detailed evidence and the card
for the agenda, pull request, or CI summary. Use JSON for automation; do not
parse human-readable report text for policy decisions.

## Read the result in this order

### 1. Is the evidence package valid?

A failed `validate` or `check` means the package cannot support the requested
review. Missing, malformed, contradictory, duplicated, unbound, or invalid
evidence must be repaired before interpreting behavioral metrics.

### 2. What behavior was actually evaluated?

Confirm that the selected scope covers the risky actions and boundary cases in
the proposed release. Look beyond the aggregate score:

- critical-case coverage and failures;
- required-escalation recall and destination accuracy;
- prohibited actions and late escalation;
- trajectory and end-state outcomes;
- rollback, observability, and human-resume evidence.

A strong documentation score cannot compensate for a critical behavioral or
control failure.

### 3. What blocks advancement?

Read blocker IDs and reasons before reading the recommendation. For every
blocker, assign one disposition:

- fix the behavior and rerun the affected cases;
- repair or strengthen the evidence;
- change the operating boundary or required human path;
- pause, roll back, or keep the release in shadow mode.

Do not dismiss a blocker because the overall score is high.

### 4. What is the bounded next decision?

Record the recommendation, effective review mode, selected candidate/run,
owners, mitigation due dates, rollback trigger, and the date or event that
requires re-review. If the result is blocked or incomplete, the next action is
not “approve with a caveat”; it is the smallest action that can produce new,
reviewable evidence.

## Meeting record

Capture these fields in the product decision record:

| Field | Record |
| --- | --- |
| Decision scope | Assistant, candidate, users, workflow, traffic, autonomous actions |
| Requested stage | Documentation, shadow launch, or controlled launch |
| Decision | Advance, remain in shadow, remediate, or block |
| Evidence reference | Report path, JSON path, run ID, candidate ID/version |
| Blockers | Stable blocker IDs and owner for each |
| Mitigations | Action, owner, due date, and expected evidence |
| Rollback | Trigger, operator, and safe fallback |
| Re-review | Date, event, or evidence change that reopens the decision |

## Common mistakes

- Treating a passing report as organizational approval.
- Treating a high evidence-completeness score as behavioral quality.
- Evaluating common happy paths while omitting risky boundaries and tail cases.
- Approving a broader scope than the selected cases and controls support.
- Allowing a stronger model, a vendor badge, or an undocumented manual check to
  substitute for evidence.
- Keeping a blocked decision open without an owner, mitigation, or re-review
  condition.

## Follow-up

If a production incident or review failure reveals a missing case, use the
incident-ingestion template to record the expected behavior, observed behavior,
impact, coverage gap, and proposed regression case. The next recipe in this
series will make that investigation-to-eval loop explicit.

