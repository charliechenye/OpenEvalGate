# Governance

OpenEvalGate is maintained as a small, local-first, deterministic open-source project. This document describes how scope, compatibility, releases, and safety-sensitive changes are decided.

## Maintainer authority

The maintainer is Chenye Zhu. The maintainer is responsible for:

- setting project scope and maintaining the documented non-goals;
- reviewing changes that affect schemas, blocker IDs, scoring, reports, CLI behavior, or trust invariants;
- deciding release timing, supported Python versions, and compatibility policy;
- coordinating security response and broken-release remediation; and
- accepting, declining, or requesting changes to contributions.

Contributors and reviewers are encouraged to challenge assumptions with tests, fixtures, and concrete evidence. A proposal that changes launch authorization or weakens a fail-closed path requires an explicit compatibility and trust-boundary review before merge.

## Decision rules

Changes should preserve deterministic output and fail-closed behavior. A change that affects a public contract must document its user impact, migration path, affected blocker or finding IDs, and required generated-artifact updates. Product breadth, integrations, and hosted features do not override the project's local-first and dependency-light scope.

## Compatibility and versioning

OpenEvalGate provides a stable Core Compatibility v1 promise from `0.1.0`.
The full scope of the product is not yet a `1.0.0` stability claim.

- patch releases fix defects without intentionally changing V1 public semantics;
- Core Compatibility v1 changes require an explicit compatibility decision,
  fixture coverage, and a `CHANGELOG.md` entry;
- a later V2 contract may add new semantics, but must not silently remove or
  change V1 during its documented support period;
- JSON is the parseable compatibility surface. Text, cards, and Markdown are
  deterministic within a release but may change; and
- only `openevalgate.__version__` is a public Python API.

The exact covered surface, schema requirements, stable blocker IDs, and
experimental exclusions are defined in [Core Compatibility v1](docs/contracts/core-compatibility-v1.md).

Schema, blocker-ID, exit-code, report, scoring, or public-dataclass changes require focused tests and compatibility review. Checked-in canonical reports are regenerated only when a semantic output change is intentional.

## Releases and rollback

Releases are created from a reviewed commit with passing CI, clean package-install and CLI smoke checks, reproducible canonical reports, and a recorded disclosure audit. A release identifies supported Python versions and known limitations. Tags are immutable release inputs; artifacts and GitHub Releases are created only after the tag's CI passes.

If a release is found to produce unsafe, non-deterministic, or materially broken behavior, the maintainer may withdraw or supersede it, publish a corrective release, and document the impact in `CHANGELOG.md`. Users should pin a known-good version when reproducibility matters.

## Security and conduct

Security vulnerabilities must follow [SECURITY.md](SECURITY.md), not a public issue. Community behavior is governed by the [Code of Conduct](CODE_OF_CONDUCT.md). Support expectations are described in [SUPPORT.md](SUPPORT.md).
