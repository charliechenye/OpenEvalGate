# Approval and recovery worksheet

**Human design/review worksheet; not CLI input or executable policy.** All
IDs, limits, SLAs, and outcomes in the examples are synthetic teaching values.

## Separate case ownership from action authority

A human queue accepting a case does not authorize a tool action. A routine
recovery can resume inside **current autonomous authority** after checking
identity, context, eligibility, policy, and all execution blocks. It need not
obtain approval merely because it paused.

An action requiring approval must present a **valid current review** and pass
the same revalidation. Bind that review to `review_id`, workflow instance ID,
action digest over tool and exact parameters, checkpoint version, and policy
version. Verify reviewer authority, expiry, and whether the review is already
consumed or superseded. Atomically consume approval and claim the action,
then execute with a stable operation identity/idempotency key. Persist enough
information to recover across interruption; the V1 boolean
`idempotency_key_required` is not proof that external effects cannot duplicate.

Synthetic example: `review_demo_01` approves the exact USD 40 action in
`workflow_demo_01`, checkpoint 7, policy `synthetic_refund_recovery_v1`.
Changing any binding requires revalidation and, when approval still applies,
a new review ID. Approval cannot override a prohibition or active fraud block.

## Callback and recovery states

| Event | Required runtime behavior | Trace/state evidence required from external harness |
| --- | --- | --- |
| Valid current approval | Revalidate; atomically consume and claim once | Matching binding tuple, reviewer authority, expiry, one completed effect |
| Rejection | Close the rejected action without execution | Rejection record, zero writes, owned user follow-up |
| Edited parameters | Invalidate old approval and create a new review | Old/new action digests, new review ID/current checkpoint, zero writes before approval |
| Review expires | Keep action paused; notify and open owned fallback | Expiry event, preserved state, accepted fallback, zero writes |
| Late response | Audit and ignore for execution | Response received after expiry/supersession; no new authority |
| Duplicate callback | Audit; return recorded result without another effect | Consumed review, original operation identity, unchanged completed-action count |
| Wrong binding or reviewer | Reject callback for execution | Which binding/authority check failed, preserved block, review-owner follow-up |
| Tool result unknown | Reconcile original operation identity before any retry | Operation lookup, durable completed/absent/unknown result; no fresh identity to hide uncertainty |
| Autonomous recovery | Revalidate current autonomous eligibility; execute once | No approval prerequisite for this path; same stable operation identity |

If reconciliation proves the effect completed, record that result and avoid
re-execution. If it proves no effect, retry only under current authority and
the adapter's documented idempotency contract. If still unknown, keep the
action paused and route to an owned operations case. A timeout or an old
approval never creates automatic retry authority.

## Compose simultaneous triggers

Record all matched trigger IDs, the selected user-facing path, **all execution
blocks**, and every mandatory specialist route. A prohibition plus suspected
account takeover must both block the requested action and create the fraud
case. Selecting refusal cannot suppress the specialist alert; selecting
approval cannot clear a fraud block. Missing required checks or unresolved
precedence keeps execution paused and routes to the policy/operations owner.

V1 models one `expected_workflow_route` and one optional `expected_handoff` per
case. For refusal plus specialist handling, preserve the mandatory route in
`expected_trajectory.required_events` and `expected_end_state.assertions`.
The harness must inspect every route and block; core validation of the
declaration is not runtime trigger arbitration.

## Rollback and evidence review

Roll back the configuration for new work while retaining in-flight review
IDs, checkpoint/policy/action bindings, operation identities, and completed
actions. Reconcile pending work against current authority; never replay a
completed effect or erase review history. Name the rollback and queue owners.

Run the [teaching scenarios](../examples/approval-recovery/README.md) with
isolated fixtures and versioned runtime, policy, and graders. Record rejected,
expired, late, duplicate, edited, conflicting-trigger, unknown-result, and
autonomous paths separately. Missing required slices or unknown required
outcomes block full review. Human reviewers confirm queue capacity, specialist
coverage, monitoring, stop conditions, rollback, and organizational sign-off.
The CLI checks V1 evidence and selected review policy; it does not implement
these authorization transitions or issue that sign-off.
