# OpenEvalGate Contracts

This directory contains versioned, implementation-facing contracts for evidence used in release assurance.

## Available contracts

- [Eval-Run Provenance Contract v1](eval-run-provenance-v1.md) - defines how a run manifest can wrap an existing OpenEvalGate-compatible `eval_results.csv` with candidate, evaluator, policy, artifact, lifecycle, freshness, recency, assurance, finding, and authorization metadata.

## Provenance Schemas

The proposed eval-run provenance contract is paired with four Draft 2020-12 schemas:

- `schemas/eval-run-manifest-v1.schema.json` for `run_manifest.yaml`.
- `schemas/eval-run-artifact-index-v1.schema.json` for `artifact_index.yaml`.
- `schemas/eval-run-review-context-v1.schema.json` for `review_context.yaml`.
- `schemas/eval-run-provenance-expected-v1.schema.json` for fixture `expected.yaml` classifications and registered finding IDs.

Fixture expectations under `spec/fixtures/provenance/v1/` are machine-validated by `tests/test_provenance_contract_fixtures.py`. This validation is contract-development coverage; it does not implement production provenance parsing or CLI output.

## Contract principles

Contracts in this directory are:

- vendor-neutral and local-first;
- versioned before enforcement is implemented;
- paired with machine-readable schemas where practical;
- paired with conformance fixtures that define expected behavior where practical;
- explicit about compatibility, threat boundaries, and non-claims;
- designed so missing or contradictory evidence cannot silently authorize launch.

A contract may be published before the CLI enforces it. The document, schemas, and fixtures establish intended semantics; implementation status remains documented separately in the roadmap and release notes.

The eval-run provenance contract is proposed. It does not change the current CSV parser or require new provenance columns in `eval_results.csv`.
