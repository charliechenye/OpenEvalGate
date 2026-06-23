# Eval-Run Provenance Contract v1

Status: proposed contract for OpenEvalGate `0.2.0`

## Purpose

OpenEvalGate evaluates externally produced evidence for AI-assistant and agent launch decisions. Metrics are not decision-ready unless reviewers can determine which candidate, policies, evaluator, inputs, and outputs produced them—and whether those artifacts still match the release under review.

This contract defines a vendor-neutral, run-scoped evidence envelope that makes evaluation evidence attributable, immutable, internally consistent, and classifiable for later launch authorization.

> Evaluation evidence is decision-relevant only when it can be traced to the exact candidate and policy inputs that produced it, and when those inputs and outputs have not drifted since the run.

The contract does not make OpenEvalGate an eval runner, hosted governance platform, runtime guardrail, or certification authority.

## Scope

Version 1 defines:

- an immutable run directory;
- `run_manifest.yaml` for run-level identity and pinned inputs;
- a run-scoped `eval_results.csv` identity contract;
- `artifact_index.yaml` for per-case output identity;
- evaluator categories and minimum evidence;
- resource descriptors and SHA-256 representation;
- lifecycle, validity, freshness, recency, and assurance dimensions;
- verifier-supplied release context;
- bounded compatibility for projects without provenance;
- controlled-launch provenance requirements;
- executable conformance fixtures.

Version 1 does not implement runtime enforcement, signatures, remote attestation, candidate registries, vendor adapters, or OpenEvalGate report provenance.

## Run-scoped evidence envelope

Each run has its own authoritative result file:

```text
eval_runs/
  run_002/
    run_manifest.yaml
    eval_results.csv
    artifact_index.yaml
    artifacts/
      case_001.md
```

A project-level aggregate `eval_results.csv` may remain as a legacy input or derived view, but it is not the immutable provenance subject for a versioned run.

Directory names are not authoritative. Run, case, trial, candidate, producer, and evaluator identity must be declared in machine-readable fields and cross-checked.

## Run manifest

The normative schema is `schemas/eval-run-manifest-v1.schema.json`.

Required top-level fields:

- `schema_version`
- `run`
- `candidate`
- `producer`
- `evaluation`
- `inputs`
- `outputs`

An optional `extensions` object is reserved for namespaced additions. Because version 1 schemas are strict, backward-compatible v1 extensions must live under `extensions`.

### Run

`run` contains:

- `id`
- `status`: `complete`, `failed`, or `aborted`
- `started_at`
- `completed_at`

Timestamps are timezone-aware RFC 3339 strings. A completion timestamp must not be earlier than its start timestamp. Only a complete run may support launch authorization.

### Candidate

`candidate` contains a stable `id`, immutable `version`, and optional candidate-manifest descriptor.

The candidate is the evaluated release unit, not merely a base-model alias. It may include model, prompt, tools, routing configuration, code, and runtime settings.

For controlled launch, the release target must be independently supplied through review context and must match the run candidate. A future OpenEvalGate candidate registry or project-level candidate manifest may provide that context; the run manifest itself is not sufficient to prove that it matches the release target.

### Producer

`producer` identifies the process that created the envelope through an `id` and `version`.

The producer is distinct from the eval framework and from OpenEvalGate. Validation must not imply that OpenEvalGate executed or witnessed the run.

### Evaluation and evaluator kinds

`evaluation.kind` is one of:

- `human`
- `deterministic`
- `model_judge`
- `hybrid`

A human evaluator declares a stable role or pseudonymous ID and a pinned rubric or review policy.

A deterministic evaluator declares implementation ID, version, and a configuration digest when configuration affects results.

A model judge declares judge identity/version, rubric or prompt digest, material configuration, and deterministic parsing or aggregation policy where applicable.

A hybrid evaluator declares component evaluators and a pinned aggregation or decision policy. Each component inherits the minimum requirements of its own evaluator kind. `hybrid` without complete component and policy identity is invalid.

## Run-scoped result-row identity

The normalized row schema is `schemas/eval-run-result-row-v1.schema.json`.

A version 1 run-scoped `eval_results.csv` must include these non-empty columns:

- `run_id`
- `case_id`
- `trial_id`
- `candidate_id`
- `candidate_version`
- `evaluator_id`

It may include:

- `primary_output_artifact_id`

Other behavioral columns remain governed by the existing eval-result contract.

Legacy columns such as `candidate`, `evaluator`, and `observed_output_path` do not satisfy version 1 provenance identity by themselves. Implementations may display or migrate them, but must not infer immutable candidate version or evaluator identity from free-text aliases.

A result row is uniquely identified for provenance purposes by:

```text
(run_id, case_id, trial_id, candidate_id, candidate_version, evaluator_id)
```

