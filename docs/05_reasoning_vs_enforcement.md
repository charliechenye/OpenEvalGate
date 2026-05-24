# Reasoning Vs Deterministic Enforcement

Use LLMs for reasoning. Use deterministic systems for enforcement.

An LLM can interpret user intent, draft a response, summarize context, and propose next steps. It should not be the only mechanism deciding whether a high-risk action is allowed.

## Good LLM work

- Explain policy in user-friendly language.
- Identify ambiguity.
- Propose a response.
- Suggest escalation.
- Summarize evidence for a reviewer.

## Good deterministic work

- Check entitlement.
- Enforce refund limits.
- Block prohibited actions.
- Verify account ownership.
- Apply region-specific policy gates.
- Record audit events.

## Launch implication

If a tool action can create financial, legal, account, privacy, safety, or compliance harm, the launch gate should require deterministic enforcement before the model can trigger or recommend that action.
