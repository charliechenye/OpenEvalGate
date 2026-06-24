# Eval-Run Provenance Contract v1

Status: proposed contract for a future OpenEvalGate release

## Purpose

OpenEvalGate evaluates externally produced evidence for AI-assistant and agent launch decisions. Metrics are not decision-ready unless reviewers can determine which candidate, policies, evaluator, inputs, and outputs produced them, whether the historical evidence is internally trustworthy, and whether it still matches the release under review.

This contract defines a vendor-neutral, run-scoped evidence envelope for existing OpenEvalGate-compatible eval results. The provenance manifest wraps an existing compatible `eval_results.csv`. It does not require external eval systems to adopt new provenance columns or rewrite every row.

PR 18 defines the contract, schemas, fixtures, and fixture-development validation only. It does not implement production provenance parsing, report rendering, CLI behavior, controlled-launch enforcement, blockers, recommendation logic, or authorization code.

## Scope

Version 1 defines:

- a run directory containing an existing compatible `eval_results.csv`;
- `run_manifest.yaml` for run-level identity, lifecycle, evaluator identity, and optional pinned evidence;
- optional `artifact_index.yaml` for machine-readable output artifact identity;
- optional `review_context.yaml` for current-release freshness and recency comparison;
- an `expected.yaml` fixture contract for normative examples;
- lifecycle, validity, freshness, recency, assurance, finding, and authorization vocabulary;
- bounded compatibility for projects without a manifest.

Version 1 does not define a new CSV row schema, remote attestation, vendor adapters, OpenEvalGate review provenance, runtime enforcement, or report output.

## Existing CSV Compatibility

The existing OpenEvalGate `eval_results.csv` contract remains authoritative. This contract does not require new CSV columns, including:

- `candidate_id`
- `candidate_version`
- `evaluator_id`
- `primary_output_artifact_id`

The compatibility cross-check uses existing fields:

- `run_id`
- `candidate`
- `evaluator`
- `case_id`
- `trial_id`
- `observed_output_path`

`trial_id` remains optional under the existing CSV contract.

## Run Manifest

The normative schema is `schemas/eval-run-manifest-v1.schema.json`.

The base manifest identifies one run, one candidate ID and version, and one top-level evaluation identity. Multi-candidate run manifests are deferred.

Manifest values are inherited by CSV rows and artifacts instead of being repeated as new CSV provenance columns:

- immutable candidate ID and version;
- producer identity, when supplied;
- evaluation framework identity, when supplied;
- evaluator identity and kind;
- lifecycle status;
- run timestamps, when supplied;
- input and output descriptors, when supplied.

Missing producer, framework, evaluation policy, timestamps, digests, inputs, candidate artifact, artifact index, or review context does not automatically make a manifest structurally invalid. Those fields affect assurance, freshness, recency, and controlled-launch eligibility.

## Descriptor Types

The schema separates file descriptors from named resource descriptors.

A `fileDescriptor` is used for fixed-purpose files such as `candidate.artifact`, `outputs.artifact_index`, evaluator configuration, `evaluation.policy`, and hybrid `evaluation.evaluator.decision_policy`. It requires at least one of `path` or `uri`, permits both, and does not require `role`. Its optional digest is SHA-256 over raw bytes.

A dedicated `resultsDescriptor` is used for `outputs.results`. It extends file-descriptor semantics but requires a local `path` in v1. A URI may be supplied in addition to the path, but URI-only results are schema-invalid because OpenEvalGate must parse and cross-check the CSV locally.

A `namedResourceDescriptor` is used only for `run_manifest.inputs[]` and `review_context.inputs[]`. It requires `role`, requires at least one of `path` or `uri`, and permits both. Known singleton roles may omit `name`; repeatable and custom roles require a non-empty `name`.

Known singleton input roles are:

- `eval_cases`
- `evaluation_policy`
- `review_policy`
- `routing_policy`
- `escalation_contract`
- `action_risk_matrix`

Roles are extensible. Custom roles are allowed, default to repeatable, and require `name`. Known singleton roles may appear at most once. Duplicate singleton roles are semantically invalid. Repeatable resources match between historical evidence and current review context by `(role, name)`.