Duplicate provenance result identities are invalid.

`primary_output_artifact_id`, when supplied, must resolve to exactly one artifact-index entry. Additional artifacts may share the same result identity and are discovered through the artifact index.

## Resource descriptors

Policy-relevant inputs and outputs use one descriptor shape:

```yaml
role: review_policy
path: review_policy.yaml
media_type: application/yaml
schema_version: "1"
digest:
  sha256: "9d9b2f2f9bcb8f44f9ad2de631f21d9075a40f4b7c4e6aefdf3cb60507d4f243"
```

Required fields:

- `role`
- at least one of `path` or `uri`
- `digest.sha256`

A descriptor may include both `path` and `uri`: `uri` identifies the logical or external resource, while `path` identifies locally available verification bytes.

Optional fields include `name`, `media_type`, `schema_version`, and `annotations`. Unrecognized annotations are informational and must not authorize launch.

### Required input-role matrix

| Input role | Requirement |
| --- | --- |
| `eval_cases` | Always required. |
| `evaluation_policy` or evaluator rubric | Always required. |
| `candidate_manifest` | Required for controlled-launch eligibility. |
| `review_policy` | Required when review policy selects or interprets evidence. |
| `routing_policy` | Required when routing, workflow, destination, or model-assignment claims are evaluated. |
| `escalation_contract` | Required when escalation, handoff, fallback, or resume claims are evaluated. |
| `action_risk_matrix` | Required when tool or action authorization is evaluated. |
| Dataset, fixture, model policy, evaluator configuration | Required when it can materially change evaluation behavior or interpretation. |

Implementations must not require unrelated project files.

### Required outputs

`outputs` identifies:

- `results`: the run-scoped `eval_results.csv`;
- `artifact_index`: required when any result or evaluation claim references output artifacts.

Additional outputs may be declared with resource descriptors.

## Digest and path rules

SHA-256 values:

- are calculated over raw file bytes;
- use quoted lowercase 64-character hexadecimal strings in YAML;
- are not calculated after newline, Unicode, YAML, JSON, or CSV normalization;
- change whenever file bytes change.

Version 1 does not define an implicit recursive directory hash. Directory contents are represented by an explicit artifact index.

Local paths must be relative to the file containing the descriptor, resolve within the verifier's allowed evidence root, and reference existing regular files when verified. Absolute paths, path escapes after resolution, and unconstrained symlinks are invalid.

A URI is declarative unless an explicit resolver supplies bytes. Network retrieval is disabled by default. URI-only evidence cannot reach `verified` assurance unless a trusted resolver supplies bytes matching the recorded digest.

## Artifact index

The normative schema is `schemas/eval-run-artifact-index-v1.schema.json`.

Each entry binds an output artifact to:

- unique `artifact_id`
- `artifact_type`
- `run_id`
- `case_id`
- optional `trial_id`
- `candidate_id`
- `candidate_version`
- `evaluator_id`
- resource path and digest

The entry must agree with the manifest and referenced result row. Human-readable artifacts may repeat these fields, but prose is not the authoritative identity source.

Within one artifact index:

- `artifact_id` values must be unique;
- normalized artifact paths must be unique;
- duplicate compound identities with the same `artifact_type` are invalid;
- a result-row `primary_output_artifact_id` must resolve exactly once.

## Two verification comparisons

Version 1 distinguishes internal envelope integrity from release-time freshness.

### Envelope verification

Envelope verification checks that historical run evidence is internally coherent:

1. run-directory identity versus manifest `run.id`;
2. manifest run identity versus every result row;
3. candidate identity across manifest, results, and artifact index;
4. evaluator identity across manifest, results, and artifact index;
5. case/trial identity across results and artifact index;
6. run output containment, existence, type, and digest;
7. preserved run-input existence and digest;
8. manifest-pinned result and artifact-index digests;
9. uniqueness rules.

Failure of these checks makes provenance `invalid`.

### Release-context comparison

A verifier must separately receive review context containing:

- release-target candidate ID and version;
- current policy/input descriptors by role;
- optional evidence-age policy.

Freshness compares the valid historical envelope against this current context. A digest or candidate difference discovered only in this comparison makes evidence `stale`, not internally invalid.

The transport for review context is outside the run-envelope schema. Conformance fixtures use `review_context.yaml`. Future OpenEvalGate integration may derive it from project metadata, a candidate registry, or explicit command inputs.

## Independent classification dimensions

Provenance is not one overloaded status.

### Manifest presence

- `present`
- `legacy_absent`

### Validity

- `valid`
- `invalid`
- `not_evaluated`

### Content freshness

- `current`: a valid envelope matches release-target candidate and applicable current inputs
- `stale`: a valid envelope differs from release-target candidate or applicable current inputs
- `unknown`: freshness cannot be established

