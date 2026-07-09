# OpenEvalGate Contracts

This directory contains versioned, implementation-facing contracts for evidence used in release assurance.

## Available contracts

- [Eval-Run Provenance Contract v1](eval-run-provenance-v1.md) - defines how a run manifest can wrap an existing OpenEvalGate-compatible `eval_results.csv` with candidate, evaluator, policy, artifact, lifecycle, freshness, recency, assurance, finding, and authorization metadata.

## Provenance Schemas

The eval-run provenance contract is paired with four Draft 2020-12 schemas:

- `schemas/eval-run-manifest-v1.schema.json` for `run_manifest.yaml`.
- `schemas/eval-run-artifact-index-v1.schema.json` for `artifact_index.yaml`.
- `schemas/eval-run-review-context-v1.schema.json` for `review_context.yaml`.
- `schemas/eval-run-provenance-expected-v1.schema.json` for fixture `expected.yaml` classifications and registered finding IDs.

Fixture expectations under `spec/fixtures/provenance/v1/` are schema-validated and fixture-integrity checked by `tests/test_provenance_contract_fixtures.py`. PR 18 established the contract, schemas, fixture inventory, referenced-file checks, recorded-digest checks, orphan-file hygiene, and selected scenario invariants.

The runtime provenance subset implements manifest loading, selected run and candidate checks, evaluator identity checks, manifest-backed result selection, local digest verification for historical descriptors, historical envelope consistency checks, missing-manifest detection, unbound-result exclusion, report visibility, and controlled-launch blocking for missing, invalid, failed, or incomplete identity evidence. Verified assurance, freshness, recency, `review_context.yaml`, and complete contract authorization remain deferred.

## Contract principles

Contracts in this directory are:

- vendor-neutral and local-first;
- versioned before enforcement is implemented;
- paired with machine-readable schemas where practical;
- paired with conformance fixtures that define expected behavior where practical;
- explicit about compatibility, threat boundaries, and non-claims;
- designed so missing or contradictory evidence cannot silently authorize launch.

A contract may be published before the CLI enforces it. The document, schemas, and fixtures establish intended semantics; implementation status remains documented separately in the roadmap and release notes.

The eval-run provenance contract is proposed as a broader v1 contract. The current runtime implements its identity-enforcement subset and does not require new provenance columns in `eval_results.csv`.
