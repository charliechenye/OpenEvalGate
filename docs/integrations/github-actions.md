# GitHub Actions Decision Summary

OpenEvalGate does not require a hosted service or a vendor-specific action.
Run the local CLI after your existing evaluator has written the project
evidence, then publish the deterministic decision card to the workflow summary.

```yaml
name: OpenEvalGate review

on:
  pull_request:
    paths:
      - "review/**"
      - "eval_results.csv"

permissions:
  contents: read

jobs:
  release-assurance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: python -m pip install .
      # Run the team's existing evaluator before this step.
      - name: Validate evidence
        run: openevalgate check review/
      - name: Publish decision card
        run: |
          openevalgate report review/ \
            --format card \
            --fail-on-blocked \
            | tee "$GITHUB_STEP_SUMMARY"
```

The example intentionally keeps evaluator execution outside OpenEvalGate. The
CLI consumes local artifacts, reports stable blocker identifiers, and exits
non-zero only when `--fail-on-blocked` is requested.

For automation that needs individual fields, use the [CLI output contract](../contracts/cli-output-v1.md)
and `--format json` rather than parsing Markdown.