URI-only descriptors are valid declared evidence except for `outputs.results`. Network retrieval is disabled by default. URI-only evidence cannot become locally verified unless an explicitly configured resolver supplies matching bytes. Resolver behavior is out of scope for PR 18.

## CSV Cross-Checks And Aliases

When a manifest is present, a verifier cross-checks existing CSV fields against manifest identity:

- trim leading and trailing whitespace from CSV values before comparison;
- compare aliases case-sensitively;
- do not case-fold or Unicode-normalize in v1;
- every non-empty CSV `run_id` must equal `run.id`;
- CSV `candidate` must equal `candidate.id` or one `candidate.accepted_aliases` value;
- CSV `evaluator` must equal `evaluation.evaluator.id` or one `evaluation.evaluator.accepted_aliases` value;
- mismatches are contradictory provenance and make the historical envelope invalid.

Aliases are compatibility labels, not stable identities. Stable IDs remain authoritative. Alias rules:

- aliases must not contain leading or trailing whitespace;
- aliases must contain at least one non-whitespace character;
- aliases must be unique after trimming;
- aliases equal to the stable ID are allowed but redundant.

## Evaluation Policy Fields

`evaluation.policy` and hybrid `evaluation.evaluator.decision_policy` are distinct.

`evaluation.policy` is an optional `fileDescriptor` identifying the policy, protocol, or procedure governing the historical evaluation run as a whole. Examples include a review procedure, scoring policy, test execution protocol, or evaluation governance policy.

Hybrid `evaluation.evaluator.decision_policy` is a required `fileDescriptor` for hybrid evaluators. It identifies the aggregation, arbitration, or adjudication rule that combines component evaluator results into a final result. Examples include deterministic checks overriding a model judge, human review resolving disagreement, weighted component aggregation, or unanimous-pass requirements.

They may coexist. They are not aliases and must not be collapsed into one field.

## Canonical Input Mirrors

Fixed-purpose descriptors may be mirrored into `inputs[]` so they participate in deterministic freshness comparison. Mirrors are optional for base schema validity, declared assurance, and verified historical assurance.

Canonical mirror mapping:

| Fixed-purpose descriptor | Canonical input mirror |
| --- | --- |
| `evaluation.policy` | `inputs[role=evaluation_policy]` |
| `evaluation.evaluator.configuration` | `inputs[role=evaluator_configuration, name=<top-level evaluator id>]` |
| `evaluation.evaluator.decision_policy` | `inputs[role=hybrid_decision_policy, name=<top-level evaluator id>]` |
| Hybrid component `configuration` | `inputs[role=evaluator_component_configuration, name=<component id>]` |

A fixed-purpose descriptor without a mirror can still be part of a valid and verified historical envelope when that descriptor is itself valid and digest-verified. It cannot participate in deterministic freshness comparison. When review context is present and a release-sensitive fixed-purpose descriptor lacks its canonical mirror, freshness is `unknown` and controlled launch is blocked.

Controlled-launch-eligible evidence must mirror every release-sensitive fixed-purpose descriptor into `inputs[]`.

When both forms are present, they must describe the same underlying resource:

- if either declaration has `path`, both must have paths resolving to the same normalized run-relative file;
- if either declaration has `uri`, both must have the same URI;
- if either declaration has `digest`, both must have the same digest;
- conflicting locators are invalid;
- declarations that cannot be proven equivalent are invalid;
- `extensions` cannot establish resource equivalence.

A contradictory mirror makes the historical envelope invalid with `provenance_duplicate_resource_mismatch`. This rule applies only to fixed-purpose descriptors and their canonical mirrors, not to unrelated resources that happen to reference the same file.

## Path Roots And Local Files

Local path resolution is normative:

| Reference | Resolution root |
| --- | --- |
| Manifest file descriptors | Directory containing `run_manifest.yaml` |
| Manifest `inputs[]` | Directory containing `run_manifest.yaml` |
| `outputs.results.path` | Directory containing `run_manifest.yaml` |
| `outputs.artifact_index.path` | Directory containing `run_manifest.yaml` |
| Artifact entry `path` | Directory containing `artifact_index.yaml` |
| Review-context candidate and input paths | Directory containing `review_context.yaml` |
| CSV `observed_output_path` | Directory containing the run-scoped CSV |

After resolution:

- run-envelope paths must remain within the run directory;
- review-context paths must remain within the review-context evidence root;
- absolute paths are invalid;
- normalized `..` escapes are invalid;
- symlinks are invalid;
- referenced local paths must exist;
- referenced local paths must be regular files.

Missing digest lowers assurance. Missing local file makes provenance invalid. For review-context descriptors, a missing local file makes the review context invalid and preserves historical assurance.

## Digest Rules

SHA-256 values:

- are calculated over raw file bytes;
- use quoted lowercase 64-character hexadecimal strings in YAML;
- are not calculated after newline, Unicode, YAML, JSON, or CSV normalization;
- change whenever file bytes change.

Missing digests do not automatically make provenance invalid. They prevent verified assurance for the applicable historical evidence or prevent deterministic freshness comparison for current evidence.

A historical digest mismatch makes the historical envelope invalid. A current review-context digest mismatch makes the review context invalid and does not retroactively lower historical assurance.

## Artifact Index

The normative schema is `schemas/eval-run-artifact-index-v1.schema.json`.

`artifact_index.yaml` is optional. When present, it must contain at least one artifact. An empty artifact index is schema-invalid.

Each artifact entry requires only `artifact_id`, `artifact_type`, and `path`. Optional fields include `case_id`, `trial_id`, `evaluator_ref`, `media_type`, `digest`, `annotations`, and `extensions`. If `trial_id` is present, `case_id` is required.

Artifact semantic rules are normative:

- top-level artifact-index `run_id` must equal manifest `run.id`;
- `artifact_id` values must be unique;
- normalized artifact paths must be unique;
- `trial_id` requires `case_id`;
- artifact `case_id` and `trial_id` must agree with applicable CSV result evidence;
- `evaluator_ref`, when present, must resolve to the top-level evaluator ID or one component ID of a hybrid evaluator;
- artifact paths must resolve safely and remain contained;
- artifact files must exist and be regular files;
- symlinks are prohibited;
- digest mismatches are invalid;
- every applicable CSV `observed_output_path` used for verified evidence must map to exactly one artifact entry.

A non-empty CSV `observed_output_path` is allowed without an artifact index for legacy or declared evidence. Verified artifact provenance requires each applicable non-empty `observed_output_path` to resolve to exactly one artifact-index entry. Controlled-launch eligibility requires verified mapping for output artifacts that contribute to selected release evidence. Missing artifact indexing leaves artifact assurance incomplete; it is not automatically structural invalidity. Contradictory, ambiguous, unsafe, or digest-mismatched artifact mappings are invalid.

Mapping is performed by normalizing the CSV `observed_output_path` relative to the run-scoped CSV, normalizing artifact-index paths relative to `artifact_index.yaml`, comparing resolved run-relative paths, and requiring exactly one matching artifact entry.

Artifact identities inherit run, candidate, and top-level evaluator identity from the run manifest and artifact index. Artifact entries do not repeat run, candidate, or evaluator identity.

## Review Context, Freshness, And Recency

The normative schema is `schemas/eval-run-review-context-v1.schema.json`.

Review context supplies current release state for comparison without putting mutable state inside the immutable historical run manifest. It requires `schema_version`, `candidate.id`, and `candidate.version`. It may include `candidate.artifact`, `inputs`, `recency_policy`, `observed_at`, and `extensions`.

When `recency_policy` is present, the review context must include `observed_at`, `recency_policy.max_age_days`, and `recency_policy.max_future_clock_skew_seconds`. All time comparisons use UTC. Missing historical `run.completed_at` with configured recency policy produces `recency: unknown`. `run.started_at > run.completed_at` is invalid when both are supplied. `run.completed_at > observed_at + max_future_clock_skew_seconds` makes the review context invalid.

`evaluation.policy`, `review_context.recency_policy`, and the governing OpenEvalGate review or authorization policy have different jobs:

- `evaluation.policy` describes how the historical evaluation run was conducted.
- `review_context.recency_policy` supplies the age threshold and observation time used to classify evidence as acceptable, expired, or unknown.
- the governing OpenEvalGate review or authorization policy determines whether controlled launch may proceed when no recency limit has been configured.

Provenance reports `recency: not_configured` when no age policy is configured. A future authorization implementation determines whether that state is acceptable for controlled launch. The default is blocked unless the governing OpenEvalGate review policy explicitly permits the absence of a configured evidence-age limit. That permission does not come from the historical run manifest, `evaluation.policy`, or the absence of `review_context.recency_policy`.

