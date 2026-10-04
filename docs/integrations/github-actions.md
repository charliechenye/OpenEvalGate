# GitHub Actions evidence review and decision summary

Run OpenEvalGate after your evaluator writes a V1 review package. In a
consumer repository, install it from its own pinned checkout; `pip install .`
otherwise installs the consumer project. For Promptfoo use the
[tutorial](promptfoo.md) and [workflow](../../examples/integrations/promptfoo/review.yml).
For another V1 producer, use this pattern:

```yaml
name: OpenEvalGate review

on: [pull_request, workflow_dispatch]

permissions:
  contents: read

jobs:
  release-assurance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - name: Require a reviewed full commit SHA
        shell: bash
        env:
          OPEN_EVAL_GATE_COMMIT: ${{ vars.OPEN_EVAL_GATE_COMMIT }}
        run: '[[ "$OPEN_EVAL_GATE_COMMIT" =~ ^[0-9a-f]{40}$ ]]'
      - uses: actions/checkout@v7
        with:
          repository: charliechenye/OpenEvalGate
          ref: ${{ vars.OPEN_EVAL_GATE_COMMIT }}
          path: .openevalgate
      - uses: actions/setup-python@v6
        with:
          python-version: "3.12"
      - run: python -m pip install ./.openevalgate
      # Execute your evaluator/producer here. Fail on errors, and write review/.
      - name: Validate and save the decision
        shell: bash
        run: bash .openevalgate/scripts/review_evidence_ci.sh review artifacts
      - name: Save evidence and diagnostics
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: release-review
          path: |
            artifacts/
            review/
```

Set `OPEN_EVAL_GATE_COMMIT` to a published revision containing the helper.
While this change is unpublished, test locally. The helper saves validation
JSON, report JSON, a card, stderr logs, and statuses, and appends the decision
to `GITHUB_STEP_SUMMARY`.

If upstream commands capture failures or use `continue-on-error`, pass their
actual eval/conversion exit codes as the helper's third/fourth arguments. It
fails and skips review on an upstream failure. `always()` on artifact upload
does not make the failed review pass.

For a direct report pipeline, specify Bash and preserve its status:

```bash
set -o pipefail
openevalgate report review --format card --fail-on-blocked | tee decision-card.md
```

The default report can exit `0` for a blocked recommendation; use
`--fail-on-blocked` to fail CI. `check` separately rejects invalid evidence.

For automation that needs individual fields, use the [CLI output contract](../contracts/cli-output-v1.md)
and `--format json` rather than parsing Markdown. V1 freshness/expiry
authorization is incomplete; see [checks and limits](promptfoo.md#what-does-openevalgate-check-and-what-must-the-team-verify).
