# SOP Compiler Guide

Do not make the LLM read your whole SOP. Compile the deterministic policy and context needed for the case before the model sees it.

## Why compilation matters

Long SOPs create ambiguity, token cost, stale context, and inconsistent policy selection. Production assistants need the smallest sufficient policy context for the user request.

## Compiler inputs

- User intent.
- User/account attributes.
- Product or workflow state.
- Region, language, plan, or entitlement.
- Current policy version.
- Known exclusions and escalation triggers.

## Compiler output

The model should receive concise, versioned context: applicable policy, allowed actions, blocked actions, escalation triggers, and response constraints.

## Launch gate

The SOP/policy compilation gate should prove that policy context is selected deterministically and that missing or conflicting context routes to revision, escalation, or block.