Freshness comparison operates over:

1. candidate identity and candidate artifact;
2. every resource declared in `run_manifest.inputs[]`.

The complete historical `inputs[]` set is the canonical freshness comparison scope. For each historical input:

- known singleton resources match by `role`;
- repeatable and custom resources match by `(role, name)`;
- exactly one current counterpart must exist;
- matching identity and digest means current for that resource;
- different digest means stale;
- missing counterpart means overall freshness `unknown`;
- insufficient locator, identity, or digest evidence means overall freshness `unknown`;
- duplicate current counterparts make the review context invalid;
- extra current resources that were not present historically do not make historical evidence stale.

When review context is present, candidate ID and version are always compared. If historical `candidate.artifact` exists, current `candidate.artifact` is required for freshness to become `current`. Matching candidate artifact digest means current; different current candidate artifact digest means stale; missing or unverifiable current candidate artifact means unknown. If historical candidate artifact is absent, matching candidate ID and version are sufficient for candidate comparison. No review context means overall freshness `unknown`.

A valid envelope may be classified `freshness: current` only when the candidate and every historical input in scope are successfully compared. Controlled-launch eligibility requires freshness to be `current`.

## Invalidity And Drift States

The provenance model distinguishes four states:

1. Historical-envelope invalidity. The immutable run evidence is invalid, including manifest schema failure, historical digest mismatch, invalid historical path, missing historical local file, CSV identity contradiction, artifact-index contradiction, duplicate historical resource identity, or timestamp-order failure inside the historical manifest. Classification uses `validity: invalid`, `freshness: not_evaluated`, `recency: not_evaluated`, and `assurance: unavailable`. Lifecycle may reflect a recognized valid v1 `run.status` when available, except unsupported schema versions use `lifecycle: unknown`.

2. Review-context invalidity. The historical envelope is valid, but the current comparison context is structurally or semantically invalid, including review-context schema failure, duplicate current counterparts, unsafe current path, missing current local file, current descriptor digest mismatch, or future clock-skew contradiction. Classification uses `validity: invalid`, `freshness: not_evaluated`, and `recency: not_evaluated`, while preserving historical assurance and lifecycle.

3. Incomplete current comparison evidence. Current evidence is absent or insufficient but not contradictory, including no review context, a missing current counterpart, missing current candidate artifact, or descriptors lacking enough digest or identity evidence. Historical validity and assurance are preserved, freshness becomes `unknown`, and controlled launch is blocked.

4. Valid drift. Current evidence is valid and comparable but differs from historical evidence, including candidate ID or version mismatch, candidate artifact digest drift, or resource digest drift. Historical validity and assurance are preserved, freshness becomes `stale`, and controlled launch is blocked.

`assurance: verified` evaluates the immutable historical run envelope. `freshness: current` evaluates current comparison evidence. Missing or invalid current evidence does not retroactively make historical assurance declared or unavailable.

## Classification Vocabulary

Provenance is classified across independent dimensions. These are the only v1 values.

| Dimension | Values |
| --- | --- |
| Manifest presence | `present`, `legacy_absent` |
| Validity | `valid`, `invalid`, `not_evaluated` |
| Freshness | `current`, `stale`, `unknown`, `not_evaluated` |
| Recency | `acceptable`, `expired`, `unknown`, `not_configured`, `not_evaluated` |
| Assurance | `unavailable`, `declared`, `verified` |
| Lifecycle | `complete`, `failed`, `incomplete`, `unknown` |
| Documentation and shadow authorization | `allowed`, `allowed_with_warning`, `blocked` |
| Controlled-launch authorization | `eligible`, `blocked` |

Signed attestation is reserved for a future contract version and is not a v1 classification.

## Assurance

`unavailable` means no usable historical provenance assurance can be established because no run manifest exists, the manifest is schema-invalid, or the historical evidence envelope is semantically invalid. Examples include unsupported schema version, missing required manifest fields, historical digest mismatch, unsafe historical path, contradictory run identity, duplicate artifact identity, or duplicate singleton resource role.

