# Human Escalation template catalog

The only generic **V1 CLI input template** is
[templates/escalation_contract.yaml](../../../../templates/escalation_contract.yaml).
It replaces the duplicate `escalation-contract.yaml` formerly here and requires
completion; see the [fill-in requirements](../../../../templates/README.md).
Use the shared [Golden case template](../../../../templates/golden_eval_case.yaml)
for escalation evals rather than inventing a separate `eval_case` envelope.

All files in this directory are **human design and review worksheets**, even
when YAML names include `schema` or `release-gate`. OpenEvalGate does not read
them. All filled policies, limits, SLAs, cadences, thresholds, and results are
synthetic teaching examples that require a product-specific decision.

| Worksheet | Purpose |
| --- | --- |
| [Queue routing](queue-routing-worksheet.md) | Define owned destinations, capacity, fallback, and simultaneous-trigger handling. |
| [Handoff payload](handoff-payload-schema.yaml) | Design a minimum sufficient runtime payload; not an OpenEvalGate schema. |
| [Approval and recovery](approval-and-recovery.md) | Define current authority, review binding, callback states, operation reconciliation, and rollback. |
| [Fallback and durable state](fallback-and-durable-state-checklist.md) | Review runtime implementation and trace/state evidence. |
| [Release gate design](escalation-release-gate.yaml) | Design slice and operational rules; only supported rules map to `review_policy.yaml`. |
| [Incident intake](incident-ingestion-template.md) | Capture failures and convert them into V1 cases and runner assertions. |
| [Recertification](recertification-checklist.md) | Recheck policy, queues, runtime controls, and ownership. |

The website starter kit's approval example, recovery state rules, trigger
composition, handoff binding fields, and rollback/evidence requirements are
adapted here and in the [V1 teaching case pack](../examples/approval-recovery/README.md).
They describe obligations for an external implementation, not new core gates.
