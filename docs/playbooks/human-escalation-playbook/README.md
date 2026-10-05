# Human Escalation Playbook

Companion to [Human Escalation Playbook](https://chenyezhu.com/playbooks/human-escalation-playbook/).
This repository maintains the article's templates and examples. Start with a
workflow where wrong autonomy or failed handoff has material consequences.

Human escalation combines authority boundaries, owned destinations, minimum
sufficient context, SLAs, durable state, and actual runtime checks. OpenEvalGate
validates local **evidence** after an external harness runs the system. It does
not operate queues, authorize tool actions, or implement approval transitions.
Every filled policy, threshold, limit, SLA, cadence, date, count, and outcome
here is a **synthetic teaching example**, not a product default or production
measurement.

## Choose the right file

| Classification | Maintained entry | What it can do |
| --- | --- | --- |
| CLI input templates, incomplete until filled | [Escalation contract](../../../templates/escalation_contract.yaml), [Golden cases](../../../templates/golden_eval_case.yaml), [fill-in requirements](../../../templates/README.md) | Copy into a project; fill identities, rules, owners, positive SLA/cadence, resume controls, and actual case references. |
| Complete V1 input examples, directly validatable | [Refund contract](examples/customer-support-refund/escalation-contract.yaml), [education contract](examples/education-integrity/escalation-contract.yaml), [presales contract](examples/presales-commercial/escalation-contract.yaml) | Standalone structure checks; without project cases, case references and runtime behavior are not checked. |
| Complete linked teaching inputs | [Approval/recovery pack](examples/approval-recovery/README.md) | Validate V1 cases and contract together; ten expected-behavior scenarios, with no run results. |
| Human design/review worksheets, not CLI input | [Worksheet catalog](templates/README.md); [refund payload](examples/customer-support-refund/handoff-payload.yaml), [refund gate](examples/customer-support-refund/escalation-release-gate.yaml), domain queue worksheets | Design payloads, queues, callbacks, recovery, gates, and operational review; the CLI does not read them. |
| Complete synthetic evidence project | [Subscription support assistant](../../../examples/subscription_support_assistant/) | Run `validate`, `check`, and `report --format card` on maintained manifest-bound evidence. |

There is one generic contract template at the root; the duplicate playbook
copy was removed. Neither blank input template is promised to pass without
completion. The [formal V1 schema](../../../schemas/escalation-contract-v1.schema.json)
and [actual validator](../../../openevalgate/escalation.py) govern structure.
`schema_version` must be exactly the quoted string `"1"`.

## Article steps to evidence and checks

Commands below are CLI subcommands; runnable commands follow the table.
Replace project placeholders for your own package.

| Article step | Repository file | Who executes the check | CLI command / report output |
| --- | --- | --- | --- |
| 1–2. Select workflow and map boundaries | [Contract template](../../../templates/escalation_contract.yaml); project `automation_boundary_matrix.md` and `human_escalation_design.md` | PM/domain owner defines authority; runtime evaluates context and risk | `check <project>` validates required artifacts and optional contract declarations. |
| 3–5. Declare triggers, destinations, payload, queues, fallback | [Queue worksheet](templates/queue-routing-worksheet.md), [handoff worksheet](templates/handoff-payload-schema.yaml), project `escalation_contract.yaml` | Core checks IDs, enums, SLA/fallback/owner declarations and linked references; runtime checks triggers, queue acceptance, actual payload | `check <project>`; `report` shows contract coverage and submitted handoff metrics. |
| 6. Define pause, callbacks, resume, rollback | [Approval/recovery worksheet](templates/approval-and-recovery.md), [durable-state checklist](templates/fallback-and-durable-state-checklist.md) | Runtime implements authorization, atomic claims, state, reconciliation; human reviews traces | Core checks durable-state declarations and requires checkpoint/idempotency flags on approval paths; it does not execute the state machine. |
| 7. Run escalation/recovery tests | [Recovery cases](examples/approval-recovery/eval_cases.yaml); [result CSV](../../../examples/subscription_support_assistant/eval_results.csv); [manifest](../../../examples/subscription_support_assistant/run_manifest.yaml) | External harness executes isolated trials and trace/state graders; core checks submitted evidence | `validate` checks cases; `check` checks run/result binding; `report` summarizes route, destination, context, fallback, resume. |
| 8. Review required slices and control gates | [Gate worksheet](templates/escalation-release-gate.yaml); [review policy](../../../examples/subscription_support_assistant/review_policy.yaml); [launch-gate review](../../../examples/subscription_support_assistant/launch_gate_review.md) | Core evaluates supported policy/hard controls; harness/humans check additional rules | `report <project> --format card`; advice, blockers, maximum stage, next actions. |
| 8–9. Decide rollout, learn, recertify | [Decision record](../golden-eval-set-playbook/templates/decision_record_template.yaml), [incident intake](templates/incident-ingestion-template.md), [recertification](templates/recertification-checklist.md) | Named organizational owner, engineering, operations, policy/risk | Record organizational approval separately; reopen review after incidents and material changes. |

## Boundary and authorization rules

| Path | Authority and required behavior |
| --- | --- |
| Resolve / autonomous recovery | Current identity, context, policy, eligibility, and all risk checks permit the action inside autonomous scope; revalidate and execute once. |
| Clarify | A recoverable fact is missing; pause the action, cap attempts, detect repeated questions, and reevaluate triggers. |
| Escalate | Human judgment or specialist investigation owns resolution; accepted case ownership grants no tool-action authority. |
| Approval | An otherwise permitted, fully specified action needs bounded human authorization; preserve it and wait for a valid current review. |
| Refuse / block | Prevent prohibited execution while preserving any mandatory specialist route. |

Autonomous recovery and approval recovery have different authorization rules.
An ordinary permitted action does not need approval merely because it paused.
Approval must bind review ID, workflow instance, exact action digest,
checkpoint, policy, reviewer authority, and expiry. Atomically consume approval
and claim the action before one effect. Rejection, edits, expiry, lateness,
and duplicate callbacks need separate handling. Edited actions require a new
bound review; approval cannot override execution blocks.

Overlapping triggers must retain all execution blocks and required specialist
routes, even when the user-facing response is refusal. V1 has one workflow
route and one optional handoff; the [conflict teaching case](examples/approval-recovery/eval_cases.yaml)
keeps extra specialist obligations in formal trajectory/state assertions for
the external harness to check.

Unknown tool outcomes require reconciliation by the **original operation
identity** before considering retry. Completed effects must not replay;
still-unknown effects remain paused with an owned fallback. Rollback changes
new-work configuration while preserving in-flight approval bindings, operation
identities, and completed-action records. The [approval/recovery worksheet](templates/approval-and-recovery.md)
defines state rules, evidence, and rollback responsibilities.

## What the core checks and what remains external

`human_escalation_design.md` remains required human-readable evidence.
`escalation_contract.yaml` is optional, but `check` validates it when present:
workflow fields, boundary lists, trigger/destination IDs, payload-field lists,
positive SLA, fallback/owner declarations, durable-state flags/resume text,
and recertification declarations. With project `eval_cases.yaml`, it also
checks required case IDs and handoff trigger/destination/type references.

These checks do not interpret trigger/boundary prose, enforce timers, verify
actual reviewer authority or action digests, or prevent duplicate effects.
A declared `approval_timeout_minutes` is not a core timer. The
[refund design notes](examples/customer-support-refund/design-notes.md) retain
allowed/prohibited actions, the synthetic USD 25 limit, clarification budget,
and audit obligations outside ignored extensions. That standalone contract
uses a separate teaching fixture and is not a replacement for the maintained
complete project contract; match IDs and policies before adopting it.

`eval_cases.yaml` defines **expected behavior**, tools, routes, traces, final
states, and handoffs. The **external runner** executes and grades the system,
then supplies `eval_results.csv` with a valid `run_manifest.yaml` binding the
run, candidate, evaluator, and results. It must implement every assertion,
retain independent fixtures and trace/state evidence, report distinct cases
separately from trials, and fail required checks. A plausible final response
is not proof of a completed handoff.

`review_policy.yaml` supplies core mode, selected run/candidate, coverage,
trial depth, and supported pass/route thresholds. The core applies fixed
critical-case, prohibited-action, required-escalation, and supported high-risk
handoff failure rules. Optional submitted metrics do not prove real state
transitions; not every diagnostic has a configurable gate. The harness must
map failed required assertions to case failure. Unknown required judgments
stay incomplete and block full review; necessary slices omitted from declared
cases cannot be inferred by the core. See the [comparison protocol](../golden-eval-set-playbook/templates/comparison-and-grading.md)
for version, trial, and unknown-evidence rules.

`launch_gate_review.md` supplies control statuses and meaningful evidence for
hard-gate review. Design `escalation-release-gate.yaml` worksheets do not become
executable policies. Extra slice rules, baseline comparisons, callback
correctness, trigger composition, operations capacity, monitoring, stop
conditions, rollback, and organizational sign-off remain external/human work.
Report/card gives a recommendation; organizational authorization is recorded
separately. The current core can still recommend controlled launch for `stale`
or `expired` evidence; external review must block that use. The
[minimal reproduction and core follow-up](../evidence-freshness-follow-up.md)
records the expected rule and compatibility impact without changing core gates.

## Validate the examples

Run from the repository root in an environment with this checkout installed;
see [installation](../../../CONTRIBUTING.md#development-setup).
There is no escalation CLI subcommand. For the three standalone contracts,
use the **official Python validator**:

```bash
python - <<'PY'
from pathlib import Path
from openevalgate.escalation import validate_escalation_contract

root = Path("docs/playbooks/human-escalation-playbook/examples")
valid = True
for domain in ("customer-support-refund", "education-integrity", "presales-commercial"):
    result = validate_escalation_contract(root / domain / "escalation-contract.yaml")
    print(f"{domain}: valid={result.valid}; triggers={result.trigger_count}; destinations={result.destination_count}")
    for issue in result.issues:
        print(f"  {issue.path}: {issue.message}")
    valid = valid and result.valid
raise SystemExit(0 if valid else 1)
PY
```

This checks declarations only. The [recovery-pack commands](examples/approval-recovery/README.md)
validate its cases and contract together. In a full project, `check` validates
linked references when the optional contract is present.

Use the maintained complete project for a runnable review:

```bash
python -m openevalgate.cli validate examples/subscription_support_assistant/eval_cases.yaml
python -m openevalgate.cli check examples/subscription_support_assistant/
python -m openevalgate.cli report examples/subscription_support_assistant/ --format card
```

`check` confirms artifact validation, not launch readiness. Report/card shows
submitted escalation recall, over-escalation, destination, context, fallback,
resume, and lateness metrics when available, supported blockers, and a
recommended stage. A successful report process exit is not organizational
approval. See [review modes](../../review-modes.md).

The lightweight [playbook regression tests](../../../tests/test_playbook_examples.py)
call formal validators and V1 schemas. The documentation CI job runs them on
docs-only changes too, independently of the full pytest matrix.
