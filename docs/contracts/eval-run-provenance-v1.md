# Eval-Run Provenance Contract v1

Status: proposed contract for a future OpenEvalGate release

## Purpose

OpenEvalGate evaluates externally produced evidence for AI-assistant and agent launch decisions. Metrics are not decision-ready unless reviewers can determine which candidate, policies, evaluator, inputs, and outputs produced them, and whether those artifacts still match the release under review.

This contract defines a vendor-neutral, run-scoped evidence envelope for existing OpenEvalGate-compatible eval results. The central adoption rule is:

> The provenance manifest wraps an existing compatible `eval_results.csv`. It does not require external eval systems to adopt new provenance columns or rewrite every row.

The contract does not make OpenEvalGate an eval runner, hosted governance platform, runtime guardrail, or certification authority. PR 18 defines the contract only; runtime parsing, report rendering, controlled-launch enforcement, blockers, and authorization code are not implemented here.

## Scope

Version 1 defines:

- a run directory containing an existing compatible `eval_results.csv`;
- `run_manifest.yaml` for run-level identity, lifecycle, evaluator identity, and optional pinned evidence;
- optional `artifact_index.yaml` for machine-readable output artifact identity;
- optional review context for current-release freshness and recency comparison;
- lifecycle, validity, freshness, recency, assurance, and authorization vocabulary;
- bounded compatibility for projects without a manifest.

Version 1 does not define a new CSV row schema, remote attestation, vendor adapters, OpenEvalGate review provenance, runtime enforcement, or report output.

## Evidence Envelope

A typical run directory may look like:

```text
eval_runs/
  run_002/
    run_manifest.yaml
    eval_results.csv
    artifact_index.yaml
    artifacts/
      case_001.md
```

Directory names are not authoritative. The manifest declares the run-level identity, and existing CSV values are cross-checked against it.

The existing OpenEvalGate `eval_results.csv` contract remains authoritative. This contract does not require new CSV columns, including:

- `candidate_id`
- `candidate_version`
- `evaluator_id`
- `primary_output_artifact_id`

The existing CSV fields remain the compatibility surface for result rows, including:

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

Manifest values are inherited by rows and artifacts instead of being repeated as new CSV provenance columns:

- immutable candidate ID and version;
- producer identity, when supplied;
- evaluation framework identity, when supplied;
- evaluator identity and kind;
- lifecycle status;
- run timestamps, when supplied;
- input and output descriptors, when supplied.

Missing producer, framework, evaluation policy, timestamps, digests, inputs, candidate artifact, artifact index, or review context does not automatically make a manifest structurally invalid. Those fields affect assurance, freshness, recency, and controlled-launch eligibility.

## CSV Cross-Checks

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

`evaluation.policy` is an optional descriptor identifying the policy, protocol, or procedure governing the historical evaluation run as a whole. Examples include a review procedure, scoring policy, test execution protocol, or evaluation governance policy.

Hybrid `evaluation.evaluator.decision_policy` is a required descriptor for hybrid evaluators. It identifies the aggregation, arbitration, or adjudication rule that combines component evaluator results into a final result. Examples include human-review tie-break, deterministic-check override, weighted component aggregation, or unanimous-pass requirement.

They may coexist. They are not aliases and must not be collapsed into one field.

## Resource And File Evidence

The schema separates fixed-purpose file descriptors from named input resources.

File descriptors are used for candidate artifacts, result CSVs, artifact indexes, evaluator configuration artifacts, and fixed-purpose output or configuration files. They do not require a `role`.

Named resource descriptors are used for manifest inputs and review-context inputs. They require `role`, keep roles extensible, and may require `name` for repeatable resources.

Known singleton input roles may appear at most once:

- `eval_cases`
- `evaluation_policy`
- `review_policy`
- `routing_policy`
- `escalation_contract`
- `action_risk_matrix`

Custom roles are allowed. Custom roles default to repeatable and require `name`. Repeatable resources match between historical evidence and current review context by `(role, name)`. Duplicate singleton roles are semantically invalid.

URI-only evidence is valid declared evidence. Network retrieval is disabled by default. URI-only evidence cannot become locally verified unless an explicitly configured resolver supplies matching bytes. Resolver behavior is out of scope for PR 18.

## Digest And Path Rules

SHA-256 values:

- are calculated over raw file bytes;
- use quoted lowercase 64-character hexadecimal strings in YAML;
- are not calculated after newline, Unicode, YAML, JSON, or CSV normalization;
- change whenever file bytes change.

Missing digests do not automatically make provenance invalid. They prevent verified assurance for the applicable evidence.

