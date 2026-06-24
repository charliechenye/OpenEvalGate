# Provenance v1 Conformance Fixtures

These fixtures define normative examples for the proposed Eval-Run Provenance Contract v1.

They are contract fixtures, not executable OpenEvalGate runtime inputs yet. Production parsing, reporting, freshness evaluation, and controlled-launch enforcement remain pending.

## Directory Structure

Each fixture is a directory. Every fixture contains `expected.yaml`; other files appear only when relevant:

- `run_manifest.yaml` for declared or verified provenance;
- `eval_results.csv` using the existing OpenEvalGate CSV headers;
- `artifact_index.yaml` when output artifact provenance is indexed;
- `review_context.yaml` when current candidate, current inputs, or recency policy is compared;
- `inputs/` for preserved historical evidence;
- `current/` for current release-context evidence;
- `artifacts/` for output artifacts referenced by result rows.

Legacy fixtures intentionally omit `run_manifest.yaml`.

## Expected Shape

Each `expected.yaml` separates document schema validation from semantic provenance classification:

```yaml
schema_validation:
  manifest: valid
  artifact_index: not_present
  review_context: not_present

provenance:
  manifest_presence: present
  validity: valid
  freshness: unknown
  recency: not_configured
  assurance: declared
  lifecycle: complete

authorization:
  documentation: allowed
  shadow: allowed
  controlled_launch: blocked

findings: []
```

Allowed schema-validation values are `valid`, `invalid`, `not_present`, and `not_applicable`.

Allowed provenance values are defined by the contract:

- manifest presence: `present`, `legacy_absent`;
- validity: `valid`, `invalid`, `not_evaluated`;
- freshness: `current`, `stale`, `unknown`, `not_evaluated`;
- recency: `acceptable`, `expired`, `unknown`, `not_configured`, `not_evaluated`;
- assurance: `unavailable`, `declared`, `verified`;
- lifecycle: `complete`, `failed`, `incomplete`, `unknown`.

Documentation and shadow authorization use `allowed`, `allowed_with_warning`, or `blocked`. Controlled launch uses `eligible` or `blocked`.

## Inventory

| Fixture | Purpose |
| --- | --- |
| `aborted-run` | Minimal verified human-evaluator evidence whose aborted run status maps to incomplete lifecycle. |
| `candidate-alias-mismatch` | Schema-valid manifest contradicted by CSV candidate identity. |
| `contradictory-duplicate-resource` | Fixed-purpose evaluation policy and canonical input mirror disagree. |
| `duplicate-artifact-id` | Schema-valid artifact index with semantically duplicate artifact identity. |
| `duplicate-hybrid-component-id` | Hybrid evaluator components reuse the same component ID. |
| `duplicate-normalized-artifact-path` | Artifact entries use distinct path text that normalizes to one artifact file. |
| `duplicate-singleton-role` | Schema-valid inputs with semantically duplicate singleton role. |
| `empty-artifact-index` | Schema-invalid artifact index because an included index must be non-empty. |
| `evaluator-alias-mismatch` | Schema-valid manifest contradicted by CSV evaluator identity. |
| `expired-evidence` | Valid current evidence that exceeds configured maximum age. |
| `failed-run` | Valid evidence from a failed run lifecycle. |
| `freshness-unknown-missing-current-candidate-artifact` | Verified historical candidate artifact with no current candidate artifact counterpart. |
| `freshness-unknown-missing-current-input` | Verified historical input with no current input counterpart. |
| `future-clock-skew` | Verified historical envelope with current review observation contradicted by future clock skew. |
| `invalid-artifact-identity` | Schema-valid artifact index contradicted by result case/trial identity. |
| `invalid-input-digest` | Schema-valid manifest with a historical input digest mismatch. |
| `invalid-output-digest` | Schema-valid manifest with a result-output digest mismatch. |
| `invalid-run-identity` | Schema-valid manifest contradicted by CSV run identity. |
| `invalid-timestamp-order` | Historical manifest timestamps have start after completion. |
| `invalid-unsafe-path` | Schema-valid descriptor with a semantically unsafe path escape. |
| `legacy-no-manifest` | Existing CSV without a manifest; readable but not launch-authorizing. |
| `minimal-declared-human` | Minimal valid manifest wrapping an unchanged existing CSV with declared assurance. |
| `missing-local-file` | Historical run envelope references one missing local file. |
| `missing-required-candidate-id` | Schema-invalid v1 manifest missing required candidate identity. |
| `recency-unknown-missing-completed-at` | Verified current evidence with configured recency policy but no historical completion time. |
| `review-context-invalid-current-digest` | Verified historical envelope with a current-context descriptor digest mismatch. |
| `stale-candidate` | Valid historical evidence for a candidate version different from the current release target. |
| `stale-eval-cases` | Valid historical evidence whose current eval cases digest has drifted. |
| `stale-policy-input` | Valid historical evidence whose current policy input has drifted. |
| `stale-routing-policy` | Valid historical evidence whose current routing policy digest has drifted. |
| `unsupported-schema-version` | Schema-invalid manifest with unsupported major schema version. |
| `uri-only-results` | Manifest results descriptor is URI-only and therefore schema-invalid in v1. |
| `valid-current-deterministic` | Verified, current deterministic evaluator evidence. |
| `valid-current-human` | Verified, current human-reviewed evidence with indexed artifact provenance. |
| `valid-current-hybrid` | Verified, current hybrid evaluator evidence with top-level evaluator identity. |
| `valid-current-model-judge` | Verified, current model-judge evaluator evidence. |
| `verified-freshness-unknown` | Fully verified historical evidence with no review context for current comparison. |

## Interpretation

Legacy evidence has `assurance: unavailable`. Declared evidence has a structurally and semantically valid manifest, but the applicable historical envelope has not been fully integrity-verified. Verified evidence has matching digests and internally consistent identities for the applicable historical envelope.

Stale evidence is valid historical evidence that differs from current release context. Expired evidence is valid historical evidence that fails the configured age policy. Invalid evidence is not evaluated for freshness or recency and must not fall back to legacy handling.