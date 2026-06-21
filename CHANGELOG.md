# Changelog

All notable changes to OpenEvalGate are documented in this file.

The project follows semantic versioning while it remains in alpha. Until a stable `1.0.0` release, minor versions may contain significant policy or schema changes.

## [Unreleased]

### Added

- Global `openevalgate --version` output derived from installed package metadata.
- Wheel and source-distribution content and metadata verification.
- Clean-wheel installation and installed console-script smoke testing.
- GitHub Actions validation across supported Python versions.
- Repository build and canonical-report reproducibility checks.
- Security reporting guidance.
- Contributor code of conduct.
- Citation and maintainer attribution metadata.
- Structured issue and pull request templates.

### Changed

- Canonical report reproduction is revalidated byte-for-byte through the installed wheel.
- Public package metadata now identifies the maintainer and project URLs.
- Contributor guidance now documents validation, evidence hygiene, compatibility review, and security reporting expectations.
- README roadmap language reflects that centralized hard-gate semantics are implemented.

## [0.1.1]

### Added

- Deterministic launch-recommendation semantics.
- Centralized policy evaluation for eight launch-blocking hard gates.
- Tri-state applicability for conditional gates.
- Strict positional action-risk parsing and whole-artifact invalidation.
- Deterministic hard-gate and diagnostic action-risk reporting.
- Cross-domain examples for customer support, presales, and education.
- Structured escalation and routing evidence.

### Preserved

- The 100-point evidence-completeness scoring model.
- Stable blocker IDs and CLI behavior.
- The shadow-only launch ceiling pending behavioral sufficiency policy.
