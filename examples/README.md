# Canonical Reference Scenarios

The canonical OpenEvalGate examples are synthetic, illustrative scenarios created to demonstrate the framework's inputs, validation, assessment, and reporting workflow.

Their data, metrics, model outputs, policies, and generated reports are illustrative. They are not external production deployments, evidence of independent adoption, case studies, or external validation of OpenEvalGate.

## Scenarios

- [Subscription Support Assistant](subscription_support_assistant/README.md) demonstrates a passing controlled-launch package for billing explanations, cancellation approval, account-security escalation, and authentication refusal.
- [Customer Support Assistant](customer_support_assistant/README.md) demonstrates escalation quality, action boundaries, fraud routing, dependency fallback, and a blocked recommendation despite high evidence completeness.
- [Presales Assistant](presales_assistant/README.md) demonstrates commercial authority boundaries, unsupported-commitment controls, pricing approval, and specialist escalation.
- [Education Assistant](education_assistant/README.md) demonstrates academic-integrity boundaries, learner-safety escalation, accessibility review, context transfer, and durable resume behavior.

Each scenario README links its principal inputs and canonical generated report and provides commands that run from the repository root.

The Subscription Support Assistant is the passing controlled-launch reference. The Customer Support Assistant is the blocked controlled-launch reference. Presales and Education show documentation and shadow-launch packages with deliberate evidence gaps.

Each result-bearing scenario includes a `run_manifest.yaml` that binds the illustrative `eval_results.csv` to a declared run, candidate, evaluator identity, and (where available) digested historical and current evidence.
