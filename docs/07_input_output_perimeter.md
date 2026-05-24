# Input And Output Perimeter

A production assistant needs a perimeter around generation.

The input filter decides whether a request should enter the assistant workflow. The output critic decides whether a proposed response can be shown.

## Input filter

The input filter should identify unsupported scope, prohibited requests, prompt injection attempts, missing required context, regulated workflows, and requests that require a human.

Possible routes: accept, refuse, escalate, block.

## Output critic

The output critic reviews the proposed response for grounding, policy alignment, helpfulness, action safety, and escalation judgment.

Possible routes: show, revise, escalate, block.

## Response admission gate

The response admission gate is the final decision before the user sees text or an action is taken. The main LLM proposes. The critic decides.
