# Eval Case Intake From Production Incident

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
| Expected route | show / revise / escalate / block |
| Risk tier | low / medium / high / prohibited |
| Policy reference |  |
| Owner |  |

## Release Gate Impact

Should this case block release, trigger limited rollout, or be monitored?

## Follow-Up

| Action | Owner | Due date |
| --- | --- | --- |
| Add or update eval case |  |  |
| Update rubric or deterministic check |  |  |
| Update launch gate threshold |  |  |
| Review production traces for similar cases |  |  |
