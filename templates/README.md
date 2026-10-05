# CLI input templates

Maintain one generic template for each CLI input in this directory. Playbooks
link here; filled domain examples remain in their own example directories.

| File | Classification | Required adaptation |
| --- | --- | --- |
| [golden_eval_case.yaml](golden_eval_case.yaml) | Incomplete V1 CLI input template | Fill stable unique IDs, prompt, context, policy, owner, quoted review date, required/prohibited behavior, tool boundaries, rubric, and both routes; supply trajectory and state assertions that your runner implements. |
| [escalation_contract.yaml](escalation_contract.yaml) | Incomplete V1 CLI input template | Fill workflow identity and policy, boundary rules, unique trigger/destination IDs, positive SLA and recertification cadence, destination owners/fallbacks, resume rules, and actual case IDs. |

Neither blank template is promised to validate out of the box. Copy the Golden
template to a project as `eval_cases.yaml` and the escalation template as
`escalation_contract.yaml`. Keep `schema_version: "1"` as a quoted string and
`eval_cases` as a list. Replace every empty string and zero; remove unused
optional objects or complete them. Review all illustrative enum selections
against your workflow rather than treating them as product defaults.

Use `openevalgate validate <project>/eval_cases.yaml` for cases. Project
`openevalgate check <project>` also checks an optional escalation contract and
its references to project cases. Standalone contract validation uses the
official Python validator, as shown in the
[Human Escalation playbook](../docs/playbooks/human-escalation-playbook/README.md).
Validation does not execute the assistant, interpret boundary prose as policy
code, run assertions, or authorize release.

The formal schemas are [eval cases V1](../schemas/eval-cases-v1.schema.json)
and [escalation contract V1](../schemas/escalation-contract-v1.schema.json),
with semantic validation in [schema.py](../openevalgate/schema.py) and
[escalation.py](../openevalgate/escalation.py). The
[Golden](../docs/playbooks/golden-eval-set-playbook/templates/README.md) and
[Human Escalation](../docs/playbooks/human-escalation-playbook/templates/README.md)
working papers are for design and review; the CLI does not read them.
