# Review Promptfoo results before an AI agent release

OpenEvalGate reviews evidence after Promptfoo has run your agent. Its experimental
repository producer accepts **Promptfoo 0.123.1** JSON exports, selects one
prompt/provider pair, and writes existing V1 evidence. It adds rollback,
monitoring, escalation, and evidence-sufficiency review to a release discussion.
Promptfoo already provides eval assertions and CI quality gates; keep using those.

Install from the [same source checkout](../installation.md) as these scripts.
The producer uses OpenEvalGate's existing Python dependencies. It neither
imports Promptfoo nor calls a model API. Node/Promptfoo are needed only to
generate new upstream results.

## How do I review Promptfoo results in GitHub Actions?

**Run your eval, export one declared candidate, then run `check` and
`report --fail-on-blocked`. Preserve diagnostics and propagate every failure.**

1. Create `review/` with your team's cases, controls, policy, and current review
   context. Start with `openevalgate init review --profile minimal`; its
   placeholders are intentionally incomplete. Fill them using the
   [practitioner guide](../00_getting_started_for_practitioners.md).
2. Add explicit case/trial/candidate metadata to Promptfoo tests and make
   your harness emit the structured observations below.
3. Copy [review.yml](../../examples/integrations/promptfoo/review.yml) to
   `.github/workflows/release-review.yml` in **your** repository. Edit the
   identities, provider, prompt index, paths, and application-install command.
   It assumes a Node project with a committed lockfile and `npm ci`.
4. Set repository variable `OPEN_EVAL_GATE_COMMIT` to a reviewed full SHA
   containing the producer/helper. The workflow separately checks out and
   installs `.openevalgate`. `pip install .` would install your project instead.
   Older releases lack these scripts; until this change is published, test locally.

The essential local conversion is:

```bash
python scripts/export_promptfoo_v1.py \
  --input artifacts/promptfoo.json --project review \
  --run-id promptfoo_ci \
  --candidate-id support-agent --candidate-version release-candidate-1 \
  --evaluator-id route-contract --evaluator-version 1 \
  --evaluation-kind deterministic \
  --reviewed-by 'ci:route-review' --reviewed-at '2026-10-04T04:00:00Z' \
  --provider-id your-provider-id --prompt-index 0
bash scripts/review_evidence_ci.sh review artifacts 0 0
```

Replace example identities/time with actual values. `reviewed_by` names the
declared process; an automated CI identity does not claim human approval.
Use `--evaluation-kind model_judge` when the evaluator actually uses model
judging. Mixed/human/hybrid exports are outside this example's supported contract.

Successful conversion prints `Exported N rows ...`. The helper saves
`check.json`, `report.json`, `decision-card.md`, stderr logs, and
`review-status.txt`. The workflow additionally saves upstream JSON/log,
conversion log, and review evidence, including on failure. These may contain
your outputs; use your repository's access/retention policy.

| Stage | Failure behavior |
| --- | --- |
| Upstream evaluation exits nonzero | Job fails; raw output/log are retained. The helper skips review even if conversion succeeded. |
| Conversion rejects an export | Exits `1`; no complete evidence package is published. Job fails and retains the rejection log. |
| `check` rejects project evidence | Job fails; report and validation diagnostics are still attempted and saved. |
| Report is `blocked` | `--fail-on-blocked` exits `1`; JSON/card are retained. |
| `tee` or summary writing fails | Job fails; successful `tee` cannot hide a failed report. |

The Bash helper captures `PIPESTATUS` immediately after its card pipeline.
Its optional third/fourth arguments are actual upstream eval/conversion exit
codes. Pass zeros only when those commands have already succeeded. See the
[generic Actions guide](github-actions.md) for other V1 producers.

## Map cases and observations explicitly

Each exported `testCase.metadata.openevalgate` must contain:

```yaml
metadata:
  openevalgate:
    case_id: invoice_explanation_001
    trial_id: trial_001
    candidate_id: support-agent
    candidate_version: release-candidate-1
```

Use your project's `eval_cases.yaml` IDs. Candidate/version must equal the
explicit flags; run/candidate must match any `review_policy.yaml` selection.
Use an immutable commit or build ID for the actual tested candidate version,
and declare the same identity in your current review context. The workflow's
`release-candidate-1` is a placeholder, not a version to reuse across changes.
Repeated trials need distinct IDs. Test positions and display labels are not
substitutes for explicit identity.

Each selected `response.output` must be a **JSON string** holding an object:

```json
{"route":"escalate","actual_workflow_route":"approval","actual_destination":"billing_approval_queue","trajectory_pass":true,"end_state_pass":true,"prohibited_action_occurred":false,"payload_complete":true,"fallback_success":true,"resume_success":true,"late_escalation":false}
```

Instrument actual routing/tool/handoff behavior in your harness. Asking the
candidate to describe its route does not independently verify that route.
The example provider returns predetermined synthetic observations only to
demonstrate the handoff.

`route` is required: `show`, `revise`, `escalate`, or `block`. The authoritative
**expected** route comes from the matching project case. The producer derives
`route_match` and workflow/destination matches when both expected and observed
values are present. It never invents missing observations or turns an overall
assertion pass into a trajectory/handoff pass.

