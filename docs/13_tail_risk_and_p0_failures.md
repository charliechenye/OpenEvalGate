# Tail Risk And P0 Failures

Average performance is not launch readiness. Tail failures define trust.

A GenAI agent can look great on average and still be unsafe to launch. Mean performance tells one story; tail risk tells the story that gets escalated. Rare does not mean acceptable.

For GenAI systems, this is reinforced by risk guidance such as the [NIST AI RMF Generative AI Profile](https://www.nist.gov/itl/ai-risk-management-framework/ai-rmf-generative-ai-profile) and application security risks captured in the [OWASP Top 10 for LLM Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/).

## What Launch Gates Must Evaluate

- Average-case evals.
- Boundary-case evals.
- Adversarial evals.
- High-impact action tests.
- Policy-violation tests.
- Escalation tests.
- Output critic checks.
- Human review paths.
- Hard blocks for prohibited actions.

## Common Tail Failures

- Promising something the business cannot honor.
- Issuing compensation outside policy.
- Calling an ineligible tool.
- Failing to escalate high-risk cases.
- Giving a confident answer from weak grounding.
- Creating a privacy or compliance violation.

## Controlled Failure

The goal is not perfection. The goal is controlled failure. A launch-ready assistant has clear blocks, escalation paths, deterministic enforcement, monitoring, and rollback for the failures that matter most.