Local paths must be relative to the file containing the descriptor, resolve within the allowed evidence root, and reference existing regular files when verified. Absolute paths, path escapes after resolution, and symlinks are invalid when path safety is evaluated.

## Artifact Index

The normative schema is `schemas/eval-run-artifact-index-v1.schema.json`.

`artifact_index.yaml` is optional. It is not required when the CSV contains all decision-relevant evidence and no external output artifact is reviewed as release evidence. When an artifact index is present, it must contain at least one artifact; an empty artifact index is schema-invalid.

Each artifact entry requires `artifact_id`, `artifact_type`, and `path`. Optional fields include `case_id`, `trial_id`, `evaluator_ref`, `media_type`, `digest`, `annotations`, and `extensions`. If `trial_id` is present, `case_id` is required.

Artifact indexing rules:

- a non-empty CSV `observed_output_path` is allowed without an artifact index for legacy or declared evidence;
- verified artifact provenance requires each applicable non-empty `observed_output_path` to resolve to exactly one artifact-index entry;
- controlled-launch eligibility requires verified mapping for output artifacts that contribute to selected release evidence;
- missing artifact indexing leaves artifact assurance incomplete; it is not automatically structural invalidity;
- contradictory, ambiguous, unsafe, or digest-mismatched artifact mappings are invalid.

Mapping is performed by normalizing the CSV `observed_output_path` relative to the run-scoped CSV, normalizing artifact-index paths relative to `artifact_index.yaml`, comparing resolved run-relative paths, and requiring exactly one matching artifact entry.

Artifact identities inherit run, candidate, and top-level evaluator identity from the run manifest and artifact index. Artifact entries do not need to repeat candidate or evaluator identity. For hybrid evaluations, optional `evaluator_ref` may identify the top-level evaluator or one component.

## Review Context And Freshness

The normative schema is `schemas/eval-run-review-context-v1.schema.json`.

Review context supplies current release state for comparison without putting mutable state inside the immutable historical run manifest. A review context requires `schema_version`, `candidate.id`, and `candidate.version`. It may include `candidate.artifact`, `inputs`, `recency_policy`, `observed_at`, and `extensions`. If `recency_policy` is present, `observed_at` is required for deterministic recency evaluation.

`evaluation.policy`, `review_context.recency_policy`, and the governing OpenEvalGate review or authorization policy have different jobs:

- `evaluation.policy` describes how the historical evaluation run was conducted.
- `review_context.recency_policy` supplies the age threshold and observation time used to classify evidence as acceptable, expired, or unknown.
- the governing OpenEvalGate review or authorization policy determines whether controlled launch may proceed when no recency limit has been configured.

Freshness rules:

- invalid historical envelope -> `not_evaluated`;
- no review context -> `unknown`;
- required current comparison resource absent -> `unknown`;
- current descriptor exists but lacks sufficient verified identity or digest information -> `unknown`;
- valid historical envelope plus matching current identity and matching digest -> `current`;
- valid historical envelope plus matching current identity and different digest -> `stale`;
- candidate ID or version mismatch against the release target -> `stale`;
- historical bytes not matching the historical recorded digest -> invalid, not stale.

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

## Classification Precedence

Classification follows these precedence rules:

1. Legacy evidence with no manifest:

   ```yaml
   provenance:
     manifest_presence: legacy_absent
     validity: not_evaluated
     freshness: not_evaluated
     recency: not_evaluated
     assurance: unavailable
     lifecycle: unknown
   ```

2. Invalid historical envelope:

   ```yaml
   provenance:
     manifest_presence: present
     validity: invalid
     freshness: not_evaluated
     recency: not_evaluated
     assurance: unavailable
   ```

   Do not evaluate freshness or recency when the historical envelope is invalid.

3. Valid envelope without review context:

   ```yaml
   validity: valid
   freshness: unknown
   ```

4. Valid envelope without recency policy:

   ```yaml
   recency: not_configured
   ```

5. Valid but stale evidence:

   ```yaml
   validity: valid
   freshness: stale
   ```

   Recency remains independent and may be `acceptable`, `expired`, `unknown`, or `not_configured`.

6. Valid but expired evidence:

   ```yaml
   validity: valid
   freshness: current
   recency: expired
   ```

7. Fully current evidence that may become eligible:

   ```yaml
   validity: valid
   freshness: current
   assurance: verified
   lifecycle: complete
   ```

   Recency must be `acceptable`, or `not_configured` only when the governing OpenEvalGate review or authorization policy explicitly permits proceeding without a configured evidence-age limit.

Recency precedence:

| Condition | Recency |
| --- | --- |
| Legacy evidence with no manifest | `not_evaluated` |
| Invalid provenance envelope | `not_evaluated` |
| Valid provenance with no recency policy | `not_configured` |
| Recency policy exists, but required evidence is missing | `unknown` |
| Computed age is within policy threshold | `acceptable` |
| Computed age exceeds policy threshold | `expired` |

Provenance reports `recency: not_configured` when no age policy is configured. A future authorization implementation determines whether that state is acceptable for controlled launch. The default is blocked unless the governing OpenEvalGate review or authorization policy explicitly permits the absence of a configured evidence-age limit. That permission does not come from the historical run manifest, `evaluation.policy`, or the absence of `review_context.recency_policy`.

## Assurance

`unavailable` means no usable provenance assurance can be established because no run manifest exists, the manifest is schema-invalid, or the historical evidence envelope is semantically invalid. Examples include unsupported schema version, missing required manifest fields, historical digest mismatch, unsafe path, contradictory run identity, duplicate artifact identity, or duplicate singleton resource role.

`declared` means a structurally and semantically valid run manifest exists, but the complete applicable evidence envelope has not been integrity-verified. Examples include:

- an applicable local descriptor lacks a digest;
- results CSV is not digest-verified;
- an applicable artifact is not indexed or digest-verified;
- URI-only evidence has no configured resolver supplying verified bytes;
- an applicable declared file has not been verified.

`verified` means the historical envelope is valid and all applicable evidence declared as part of it is integrity-verified. At minimum:

- every applicable local descriptor has a digest;
- each digest matches finalized raw file bytes;
- the results CSV digest matches;
- artifact-index bytes match when the manifest declares an artifact index;
- each applicable selected output artifact is uniquely mapped;
- each applicable selected output artifact has a matching digest;
- paths and identities are internally consistent;
- URI-only evidence has verified bytes supplied by an explicitly configured resolver, or it prevents verified assurance.

`verified` does not imply freshness is current, recency is acceptable, lifecycle is complete, or evidence is sufficient for controlled launch.

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

1. Invalid provenance:

   ```yaml
   authorization:
     documentation: allowed_with_warning
     shadow: blocked
     controlled_launch: blocked
   ```

2. Failed or incomplete lifecycle:

   ```yaml
   authorization:
     documentation: allowed_with_warning
     shadow: blocked
     controlled_launch: blocked
   ```

3. Stale evidence:

   ```yaml
   authorization:
     documentation: allowed_with_warning
     shadow: allowed_with_warning
     controlled_launch: blocked
   ```

4. Expired evidence:

   ```yaml
   authorization:
     documentation: allowed_with_warning
     shadow: allowed_with_warning
     controlled_launch: blocked
   ```

5. Recency unknown under a configured recency policy:

   ```yaml
   authorization:
     documentation: allowed
     shadow: allowed_with_warning
     controlled_launch: blocked
   ```

6. Legacy evidence:

   ```yaml
   authorization:
     documentation: allowed
     shadow: allowed_with_warning
     controlled_launch: blocked
   ```

7. Valid, declared, complete evidence:

   ```yaml
   authorization:
     documentation: allowed
     shadow: allowed
     controlled_launch: blocked
   ```

   This includes the adoption-friendly case where freshness is `unknown` because no review context was supplied.

8. Valid, verified evidence with freshness unknown:

   ```yaml
   authorization:
     documentation: allowed
     shadow: allowed_with_warning
     controlled_launch: blocked
   ```

9. Valid, verified, current, complete evidence with acceptable recency:

   ```yaml
   authorization:
     documentation: allowed
     shadow: allowed
     controlled_launch: eligible
   ```

10. Valid, verified, current, complete evidence with recency not configured:

    Controlled launch is eligible only when the governing OpenEvalGate review or authorization policy explicitly permits proceeding without a configured evidence-age limit. Otherwise:

    ```yaml
    authorization:
      documentation: allowed
      shadow: allowed
      controlled_launch: blocked
    ```

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

Self-contained fixture directories under `spec/fixtures/provenance/v1/` will include real input, result, artifact, review-context, and expected-classification files. Recorded SHA-256 values must be computed from fixture bytes.

The fixtures are normative contract examples, but PR 18 does not make production code execute them.

## Implementation Sequence

Future implementation work is expected to:

1. Parse manifests, existing compatible result CSVs, artifact indexes, and review context.
2. Validate schema, identity, uniqueness, containment, lifecycle, and envelope digests.
3. Classify presence, validity, freshness, recency, assurance, lifecycle, and authorization.
4. Surface classifications in reports.
5. Connect provenance eligibility to controlled-launch authorization.

Each implementation step must preserve fail-closed behavior.
