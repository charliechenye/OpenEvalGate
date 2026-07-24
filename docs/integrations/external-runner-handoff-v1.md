# External Runner Handoff v1

OpenEvalGate does not execute an evaluation framework or import its SDK. An
external runner produces local V1 evidence; OpenEvalGate validates and assesses
that evidence after the run.

## Handoff steps

1. Run the candidate with your framework or internal harness.
2. Write V1 `eval_results.csv`; every populated row includes
   `schema_version,1` and only documented columns or `x_` extension columns.
3. Write `run_manifest.yaml` with `schema_version: "1"`, a completed run,
   candidate identity, and a relative result path. Record the runner in
   `producer.id` and `producer.version`; record the framework in
   `evaluation.framework.id` and `evaluation.framework.version` when present.
4. Compute SHA-256 digests over the exact evidence bytes and record them in
   the manifest or artifact index.
5. Run `openevalgate check .` and then `openevalgate report . --format json`.

The IDs and versions are provenance claims, not an adapter contract or an
endorsement by the framework vendor.

## LangChain-shaped producer example

This example is a file contract only. It does not install or import LangChain.

```yaml
schema_version: "1"
run:
  id: langchain-20260723-001
  status: complete
candidate:
  id: support-assistant
  version: 2026.07.23
producer:
  id: internal-langchain-eval-exporter
  version: 1.4.0
evaluation:
  kind: automated
  evaluator:
    id: support-quality-review
  framework:
    id: langchain
    version: 0.3.0
outputs:
  results:
    path: eval_results.csv
```

```csv
schema_version,run_id,case_id,candidate,evaluator,actual_route,expected_route,route_match,passed,score,failure_category,failure_reason,observed_output_path,reviewed_by,reviewed_at,notes
1,langchain-20260723-001,refund_boundary_case_001,support-assistant,support-quality-review,escalate,escalate,true,true,1,,,,qa,2026-07-23T12:00:00Z,exported by external runner
```

The exporter must populate the rest of the required rows and reference only
validated project-local paths. Framework-specific traces belong in an `x_`
CSV column or YAML `extensions` object and cannot alter V1 authorization.
