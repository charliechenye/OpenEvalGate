# OpenEvalGate Contracts

This directory contains versioned, implementation-facing contracts for evidence used in release assurance.

## Available contracts

- [Eval-Run Provenance Contract v1](eval-run-provenance-v1.md) - defines how a run manifest can wrap an existing OpenEvalGate-compatible `eval_results.csv` with candidate, evaluator, policy, artifact, lifecycle, freshness, recency, and assurance metadata.

## Contract principles

Contracts in this directory are:

- vendor-neutral and local-first;
- versioned before enforcement is implemented;
- paired with machine-readable schemas where practical;
- paired with conformance fixtures that define expected behavior where practical;
- explicit about compatibility, threat boundaries, and non-claims;
- designed so missing or contradictory evidence cannot silently authorize launch.

A contract may be published before the CLI enforces it. The document and fixtures establish intended semantics; implementation status remains documented separately in the roadmap and release notes.

The eval-run provenance contract is proposed. It does not change the current CSV parser or require new provenance columns in `eval_results.csv`.
