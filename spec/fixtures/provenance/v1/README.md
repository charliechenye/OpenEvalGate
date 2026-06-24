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
| `legacy-no-manifest` | Existing CSV without a manifest; readable but not launch-authorizing. |
| `minimal-declared-human` | Minimal valid manifest wrapping an unchanged existing CSV with declared assurance. |
| `valid-current-human` | Verified, current human-reviewed evidence with indexed artifact provenance. |
| `valid-current-deterministic` | Verified, current deterministic evaluator evidence. |
| `valid-current-model-judge` | Verified, current model-judge evaluator evidence. |
| `valid-current-hybrid` | Verified, current hybrid evaluator evidence with top-level evaluator identity. |
| `stale-policy-input` | Valid historical evidence whose current policy input has drifted. |
| `stale-candidate` | Valid historical evidence for a candidate version different from the current release target. |
| `invalid-input-digest` | Schema-valid manifest with a historical input digest mismatch. |
| `invalid-output-digest` | Schema-valid manifest with a result-output digest mismatch. |
| `invalid-run-identity` | Schema-valid manifest contradicted by CSV run identity. |
| `invalid-artifact-identity` | Schema-valid artifact index contradicted by result case/trial identity. |
| `invalid-unsafe-path` | Schema-valid descriptor with a semantically unsafe path escape. |
| `expired-evidence` | Valid current evidence that exceeds configured maximum age. |
| `failed-run` | Valid evidence from a failed run lifecycle. |
| `unsupported-schema-version` | Schema-invalid manifest with unsupported major schema version. |
| `duplicate-artifact-id` | Schema-valid artifact index with semantically duplicate artifact identity. |
| `duplicate-singleton-role` | Schema-valid inputs with semantically duplicate singleton role. |
| `empty-artifact-index` | Schema-invalid artifact index because an included index must be non-empty. |
| `missing-required-candidate-id` | Schema-invalid v1 manifest missing required candidate identity. |

## Interpretation

Legacy evidence has `assurance: unavailable`. Declared evidence has a structurally and semantically valid manifest, but the applicable historical envelope has not been fully integrity-verified. Verified evidence has matching digests and internally consistent identities for the applicable historical envelope.

Stale evidence is valid historical evidence that differs from current release context. Expired evidence is valid historical evidence that fails the configured age policy. Invalid evidence is not evaluated for freshness or recency and must not fall back to legacy handling.