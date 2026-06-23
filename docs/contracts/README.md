# OpenEvalGate Contracts

This directory contains versioned, implementation-facing contracts for evidence used in release assurance.

## Available contracts

- [Eval-Run Provenance Contract v1](eval-run-provenance-v1.md) — defines how an evaluation run identifies its candidate, evaluator, policy inputs, results, output artifacts, digests, lifecycle, and freshness.

## Contract principles

Contracts in this directory are:

- vendor-neutral and local-first;
- versioned before enforcement is implemented;
- paired with machine-readable schemas where practical;
- paired with conformance fixtures that define expected behavior;
- explicit about compatibility, threat boundaries, and non-claims;
- designed so missing or contradictory evidence cannot silently authorize launch.

A contract may be published before the CLI enforces it. The document and fixtures establish the intended semantics; implementation status remains documented separately in the roadmap and release notes.