`declared` means a structurally and semantically valid run manifest exists, but the complete applicable historical envelope has not been integrity-verified. Examples include an applicable local descriptor lacking a digest, results CSV not digest-verified, an applicable artifact not indexed or digest-verified, URI-only evidence without a resolver supplying verified bytes, or an applicable declared file not verified.

`verified` means the historical envelope is valid and all applicable evidence declared as part of it is integrity-verified. At minimum:

- every applicable historical local descriptor has a digest;
- each digest matches finalized raw file bytes;
- the results CSV digest matches;
- artifact-index bytes match when the manifest declares an artifact index;
- each applicable selected output artifact is uniquely mapped;
- each applicable selected output artifact has a matching digest;
- paths and identities are internally consistent;
- URI-only evidence has verified bytes supplied by an explicitly configured resolver, or it prevents verified assurance.

`verified` does not imply freshness is current, recency is acceptable, lifecycle is complete, or evidence is sufficient for controlled launch.

## Recency Precedence

| Condition | Recency |
| --- | --- |
| Legacy evidence with no manifest | `not_evaluated` |
| Invalid provenance envelope | `not_evaluated` |
| Valid provenance with no recency policy | `not_configured` |
| Recency policy exists, but required evidence is missing | `unknown` |
| Computed age is within policy threshold | `acceptable` |
| Computed age exceeds policy threshold | `expired` |

Evidence age is `observed_at - run.completed_at`. `age <= max_age_days` is acceptable. Fixture evaluation must never silently use the machine's current time.

## Lifecycle

Lifecycle is derived from a recognized v1 manifest status:

| Manifest condition | Lifecycle |
| --- | --- |
| `run.status: complete` | `complete` |
| `run.status: failed` | `failed` |
| `run.status: aborted` | `incomplete` |
| Unsupported schema version | `unknown` |
| No manifest | `unknown` |

Recognized v1 schema with semantic invalidity may still report lifecycle from the valid parsed v1 status. Recognized v1 schema with another required field missing may report lifecycle from `run.status` when a valid parsed v1 status is available. Unsupported schema versions do not interpret `run.status` using v1 semantics. Unparseable YAML is out of scope for PR 18.

Only `complete` lifecycle may support controlled launch, and only when all other provenance requirements pass.

## Ordered Authorization Rules

The authorization rules are ordered. Earlier rules take precedence over later rules.

1. Invalid provenance: documentation `allowed_with_warning`, shadow `blocked`, controlled launch `blocked`.
2. Failed or incomplete lifecycle: documentation `allowed_with_warning`, shadow `blocked`, controlled launch `blocked`.
3. Stale evidence: documentation `allowed_with_warning`, shadow `allowed_with_warning`, controlled launch `blocked`.
4. Expired evidence: documentation `allowed_with_warning`, shadow `allowed_with_warning`, controlled launch `blocked`.
5. Recency unknown under a configured recency policy: documentation `allowed`, shadow `allowed_with_warning`, controlled launch `blocked`.
6. Legacy evidence: documentation `allowed`, shadow `allowed_with_warning`, controlled launch `blocked`.
7. Valid, declared, complete evidence: documentation `allowed`, shadow `allowed`, controlled launch `blocked`. This includes the adoption-friendly case where freshness is `unknown` because no review context was supplied.
8. Valid, verified evidence with freshness unknown: documentation `allowed`, shadow `allowed_with_warning`, controlled launch `blocked`.
9. Valid, verified, current, complete evidence with acceptable recency: documentation `allowed`, shadow `allowed`, controlled launch `eligible`.
10. Valid, verified, current, complete evidence with recency not configured: controlled launch is eligible only when the governing OpenEvalGate review or authorization policy explicitly permits proceeding without a configured evidence-age limit. Otherwise documentation is `allowed`, shadow is `allowed`, and controlled launch is `blocked`.

Documentation access means evidence may be inspected, not trusted. `allowed_with_warning` must not imply invalid evidence is trustworthy. A present-but-invalid manifest never falls back to legacy handling. A high evaluation score, documentation score, or pass rate cannot override provenance authorization limits.

## Legacy Compatibility

Projects without `run_manifest.yaml` remain readable during the compatibility window:

```yaml
provenance:
  manifest_presence: legacy_absent
  validity: not_evaluated
  freshness: not_evaluated
  recency: not_evaluated
  assurance: unavailable
  lifecycle: unknown

authorization:
  documentation: allowed
  shadow: allowed_with_warning
  controlled_launch: blocked
```

