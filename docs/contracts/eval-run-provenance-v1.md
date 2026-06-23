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
- `artifact_index.yaml` for per-case output identity;
- evaluator categories and minimum evidence;
- resource descriptors and SHA-256 representation;
- lifecycle, validity, freshness, recency, and assurance dimensions;
- bounded compatibility for projects without provenance;
- controlled-launch provenance requirements;
- conformance fixtures for future implementations.

Version 1 does not implement parsing, enforcement, signatures, remote attestation, candidate registries, vendor adapters, or report provenance.

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

An optional `extensions` object is reserved for namespaced additions.

### Run

`run` contains:

- `id`
- `status`: `complete`, `failed`, or `aborted`
- `started_at`
- `completed_at` for terminal runs

Launch evidence must come from a complete run whose completion timestamp is not earlier than its start timestamp.

### Candidate

`candidate` contains a stable `id`, immutable `version`, and optional candidate-manifest descriptor.

The candidate is the evaluated release unit, not merely a base-model alias. It may include model, prompt, tools, routing configuration, code, and runtime settings.

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

A deterministic evaluator declares implementation ID, version, and any configuration digest that affects results.

A model judge declares judge identity/version, rubric or prompt digest, material configuration, and deterministic parsing or aggregation policy where applicable.

A hybrid evaluator declares component evaluators and a pinned aggregation or decision policy. `hybrid` without component and policy identity is incomplete.

## Resource descriptors

Policy-relevant inputs and outputs use one descriptor shape:

```yaml
role: review_policy
path: review_policy.yaml
media_type: application/yaml
schema_version: "1"
digest:
  sha256: 9d9b2f2f9bcb8f44f9ad2de631f21d9075a40f4b7c4e6aefdf3cb60507d4f243
```

Required fields:

- `role`
- exactly one of `path` or `uri`
- `digest.sha256`

Optional fields include `name`, `media_type`, `schema_version`, and `annotations`. Unrecognized annotations are informational and must not authorize launch.

Applicable input roles include eval cases, review policy, routing policy, escalation contract, action-risk matrix, candidate manifest, evaluation policy, evaluator rubric, deterministic evaluator configuration, model policy, candidate-registry entry, dataset, and fixture.

Only artifacts capable of changing evaluation behavior or interpretation need to be pinned.

Outputs identify run-scoped results and, when output artifacts are referenced, the artifact index.

## Digest and path rules

SHA-256 values:

- are calculated over raw file bytes;
- use lowercase 64-character hexadecimal;
- are not calculated after newline, Unicode, YAML, JSON, or CSV normalization;
- change whenever file bytes change.

Version 1 does not define an implicit recursive directory hash. Directory contents are represented by an explicit artifact index.

Local paths must be relative, resolve within the allowed evidence root, and reference existing regular files when verified. Absolute paths, path escapes, and unconstrained symlinks are invalid.

## Artifact index

The normative schema is `schemas/eval-run-artifact-index-v1.schema.json`.

Each entry binds an output artifact to:

- `artifact_type`
- `run_id`
- `case_id`
- optional `trial_id`
- `candidate_id`
- `candidate_version`
- `evaluator_id`
- resource path and digest

The entry must agree with the manifest and referenced result row. Human-readable artifacts may repeat these fields, but prose is not the authoritative identity source.

## Required consistency checks

A verifier checks at least:

1. run-directory identity versus manifest `run.id`;
2. manifest run identity versus every result row;
3. candidate ID/version across manifest, results, and artifact index;
4. evaluator identity across manifest, results, and artifact index;
5. case/trial identity across results and artifact index;
6. output containment, existence, type, and digest;
7. required input existence and digest;
8. manifest-pinned result and artifact-index digests.

A mismatch is invalid provenance, not legacy provenance.

## Independent classification dimensions

Provenance is not one overloaded status.

### Manifest presence

- `present`
- `legacy_absent`

### Validity

- `valid`
- `invalid`

### Content freshness

- `current`: required pinned artifacts and candidate identity match
- `stale`: required content or candidate identity drifted
- `unknown`: freshness cannot be established

### Recency

- `acceptable`
- `expired`
- `not_configured`

Old evidence is not automatically stale. Staleness is content drift; expiration is age-policy failure.

### Assurance

- `declared`: self-declared and structurally valid
- `verified`: local files, identities, and digests checked
- `attested`: reserved for future signed attestations

### Lifecycle

- `complete`
- `failed`
- `aborted`

Only a complete run may support launch authorization.

## Authorization semantics

Controlled-launch evidence requires:

- manifest `present`;
- validity `valid`;
- lifecycle `complete`;
- assurance at least `verified`;
- freshness `current`;
- recency `acceptable` or `not_configured`;
- candidate identity matching the release target;
- all required policy inputs pinned;
- required result and artifact digests matching;
- no contradictory provenance.

Scores, pass rates, documentation scores, or gate completion cannot override failed provenance requirements.

Legacy evidence may support documentation review and bounded shadow analysis with an explicit warning, but it cannot authorize controlled launch.

A present-but-invalid manifest must not degrade into legacy mode.

## Legacy compatibility

Projects without `run_manifest.yaml` remain readable during the `0.x` compatibility window:

- presence: `legacy_absent`
- freshness: `unknown`
- assurance: at most `declared`
- documentation review: allowed
- shadow review: allowed with warning
- controlled launch: denied

This compatibility does not apply to malformed or contradictory manifests.

## Threat model and non-claims

This contract can detect policy drift, candidate mismatch, modified or swapped artifacts, run/case/trial identity conflicts, missing evaluator configuration, incomplete lifecycle, and evidence that no longer applies to a release target.

It does not prove evaluator honesty, human participation, candidate-output authenticity, producer-host integrity, or that a digest record was not fabricated before recording.

Version 1 is a locally verifiable evidence contract, not a cryptographically trusted attestation.

## Versioning and extensions

`schema_version` is a major-version string.

Version 1 consumers must reject unsupported major versions. Backward-compatible additions may be accepted. Unknown extensions may be ignored only when doing so cannot increase authorization. Extensions must not weaken required fields or overwrite standard semantics.

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

Fixtures under `spec/fixtures/provenance/v1/` are normative examples for future parsers and policy tests. Initial cases cover valid current human-reviewed evidence, stale policy input, invalid run identity, and legacy evidence without a manifest.

## Implementation sequence

1. Parse manifests and artifact indexes.
2. Classify presence, validity, lifecycle, freshness, recency, and assurance.
3. Introduce run-scoped immutable result files.
4. Verify digests and cross-artifact identity.
5. Surface classifications in reports.
6. Connect verified current provenance to controlled-launch authorization.

Each implementation step must preserve fail-closed behavior.
