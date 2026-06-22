# Research Context and Adjacent Tools

OpenEvalGate is not an eval runner, observability platform, or runtime guardrails system. It is a local release-assurance framework that helps teams define and assess evidence for a bounded review stage.

This document provides conceptual context from external guidance and adjacent tooling. It does not establish certification, formal standards alignment, endorsement, partnership, official integration, or external validation of OpenEvalGate.

## Relevant External Guidance

Production AI release review can involve more than average model performance. Relevant evidence may span governance, risk management, evaluation, human oversight, security, monitoring, escalation, and business ownership.

The following sources discuss related concerns:

- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework) emphasizes governance, mapping, measurement, and management of AI risk.
- [NIST AI RMF Generative AI Profile](https://www.nist.gov/itl/ai-risk-management-framework/ai-rmf-generative-ai-profile) adapts AI risk management to generative AI systems.
- [ISO/IEC 42001](https://www.iso.org/standard/81230.html) defines an AI management system standard for organizational governance.
- [OECD AI Principles](https://oecd.ai/en/ai-principles) emphasize trustworthy, human-centered, robust, and accountable AI.
- [OWASP Top 10 for LLM Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/) documents application risks such as prompt injection, sensitive information disclosure, and excessive agency.
- [EU AI Act overview](https://artificialintelligenceact.eu/) highlights risk management, human oversight, monitoring, and accountability requirements for regulated AI systems.
- [OpenAI Evals](https://github.com/openai/evals) shows the importance of structured evaluation harnesses for model behavior testing.

OpenEvalGate uses practical artifacts that address some of these concerns: golden eval sets, action risk matrices, output critic rubrics, automation boundaries, human escalation design, trust-preservation review, and release-assurance reports. This conceptual relationship is not a claim of conformance or formal alignment.

## Conceptual Relationships

| OpenEvalGate concept | Related guidance or tooling | Practical implication |
| --- | --- | --- |
| Trust preservation | [OECD AI Principles](https://oecd.ai/en/ai-principles), [NIST AI RMF](https://www.nist.gov/itl/ai-risk-management-framework) | Launch review should ask whether automation preserves user confidence and accountable operation. |
| Launch gates | [NIST AI RMF](https://www.nist.gov/itl/ai-risk-management-framework), [ISO/IEC 42001](https://www.iso.org/standard/81230.html) | Teams can use explicit governance checkpoints, owners, evidence, and mitigations. |
| Golden eval set | [OpenAI Evals](https://github.com/openai/evals), [Promptfoo](https://github.com/promptfoo/promptfoo), [DeepEval](https://github.com/confident-ai/deepeval) | Product-specific behavior should be represented as test cases, not only prose requirements. |
| Tail-risk / P0 review | [NIST AI RMF Generative AI Profile](https://www.nist.gov/itl/ai-risk-management-framework/ai-rmf-generative-ai-profile), [OWASP LLM Top 10](https://owasp.org/www-project-top-10-for-large-language-model-applications/) | Rare but high-impact failures require explicit tests, blocks, escalation, and rollback. |
| Automation boundary | [OWASP LLM Top 10](https://owasp.org/www-project-top-10-for-large-language-model-applications/), [EU AI Act overview](https://artificialintelligenceact.eu/) | High-impact actions need deterministic controls, human approval, or blocking. |
| Human escalation | [OECD AI Principles](https://oecd.ai/en/ai-principles), [EU AI Act overview](https://artificialintelligenceact.eu/) | Human intervention is a control surface, not a failure of automation. |
| Domain-owner feedback | [ISO/IEC 42001](https://www.iso.org/standard/81230.html), [NIST AI RMF](https://www.nist.gov/itl/ai-risk-management-framework) | Business, operations, policy, and trust owners should participate in ongoing review and change control. |
| Observability and monitoring | [NIST AI RMF](https://www.nist.gov/itl/ai-risk-management-framework), [Langfuse](https://github.com/langfuse/langfuse), [Arize Phoenix](https://github.com/Arize-ai/phoenix) | Release review can include evidence that production behavior will be inspectable and open to improvement. |

## Adjacent and Complementary Projects

These projects are relevant to overlapping parts of the workflow. The descriptions below identify complementary roles; they do not imply endorsement, partnership, or official integration.

| Category | Projects | What they do | How OpenEvalGate differs |
| --- | --- | --- | --- |
| Eval runners / test frameworks | [Promptfoo](https://github.com/promptfoo/promptfoo), [DeepEval](https://github.com/confident-ai/deepeval), [OpenAI Evals](https://github.com/openai/evals), [Ragas](https://docs.ragas.io/) | Execute, grade, or structure LLM and RAG evaluations. | OpenEvalGate can consume recorded eval outputs and organize them with business behavior contracts, gates, blockers, and reports. |
| Observability / LLMOps platforms | [LangSmith](https://docs.smith.langchain.com/), [Braintrust](https://www.braintrust.dev/docs), [Arize Phoenix](https://github.com/Arize-ai/phoenix), [Langfuse](https://github.com/langfuse/langfuse), [Helicone](https://github.com/Helicone/helicone) | Trace, observe, evaluate, experiment, monitor, and debug LLM applications. | Their outputs can be represented in `eval_results.csv` and release-review artifacts; no official integration is implied. |
| Guardrails / runtime validation | [Guardrails AI](https://github.com/guardrails-ai/guardrails) | Validate or constrain LLM outputs and runtime behavior. | OpenEvalGate records when runtime controls, output critics, action gates, or human approvals are declared as release evidence. |
| Agent skill / MCP security scanning | [SkillGate](https://github.com/charliechenye/SkillGate) | Performs static trust checks for AI-agent skills, Codex and Claude skills, MCP configs, risky capabilities, policy enforcement, baseline drift, and SARIF output. | SkillGate can provide security-review evidence; OpenEvalGate can include that evidence in a broader assistant or agent release review. |
| Agent governance / runtime control | [Microsoft Agent Governance Toolkit](https://github.com/microsoft/agent-governance-toolkit), [EGAProtocol](https://github.com/egaprotocol/egaprotocol) | Provide agent governance, runtime controls, or protocol-level accountability patterns. | OpenEvalGate focuses on local cross-functional review artifacts, eval coverage, business ownership, blockers, and reports. |
| Broader AI governance frameworks | [NIST AI RMF](https://www.nist.gov/itl/ai-risk-management-framework), [ISO/IEC 42001](https://www.iso.org/standard/81230.html), [OECD AI Principles](https://oecd.ai/en/ai-principles), enterprise risk frameworks | Define broad AI governance, management, and accountability expectations. | OpenEvalGate provides templates and a local CLI for a narrower release-assurance workflow. |

## Where OpenEvalGate Fits

OpenEvalGate can be used as a review layer around evidence produced by eval, observability, and runtime-control tools.

```text
Business intent / policy / trust risk
        ↓
OpenEvalGate release-review artifacts
        ↓
Eval runners, tracing tools, observability, guardrails, internal harnesses
        ↓
eval_results.csv, traces, incidents, model arena data
        ↓
OpenEvalGate release-assurance report
```

The core role of OpenEvalGate is to make launch evidence explicit:

- What behavior is expected?
- What behavior is unacceptable?
- What are the worst plausible failures?
- Which actions require deterministic enforcement?
- Where must humans approve, review, or intervene?
- Which metrics provide evidence of durable resolution and preserved trust?
- What hard blockers prevent launch regardless of score?

## How To Use OpenEvalGate Alongside Existing Tools

Use OpenEvalGate to define a release-review contract and your existing tools to generate evidence.

Examples:

- Use Promptfoo, DeepEval, OpenAI Evals, or Ragas to execute golden eval cases.
- Use LangSmith, Braintrust, Phoenix, Langfuse, or Helicone to inspect traces, experiments, and production behavior.
- Use Guardrails AI or internal policy services for runtime validation and enforcement.
- Use SkillGate to scan third-party agent skills and MCP configurations before installing or approving them.
- Use OpenEvalGate to collect the evidence, identify blockers, and generate the bounded release-assurance report.

The intended workflow is:

```text
Define launch gates in OpenEvalGate
  -> run evals and collect traces in your tool stack
  -> feed results back into OpenEvalGate
  -> review hard blockers, mitigations, and bounded recommendation
```

This keeps OpenEvalGate lightweight while making it useful to product, engineering, platform, trust/safety, legal, compliance, and business owners.
