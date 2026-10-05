# Golden Eval Set Playbook

Companion to [Golden Eval Set Playbook for PMs](https://chenyezhu.com/playbooks/golden-eval-set-playbook-for-pms/).
This repository maintains the article's templates and examples. Start with one
workflow and one review decision.

A golden set defines expected and prohibited behavior across prompt, retrieval,
tools, policy, workflow, handoff, and recovery. OpenEvalGate validates local
evidence after an **external runner** executes the system and grades it. The
deterministic core does not call an LLM or make an organizational release decision.

Every filled policy, threshold, frequency, date, trial count, and outcome here
is a **synthetic teaching example**, not a product default, production
measurement, or proof that a real deployment is safe.

## Choose the right file

| Classification | Maintained entry | What it can do |
| --- | --- | --- |
| CLI input template, incomplete until filled | [Golden case template](../../../templates/golden_eval_case.yaml), [fill-in requirements](../../../templates/README.md) | Copy to `eval_cases.yaml`; complete IDs, context, policy, owner/date, behavior, tools, routes, and implemented assertions. |
| Complete V1 input examples, directly validatable | [Refund](examples/refund_agent_eval_cases.yaml), [education](examples/education_assistant_eval_cases.yaml), [presales](examples/presales_assistant_eval_cases.yaml) | Validate expected-behavior documents; they supply no observed run results. |
| Human design/review worksheets, not CLI input | [Worksheet catalog](templates/README.md), [grading/gate design notes](examples/design-notes.md) | Design comparisons, graders, gates, incidents, and decisions; the CLI does not read these papers or their YAML. |
| Complete synthetic evidence project | [Subscription support assistant](../../../examples/subscription_support_assistant/) | Run `validate`, `check`, and `report --format card` on maintained manifest-bound evidence. |

Maintain the generic case template at the repository root. The
[formal V1 JSON schema](../../../schemas/eval-cases-v1.schema.json) and
[actual validator](../../../openevalgate/schema.py) govern CLI inputs.
The old duplicated YAML design schema's `schema_version: 0.1.0` described a
reference revision, not a CLI version; see the [schema entry](schemas/README.md).
Inputs require exactly `schema_version: "1"` and an `eval_cases` list.
No blank template is promised to pass out of the box.

## Article steps to evidence and checks

Commands below are CLI subcommands. The runnable commands follow the table;
replace project placeholders when applying it to your own package.

| Article step | Repository file | Who executes the check | CLI command / report output |
| --- | --- | --- | --- |
| 0. Align scope, policy, and owners | [Alignment brief](templates/stakeholder_alignment_brief.md); project behavior contract and action-risk matrix | PM, policy/domain owner, operations | `check <project>` checks required artifacts; humans resolve disputed authority and scope. |
| 1–3. Map slices, collect cases, write behavior | [Case template](../../../templates/golden_eval_case.yaml) → project `eval_cases.yaml`; [incident intake](templates/incident_ingestion_template.md) | PM/domain owner defines behavior; core checks V1 structure and case relationships | `validate <project>/eval_cases.yaml`; issues and case count. |
| 4. Freeze versions, run independent trials, grade | [Comparison worksheet](templates/comparison-and-grading.md); [result CSV](../../../examples/subscription_support_assistant/eval_results.csv); [manifest](../../../examples/subscription_support_assistant/run_manifest.yaml) | External harness executes trace/state checks; human adjudicates required qualitative judgments; core checks submitted identity/digests | `check <project>`; `report` shows evidence, selected coverage, depth, thresholds, and provenance. |
| 5. Apply supported policy and control gates | [Gate design](templates/release_gate_template.yaml); [review policy](../../../examples/subscription_support_assistant/review_policy.yaml); [launch-gate review](../../../examples/subscription_support_assistant/launch_gate_review.md) | Core applies supported policy and hard-control rules; harness/humans check additional slice rules | `report <project> --format card`; recommendation, blockers, maximum stage, next actions. |
| Decide the full rollout scope | [Decision record](templates/decision_record_template.yaml) | Named organizational owner with engineering, operations, policy/risk | Store scope, missing evidence, sign-off, stop conditions, and rollback separately; report/card is advice. |
| 6. Operate and learn | [Review agenda](templates/eval_review_agenda.md), [incident intake](templates/incident_ingestion_template.md), [change-review recipe](../../20_agent_change_review_recipe.md) | Operations/domain owner, external harness, PM | Re-run `validate`, `check`, and `report` on new bound evidence; retain earlier decisions. |

## Evidence responsibilities and capability limits

`eval_cases.yaml` defines **expected behavior**. Put `must_do` requirements in
`expected_behavior`, prohibitions in `unacceptable_behavior`, tools in
`expected_tool_behavior`, trace rules in `expected_trajectory`, and final-state
checks in `expected_end_state`. The external runner must implement the
assertions, retain trace/final-state evidence, and fail required checks; core
validation does not execute these declarations.

`expected_route` is response admission (`show`, `revise`, `escalate`, `block`).
`expected_workflow_route` is the product path (`answer`, `clarify`, `act`,
`approval`, `escalate`, `refuse`). Refusing a graded answer while offering safe
learning help can have admission `revise` and workflow `refuse`. A discount
negotiation goes to sales (`escalate`) until a permitted proposed action is
fully specified for approval. Use `expected_handoff` only on workflow
`approval` or `escalate`, with IDs matching the project contract. Only non-policy
metadata belongs in `extensions`.

The **external runner** produces `eval_results.csv`. A valid
`run_manifest.yaml` must bind its selected run, candidate, evaluator, and
results; an unbound CSV is not usable launch evidence. Record baseline and
candidate in separate bound runs; freeze case, fixture, grader, and policy
versions; reset fixtures before every independent trial; and use distinct
`trial_id` values. Report **distinct cases** separately from **total trials**.
The core checks identities and supported consistency/digests, not trial
isolation or grader quality. See the [V1 provenance contract](../../contracts/eval-run-provenance-v1.md)
and [comparison protocol](templates/comparison-and-grading.md).

`review_policy.yaml` is a **core policy input**: review mode, selected
run/candidate, case/critical coverage, minimum trials per case, and supported
`pass_rate`/`route_match_rate` thresholds. Controlled review also applies fixed
critical-case, prohibited-action, and required-escalation invariants. A
necessary business slice omitted from the declared case set cannot be
inferred by the core. Other qualitative/slice and baseline regression rules
remain external; diagnostic summaries do not automatically become policy.

`launch_gate_review.md` records required control-gate statuses and meaningful
evidence for hard-gate checks. It is not organizational sign-off. Design-only
`release_gate_template.yaml` and per-case string `release_gate` labels do not
install executable thresholds. Translate supported controls into
`review_policy.yaml`; retain other blocking rules in the external review.

Missing necessary slices, invalid traces, or unknown necessary judgments block
**complete release review**. CSV booleans accept `true`/`false`, not an invented
`unknown` value: preserve unknown/incomplete checks in external evidence and the
decision record; do not silently count or discard them as passes. A repair may
pass its executed tests while release review remains blocked. Preserve scope,
missing evidence, owners, stop conditions, and rollback in the
[decision worksheet](templates/decision_record_template.yaml). Humans also
confirm operational readiness, uncertainty, monitoring, and rollout approval.
The current core can still recommend controlled launch for evidence classified
`stale` or `expired`. External release review must block that use. See the
[minimal reproduction and separate core follow-up](../evidence-freshness-follow-up.md);
this playbook update does not change provenance authorization semantics.

## Example categories

| Example | What it demonstrates |
| --- | --- |
| [Refund cases](examples/refund_agent_eval_cases.yaml) | Eligibility, compensation pressure, missing context, policy bypass, and a synthetic USD 50 contrast family. |
| [Education cases](examples/education_assistant_eval_cases.yaml) | Integrity refusal, grounded help, conflicting material, learner support. |
| [Presales cases](examples/presales_assistant_eval_cases.yaml) | Roadmap commitments, sales negotiations, unsupported comparisons, specialist security review. |
| [Approval/recovery pack](../human-escalation-playbook/examples/approval-recovery/README.md) | Ten V1 callback, trigger-conflict, operation-reconciliation, and autonomous recovery cases. |

The Human Escalation refund contract uses a separate synthetic USD 25 limit.
These are separate fixtures; adapt and bind matching cases/contracts before
reviewing a real project. For contrast design, see the
[Synthetic Boundary Case Guide](../../17_synthetic_boundary_case_guide.md).

## Run the examples

From the repository root in an environment with this checkout installed,
following [installation](../../../CONTRIBUTING.md#development-setup):

```bash
python -m openevalgate.cli validate docs/playbooks/golden-eval-set-playbook/examples/refund_agent_eval_cases.yaml
python -m openevalgate.cli validate docs/playbooks/golden-eval-set-playbook/examples/education_assistant_eval_cases.yaml
python -m openevalgate.cli validate docs/playbooks/golden-eval-set-playbook/examples/presales_assistant_eval_cases.yaml
```

For a complete project, use the maintained entry:

```bash
python -m openevalgate.cli validate examples/subscription_support_assistant/eval_cases.yaml
python -m openevalgate.cli check examples/subscription_support_assistant/
python -m openevalgate.cli report examples/subscription_support_assistant/ --format card
```

`validate` checks cases; `check` checks artifacts and evidence consistency,
not a launch recommendation. The card separates evidence, behavior, controls,
provenance, blockers, and recommended stage. `report --format json` provides
the existing automation contract. A successful report process exit is not
organizational approval. See [review modes](../../review-modes.md).

The lightweight [regression check](../../../tests/test_playbook_examples.py)
uses formal validators and V1 schemas, protects metadata boundaries, and
checks the linked recovery contract. It runs in the documentation CI job even
when expensive pytest jobs are skipped.