This compatibility does not apply to malformed, schema-invalid, or contradictory manifests.

## JSON Schema Validation Profile

Provenance contract validation uses JSON Schema Draft 2020-12. Validators must enable `format` assertions. `date-time` values are validated as RFC 3339 date-times, and `uri` values are validated by a Draft 2020-12-compatible format checker. Validators that treat `format` as documentation only are insufficient for conformance-fixture validation.

Identifier-like fields use a pattern equivalent to `^\S(?:[^\r\n]*\S)?$` to reject leading whitespace, trailing whitespace, empty strings, whitespace-only strings, and embedded CR or LF characters. Media type fields use a dedicated non-empty string rule that rejects CR/LF while allowing values such as `text/plain; charset=utf-8`.

## Finding Identifiers

Finding identifiers are stable within contract major version 1. Future runtime output may emit these IDs, and fixtures may require exact IDs. Removing or changing an ID requires a contract-version compatibility decision. This registry does not mean general CLI JSON output is implemented.

Registered v1 finding IDs:

- `provenance_manifest_absent`
- `provenance_manifest_schema_invalid`
- `provenance_unsupported_schema_version`
- `provenance_results_path_required`
- `provenance_run_id_mismatch`
- `provenance_candidate_alias_mismatch`
- `provenance_evaluator_alias_mismatch`
- `provenance_input_digest_mismatch`
- `provenance_output_digest_mismatch`
- `provenance_review_context_digest_mismatch`
- `provenance_artifact_index_schema_invalid`
- `provenance_artifact_identity_mismatch`
- `provenance_duplicate_artifact_id`
- `provenance_duplicate_artifact_path`
- `provenance_duplicate_singleton_role`
- `provenance_duplicate_hybrid_component_id`
- `provenance_duplicate_resource_mismatch`
- `provenance_unsafe_path`
- `provenance_local_file_missing`
- `provenance_timestamp_order_invalid`
- `provenance_future_timestamp_invalid`
- `provenance_candidate_stale`
- `provenance_evidence_stale`
- `provenance_freshness_unknown`
- `provenance_recency_unknown`
- `provenance_evidence_expired`
- `provenance_lifecycle_failed`
- `provenance_lifecycle_incomplete`

## Threat Model And Non-Claims

This contract can detect policy drift, candidate mismatch, modified or swapped artifacts, run/case/trial identity conflicts, incomplete lifecycle, and evidence that no longer applies to a release target.

It does not prove evaluator honesty, human participation, candidate-output authenticity, producer-host integrity, or that a digest record was not fabricated before recording.

Version 1 is a locally verifiable evidence contract, not a cryptographically trusted attestation.

## Versioning And Extensions

`schema_version` is a major-version string. Version 1 consumers reject unsupported major versions. Strict schemas reject unknown standard fields. Backward-compatible v1 additions must be namespaced under explicit `extensions` fields where supported. Unknown extensions may be ignored only when doing so cannot increase authorization.

## Review Provenance Is Separate

Eval-run provenance records what produced evaluation evidence.

A future review-provenance contract should record which OpenEvalGate version, review policy, command, and report inputs produced a release assessment. The OpenEvalGate version is intentionally not part of `run_manifest.yaml` unless OpenEvalGate itself acted as the external run producer.

## Relationship To External Standards

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

## Conformance Fixtures

Self-contained fixture directories under `spec/fixtures/provenance/v1/` include real input, result, artifact, review-context, and expected-classification files. Recorded SHA-256 values are computed from fixture bytes. Expected classifications are validated by `schemas/eval-run-provenance-expected-v1.schema.json` and `tests/test_provenance_contract_fixtures.py`.

The fixtures are normative contract examples, but PR 18 does not make production code execute them.

## Implementation Sequence

Future implementation work is expected to:

1. Parse manifests, existing compatible result CSVs, artifact indexes, and review context.
2. Validate schema, identity, uniqueness, containment, lifecycle, and envelope digests.
3. Classify presence, validity, freshness, recency, assurance, lifecycle, and authorization.
4. Surface classifications in reports.
5. Connect provenance eligibility to controlled-launch authorization.

Each implementation step must preserve fail-closed behavior.
