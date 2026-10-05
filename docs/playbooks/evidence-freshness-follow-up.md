# Follow-up: stale and expired evidence can still receive a passing recommendation

This is an investigation and follow-up record, not executable policy or a
change to core authorization semantics. The synthetic reproduction below was
checked during the playbook V1 alignment work. Its dates and 30-day recency
limit are teaching fixtures, not product defaults.

## Observed behavior

On temporary copies of the maintained subscription-support project, the
official report path produced:

| Current review context | Historical validity / assurance | Freshness / recency | Report status | Maximum stage / recommendation |
| --- | --- | --- | --- | --- |
| Matches manifest; within fixture age limit | valid / verified | current / acceptable | pass | Controlled launch / Ready for bounded controlled launch |
| Current candidate version differs | valid / verified | stale / acceptable | pass | Controlled launch / Ready for bounded controlled launch |
| Matches manifest; older than fixture age limit | valid / verified | current / expired | pass | Controlled launch / Ready for bounded controlled launch |

The core displays freshness/recency findings but still recommends controlled
launch in these examples. Historical integrity is not the same as suitability
for the current release. External release reviewers must reject stale or
expired evidence for that scope; neither report advice nor process exit is
organizational authorization. No core code, policy default, or gate semantics
were changed in this playbook work.

## Minimal reproduction

From the repository root with the local package installed, run this read-only
diagnostic. It writes only temporary copies, preserves historical digests, and
does not modify canonical reports or project inputs:

```bash
python - <<'PY'
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
import shutil
import yaml
from openevalgate.output import report_output

source = Path("examples/subscription_support_assistant")
manifest = yaml.safe_load((source / "run_manifest.yaml").read_text())
with TemporaryDirectory() as directory:
    for scenario in ("current", "stale", "expired"):
        project = Path(directory) / scenario
        shutil.copytree(source, project)
        context = {
            "schema_version": "1",
            "candidate": deepcopy(manifest["candidate"]),
            "inputs": deepcopy(manifest["inputs"]),
            "observed_at": "2026-06-19T00:00:00Z",
            "recency_policy": {"max_age_days": 30, "max_future_clock_skew_seconds": 300},
        }
        if scenario == "stale":
            context["candidate"]["version"] += "-changed"
        if scenario == "expired":
            context["observed_at"] = "2026-10-04T00:00:00Z"
        (project / "review_context.yaml").write_text(yaml.safe_dump(context, sort_keys=False))
        report = report_output(project)
        print(scenario, report["run_identity"]["classification"],
              report["status"], report["assessment"]["maximum_permitted_stage"],
              report["assessment"]["recommendation"])
PY
```

The current control distinguishes a freshness/authorization gap from malformed
or altered historical evidence. A separate stale-input reproduction should
also compare different, correctly digested current and historical case/policy
snapshots; corrupting a historical digest tests integrity instead.

## Expected blocking rule for the follow-up

When provenance/freshness or recency is evaluated, selected evidence classified
`stale` or `expired` must not support a passing controlled-launch recommendation.
Keep valid historical evidence available for audit, but block current launch
assessment until matching, sufficiently recent evidence is supplied. Scores
and passing behavior must not override that authorization limitation.

Define the exact assessment stage and finding/blocker mapping before changing
implementation. Review `unknown`, absent review context, lifecycle status,
missing timestamps, future skew, and selected versus unselected runs separately
so the fix has a bounded compatibility contract. The present reproduction
does not establish their desired policy.

## Compatibility impact to review

- The fix can preserve V1 input schemas and existing CLI/JSON field names while
  intentionally changing recommendation, report `status`, maximum-stage, and
  blocker values for affected evidence. Specify any blocker-ID change explicitly.
- Artifact validation and historical integrity need not fail merely because
  current authorization fails; `check` already describes artifact validation.
- Preserve default report exit behavior. An assessment newly classified as
  blocked should cause the existing `report --fail-on-blocked` path to return
  its existing blocked exit code, affecting consumers that currently accept it.
- Identify affected canonical fixtures and report bytes, regenerate only after
  an intentional semantic change, and add current/stale/expired regression
  contrasts through the official inspection and report paths.

Start from the [provenance contract](../contracts/eval-run-provenance-v1.md),
[review modes](../review-modes.md), and relevant
[code-map rows](../architecture/code-map.md). This remains a separate core task.
