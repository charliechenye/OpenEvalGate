# Manifesto

Most GenAI demos answer one narrow question: can the model do this once?

Production launch review has to answer a harder question: can this system do this reliably, safely, cost-effectively, and observably across real users?

OpenEvalGate exists for the second question.

Production GenAI is ultimately a trust-preservation problem. The goal is not maximum automation. The goal is trustworthy automation.

## Launch gates, not vibe checks

A launch gate is a concrete condition that must be true before a GenAI assistant or agent is exposed to users. It has evidence, an owner, and a mitigation path. It is not a subjective demo review.

Good teams can still use LangSmith, Braintrust, Phoenix, Langfuse, Promptfoo, DeepEval, Guardrails AI, and internal platforms. OpenEvalGate does not replace them. It defines what those systems should prove.

## Practical beliefs

- The golden eval set is the behavioral PRD for a GenAI system.
- Agent behavior is a business contract, not an engineering guess.
- Average performance is not launch readiness.
- Tail failures define trust.
- Containment is not resolution.
- Human escalation is not failure; it is a control surface.
- The best model in production is not always the biggest model.
- Public benchmarks do not tell you if a model is right for your product.
- Use LLMs for reasoning; use deterministic systems for enforcement.
- Do not make the LLM read your whole SOP; compile deterministic policy/context before the model sees it.
- Purpose-built AI assistants need input filters and output critics.
- The main LLM proposes; the output critic decides whether to show, revise, escalate, or block.

## The operating model

Launch readiness is not a single score from an eval run. It is a cross-functional decision across scope, model behavior, grounding, safety, action risk, observability, escalation, cost, rollback, and ownership.

OpenEvalGate gives teams a lightweight way to make that decision explicit.
