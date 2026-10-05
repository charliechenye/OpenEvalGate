# Eval Case Intake From Production Incident

**Human intake worksheet; the CLI does not read this file.**

Use this when a production issue, complaint, escalation, trace review, or human override should become a golden eval case.

## Incident Summary

What happened?

## User / Workflow Impact

Who was affected and how?

## Failure Type

- [ ] Wrong answer
- [ ] Ungrounded answer
- [ ] Wrong tool call
- [ ] Prohibited tool call
- [ ] Missing escalation
- [ ] Bad refusal
- [ ] Privacy / permission issue
- [ ] Policy misinterpretation
- [ ] Tool failure handling
- [ ] Trust-damaging overpromise
- [ ] Other

## Was This Represented In The Eval Set?

- [ ] Yes
- [ ] No
- [ ] Partially

## If It Was Represented, Why Did The Gate Miss It?

Describe whether the miss came from scoring, threshold, stale context, missing trace data, weak rubric, or unclear ownership.

## Investigation Classification

Select the primary follow-up category. Use a secondary category when the
incident crossed more than one control boundary.

- [ ] Evidence gap — the required evidence was missing, invalid, stale, or not selected.
- [ ] Policy gap — the business rule, risk boundary, or expected route was unclear or wrong.
- [ ] Behavior failure — the agent produced an unacceptable answer, action, or refusal.
- [ ] Routing or escalation failure — the agent chose the wrong route, destination, or handoff.
- [ ] Operational failure — a tool, dependency, fallback, resume, or rollback path failed.
- [ ] Monitoring gap — the failure was not observable or the alert/owner path was ineffective.

What evidence supports this classification?

## Should This Become A New Eval Case?

- [ ] Yes
- [ ] No

## Proposed Eval Case

| Field | Draft |
| --- | --- |
| Case ID |  |
| User input |  |
| User context |  |
| Retrieved context |  |
| Expected behavior |  |
| Unacceptable behavior |  |
| Expected tool behavior |  |
| Expected admission route | show / revise / escalate / block |
| Expected workflow route | answer / clarify / act / approval / escalate / refuse |
| Risk tier | low / medium / high / prohibited |
| Policy reference |  |
| Owner |  |

## Release Gate Impact

Should this case block release, trigger limited rollout, or be monitored?

Record the previous and new case/fixture/grader/policy versions, failing trace
and final state, required independent trials, and any missing required slice.
Write behavior into V1 fields and implement assertions in the external runner.
Keep acceptance of the repair separate from release authorization in a
[decision record](decision_record_template.yaml).

## Follow-Up Decision

- [ ] Re-evaluate the current candidate.
- [ ] Re-approve the release scope.
- [ ] Roll back or pause the release.
- [ ] Update documentation or ownership only.

What must be true before the follow-up is closed?

## Follow-Up

| Action | Owner | Due date |
| --- | --- | --- |
| Add or update eval case |  |  |
| Update rubric or deterministic check |  |  |
| Update launch gate threshold |  |  |
| Review production traces for similar cases |  |  |
