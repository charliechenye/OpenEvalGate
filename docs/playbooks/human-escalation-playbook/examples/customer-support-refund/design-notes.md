# Refund contract runtime obligations

This is a **design and review worksheet**; the CLI does not read it. The
contract, policies, USD 25 autonomy limit, two clarification attempts, SLAs,
60-minute approval timeout, and 90-day cadence are synthetic teaching values.

The V1 contract keeps allowed actions and the autonomy limit in `resolve_when`,
approval limits in `approval_required_when`, forbidden actions in
`refuse_or_block_when`, and the clarification budget and frustration override
in the clarify/escalate boundaries. These are declarations. The validator
checks their structure, not whether the runtime obeys each sentence.

The external runtime must permit `retrieve_order`, `check_refund_eligibility`,
and `create_support_followup` only inside current authority; reject
`issue_refund_without_policy_check`, `override_fraud_hold`, and
`close_case_without_resolution`; prevent repeated questions; and transfer to
an owned human path when clarification exhausts its budget or frustration
requires handoff. Resolve the precise write-action authority with the policy
owner before deployment: the illustrative limit alone is not a tool grant.

Preserve the original audit obligations in runtime traces:
`escalation_triggered`, `handoff_payload_created`, `destination_selected`,
`human_review_started`, `human_decision_recorded`, `workflow_resumed`, and
`workflow_closed`. The old top-level `audit` field was unsupported; none of
these obligations moved into ignored extensions.

Standalone validation checks the contract only. Its required case IDs refer
to the historical customer-support example vocabulary; it is not a drop-in
replacement for that project's maintained contract or the Golden refund
fixture. Validate every trigger, destination, and required case reference
against the actual project when adopting it. Use the maintained
[complete project](../../../../../examples/subscription_support_assistant/)
for an end-to-end review.