### Recency

- `acceptable`
- `expired`
- `not_configured`
- `unknown`

Old evidence is not automatically stale. Staleness is content drift; expiration is age-policy failure.

### Assurance

- `declared`: supplied but not independently checked
- `verified`: required local identities, paths, and digests were checked
- `attested`: reserved for future signed attestations
- `unknown`

`verified` describes the performed verification level. A verifier may classify valid historical evidence as verified and stale when release-context comparison detects drift.

### Lifecycle

- `complete`
- `failed`
- `aborted`
- `unknown`

Only a complete run may support launch authorization.

## Authorization outcomes

The contract uses these outcomes:

- `allowed`
- `allowed_with_warning`
- `blocked`
- `eligible`

`eligible` means provenance prerequisites pass; it does not itself authorize deployment. Other OpenEvalGate blockers and organizational approvals still apply.

Controlled-launch provenance is `eligible` only when:

- manifest presence is `present`;
- validity is `valid`;
- lifecycle is `complete`;
- assurance is at least `verified`;
- freshness is `current`;
- recency is `acceptable` or `not_configured`;
- candidate identity matches the release target;
- all conditionally required inputs are pinned;
- required result and artifact digests match;
- no contradictory provenance exists.

Scores, pass rates, documentation scores, or gate completion cannot override failed provenance requirements.

Legacy evidence may support documentation review and bounded shadow analysis with an explicit warning, but it cannot make controlled-launch provenance eligible.

A present-but-invalid manifest must not degrade into legacy mode.

## Legacy compatibility

Projects without `run_manifest.yaml` remain readable during the `0.x` compatibility window:

- presence: `legacy_absent`
- validity: `not_evaluated`
- freshness: `unknown`
- recency: `unknown` or `not_configured`
- assurance: `declared`
- lifecycle: `unknown`
- documentation review: `allowed`
- shadow review: `allowed_with_warning`
- controlled-launch provenance: `blocked`

This compatibility does not apply to malformed or contradictory manifests.

## Threat model and non-claims

This contract can detect policy drift, candidate mismatch, modified or swapped artifacts, run/case/trial identity conflicts, missing evaluator configuration, incomplete lifecycle, and evidence that no longer applies to a release target.

It does not prove evaluator honesty, human participation, candidate-output authenticity, producer-host integrity, or that a digest record was not fabricated before recording.

Version 1 is a locally verifiable evidence contract, not a cryptographically trusted attestation.

## Versioning and extensions

`schema_version` is a major-version string.

Version 1 consumers must reject unsupported major versions. Strict schemas reject unknown standard fields. Backward-compatible v1 additions must be namespaced under `extensions`. Unknown extensions may be ignored only when doing so cannot increase authorization. Extensions must not weaken required fields or overwrite standard semantics.

## Review provenance is separate

Eval-run provenance records what produced evaluation evidence.

A future review-provenance contract should record which OpenEvalGate version, review policy, command, and report inputs produced a release assessment. The OpenEvalGate version is intentionally not part of `run_manifest.yaml` unless OpenEvalGate itself acted as the external run producer.

## Relationship to external standards

| OpenEvalGate concept | Related external concept |
| --- | --- |
| Eval run | W3C PROV Activity; OpenLineage Run |
| Input or output artifact | W3C PROV Entity; in-toto ResourceDescriptor |
| Producer or evaluator | W3C PROV Agent |
| Run details and pinned inputs | SLSA run details and resolved dependencies |
| Output digests | in-toto statement subjects and resource digests |
| Complete, failed, aborted | OpenLineage run lifecycle |

OpenEvalGate adopts useful concepts but does not claim conformance, certification, or equivalent security guarantees.

References:

- https://slsa.dev/spec/v1.2/build-provenance
- https://in-toto.io/Statement/v1
- https://www.w3.org/TR/prov-o/
- https://openlineage.io/docs/spec/run-cycle/

## Conformance fixtures

Self-contained fixture directories under `spec/fixtures/provenance/v1/` include real input, result, artifact, review-context, and expected-classification files. Recorded SHA-256 values are computed from fixture bytes.

The fixture package covers valid human, deterministic, model-judge, and hybrid evaluation; stale policy input; candidate drift; output corruption; invalid identity; unsafe paths; failed lifecycle; expired evidence; unsupported schema version; duplicate artifact identity; and legacy evidence.

## Implementation sequence

1. Parse manifests, run-scoped result rows, artifact indexes, and review context.
2. Validate schema, identity, uniqueness, containment, lifecycle, and envelope digests.
3. Classify presence, validity, freshness, recency, and assurance.
4. Surface classifications in reports.
5. Connect provenance eligibility to controlled-launch authorization.

Each implementation step must preserve fail-closed behavior.
