# Presales Assistant

> **Synthetic and illustrative example:** This repository-authored scenario is not an external production deployment. Its data, metrics, model outputs, and policies are illustrative. It is not evidence of independent adoption or external validation of OpenEvalGate.

This scenario demonstrates boundaries for discounts, roadmap statements, and legal or security commitments, together with account-owner follow-up, pricing approval, and specialist review paths.

## Inputs and Report

- [Evaluation cases](eval_cases.yaml)
- [Evaluation results](eval_results.csv)
- [Run manifest](run_manifest.yaml)
- [Current review context](review_context.yaml)
- [Historical and current eval inputs](inputs/eval_cases.yaml)
- [Review policy](review_policy.yaml)
- [Generated launch report](generated_launch_report.md)

## Reproduce from the Repository Root

```bash
openevalgate validate examples/presales_assistant/eval_cases.yaml
openevalgate check examples/presales_assistant/
openevalgate report examples/presales_assistant/ \
  --output examples/presales_assistant/generated_launch_report.md
```
