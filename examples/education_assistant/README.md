# Education Assistant

> **Synthetic and illustrative example:** This repository-authored scenario is not an external production deployment. Its data, metrics, model outputs, and policies are illustrative. It is not evidence of independent adoption or external validation of OpenEvalGate.

This scenario demonstrates academic-integrity and learner-safety boundaries, instructor and accessibility review paths, handoff context, fallback behavior, and durable workflow resume.

## Inputs and Report

- [Evaluation cases](eval_cases.yaml)
- [Evaluation results](eval_results.csv)
- [Run manifest](run_manifest.yaml)
- [Review policy](review_policy.yaml)
- [Generated launch report](generated_launch_report.md)

## Reproduce from the Repository Root

```bash
openevalgate validate examples/education_assistant/eval_cases.yaml
openevalgate check examples/education_assistant/
openevalgate report examples/education_assistant/ \
  --output examples/education_assistant/generated_launch_report.md
```