| Optional type | Supported observation fields |
| --- | --- |
| Boolean | `trajectory_pass`, `end_state_pass`, `prohibited_action_occurred`, `payload_complete`, `fallback_success`, `resume_success`, `late_escalation` |
| String | `actual_workflow_route`, `actual_destination`, `actual_workflow_id`, `actual_model_id`, `routing_policy_version`, `routing_reason` |

Other raw fields are retained but do not become policy inputs. Absent optional
fields stay blank; V1 review policy determines evidence sufficiency.
Identity fields and nonempty optional string columns use trimmed, single-line
values. Structured JSON output itself may be formatted over multiple lines.

Supported export: `metadata.promptfooVersion: "0.123.1"`, `EvaluateSummaryV3`
under `results`, per-row `success`, `failureReason`, numeric `[0,1]` score,
matching `gradingResult.pass`, and structured output. Selection uses row
`provider.id` and `promptIdx`; selected rows must have one coherent `promptId`.
Export counts must agree with all rows.

Execution errors, missing observations/identity, duplicate case/trial mappings,
conflicting identities/grades, malformed JSON (including duplicate keys), and
unsupported versions/formats fail conversion. A completed **failed assertion**
is exported as `passed=false` with its actual reason. It is not dropped;
conversion can succeed for failed behavioral evidence.

Use a fresh workspace with no existing root results, manifest, artifact index,
or selected run directory. The producer refuses overwrites, validates before
publication, and publishes the authoritative manifest last. Prepare a new
workspace for another run rather than deleting an existing review's evidence.

```text
review/eval_results.csv
review/run_manifest.yaml
review/artifact_index.yaml
review/eval_runs/<run-id>/promptfoo-export.json
review/eval_runs/<run-id>/inputs/eval_cases.yaml
review/eval_runs/<run-id>/observations/<sha256-of-case-and-trial>.json
```

SHA-256 digests bind exact source JSON, cases, CSV, index, and observations.
Identical inputs/flags yield identical package bytes. The manifest uses the
upstream summary timestamp as its completion marker; it does not independently
measure execution time. `complete` means a coherent completed run envelope,
not complete case coverage or release authorization. The producer does not
update team-owned controls, approval, or `review_context.yaml`.

## Why can passing evals still block a release review?

**Assertions do not establish rollback, monitoring, or human-path readiness.**
This offline demo imports the same passing export into two new synthetic
workspaces and fails rollback/observability gate rows in the second one:

```bash
python scripts/run_promptfoo_demo.py --output /tmp/oeg-promptfoo-pass
python scripts/run_promptfoo_demo.py --output /tmp/oeg-promptfoo-blocked --blocked-controls
```

Use new directories (PowerShell may use `$env:TEMP`). No Node, model API, or
network access is needed after OpenEvalGate installation.

| Controls | Decision card | Exit |
| --- | --- | --- |
| Complete synthetic package | `Ready for bounded controlled launch` | `0` |
| Rollback and monitoring gates fail | `Not ready for controlled launch`; `missing_rollback`, `missing_monitoring` | `1` |

Supply and review actual rollback/observability evidence, then rerun the review.
Re-running passing evals cannot repair missing controls. The two eval CSVs are
byte-identical. All data is synthetic, not independent production/adoption evidence.

[Fixture provenance](../../examples/integrations/promptfoo/fixtures/provenance.json)
records actual `0.123.1` generation and hashes; the
[example README](../../examples/integrations/promptfoo/README.md) explains regeneration.

## What does OpenEvalGate check and what must the team verify?

**It validates submitted evidence and computes a bounded recommendation;
the team verifies reality, freshness, and release authority.**

```bash
openevalgate check review --format json
openevalgate report review --format card --fail-on-blocked
openevalgate report review --format json --fail-on-blocked
```

V1 checks include case/result consistency, local run/candidate/evaluator identity,
duplicate mappings, local digests, selected coverage/trial depth, configured
thresholds, critical behavioral invariants, and required control evidence.
See [V1 handoff](external-runner-handoff-v1.md), [review modes](../review-modes.md),
[gate rules](../launch-gates-and-evidence-scoring.md), and
[provenance contract](../contracts/eval-run-provenance-v1.md).

**Current V1 limit:** `stale` freshness and `expired` recency diagnostics do
not yet consistently prevent a passing recommendation. Full provenance
authorization is deferred. Verify current candidate/config/data digests,
evidence age, rollback effectiveness, monitoring, escalation operations,
owners, and actual release authority. Local digest verification proves byte
integrity, not independent truth. A reported route is not a verified tool trace;
a decision card is not organizational signoff.

## Sources and version boundary

- [Promptfoo 0.123.1 release](https://github.com/promptfoo/promptfoo/releases/tag/0.123.1)
  fixes the experimental export boundary; newer versions require separate validation.
- [Promptfoo CI/CD docs](https://www.promptfoo.dev/docs/integrations/ci-cd/)
  describe upstream eval and quality-gate execution.
- [Google AI search guidance](https://developers.google.com/search/docs/appearance/ai-features)
  uses existing SEO foundations and does not require a special AI file. This
  tutorial provides direct answers, commands, and bounded claims. Rankings and
  AI citations remain observation outcomes.
