# Governance

OpenEvalGate is maintained as a small, local-first, deterministic open-source project. This document describes how scope, compatibility, releases, and safety-sensitive changes are decided while the project is pre-1.0.

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

OpenEvalGate follows a pre-1.0 compatibility policy:

- patch releases should fix defects without intentionally changing public semantics;
- minor `0.x` releases may change schemas, policy defaults, report wording, CLI behavior, or other documented contracts;
- breaking changes must be called out in `CHANGELOG.md` with migration guidance when migration is practical;
- deprecated fields or commands should remain documented for at least one release when feasible; and
- stable compatibility guarantees are reserved for `1.0.0` and later.

Schema, blocker-ID, exit-code, report, scoring, or public-dataclass changes require focused tests and compatibility review. Checked-in canonical reports are regenerated only when a semantic output change is intentional.

## Releases and rollback

Releases are created from a reviewed commit with passing CI, clean package-install and CLI smoke checks, and reproducible canonical reports. A release should identify its supported Python versions and known limitations.

If a release is found to produce unsafe, non-deterministic, or materially broken behavior, the maintainer may withdraw or supersede it, publish a corrective release, and document the impact in `CHANGELOG.md`. Users should pin a known-good version when reproducibility matters.

## Security and conduct

Security vulnerabilities must follow [SECURITY.md](SECURITY.md), not a public issue. Community behavior is governed by the [Code of Conduct](CODE_OF_CONDUCT.md). Support expectations are described in [SUPPORT.md](SUPPORT.md).

