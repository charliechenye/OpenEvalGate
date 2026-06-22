# Changelog

All notable changes to OpenEvalGate are documented in this file.

The project follows semantic versioning while it remains in alpha. Until a stable `1.0.0` release, minor versions may contain significant policy or schema changes.

## [Unreleased]

### Added

- Explicit limitations and non-claims for certification, safe-deployment
  guarantees, standards alignment, official integrations, external validation,
  and adoption evidence.
- Synthetic and illustrative notices for all canonical reference scenarios.
- Dedicated launch-gate and evidence-scoring methodology documentation.
- Editable canonical `review_policy.yaml` samples covering documentation,
  shadow-launch, and blocked controlled-launch review.
- Explicit documentation, shadow-launch, and controlled-launch review modes.
- Optional `review_policy.yaml` with selected run/candidate scope, coverage,
  trial-depth, and initial behavioral thresholds.
- Complete critical-case coverage and non-relaxable behavioral invariants.
- Deterministic controlled-launch sufficiency assessment and report tables.
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

- Public positioning now describes OpenEvalGate as a local release-assurance
  framework with bounded, evidence-backed recommendations.
- The README is shorter and links to detailed gate, scoring, and review-mode
  documentation.
- External guidance and adjacent tools are described as conceptual context and
  complementary workflows rather than formal alignment or official integration.
- Informational controlled-launch invariant failures no longer set documentation
  or shadow review critical-control status to `Fail`.
- Controlled-launch behavioral blockers and authorization now use only the
  selected run and candidate; reports distinguish unevaluated selection,
  invalid policy, invalid results, and informational full-file metrics.
- Canonical report reproduction is revalidated byte-for-byte through the installed wheel.
- Generated Markdown reports now use canonical LF line endings across platforms to preserve byte-for-byte reproducibility.
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
- Backward-compatible effective shadow mode for projects without a review policy.
