# Changelog

All notable changes to OpenEvalGate are documented in this file.

The project follows semantic versioning while it remains in alpha. Until a stable `1.0.0` release, minor versions may contain significant policy or schema changes.

## [Unreleased]

### Added

- Public-alpha governance, support, attribution, compatibility, release, and rollback guidance.
- Enforceable Ruff, mypy, pip-audit, Bandit, and Markdown-link validation in CI.
- A copy-and-report onboarding path that keeps canonical example reports unchanged.
- Python support metadata and CI cover Python 3.10 through 3.14; local development currently uses Python 3.12.
- Runtime eval-run identity inspection for `run_manifest.yaml`, selected review-policy scope, manifest-backed result CSV identity, conventional output-directory identity, recognized Markdown output metadata, optional artifact-index identity, lifecycle findings, and missing/no-results classification, and unbound-result exclusion.
- Explicit packaged runtime provenance schemas, with wheel and source-distribution checks that compare packaged resources byte-for-byte against the normative top-level schemas.
- Expanded provenance contract fixture coverage for unsafe single-dot path segments and optional artifact identity fields, including positive omitted-identity mapping, negative wrong-trial mapping, and runtime fixture projection coverage.
- Non-empty core eval-result validation, duplicate identity rejection, strict
  ISO review-timestamp validation, and safe project-relative output references.
- Eval-case authority for expected routes and consistency validation for
  declared route matches.
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

- Result-bearing projects now require manifest-backed eval-run identity.
- Manifestless result files now fail provenance validation, while their rows are excluded from row validation, summaries, metrics, coverage, behavioral invariants, behavior-derived blockers, and launch decisions.
- Canonical examples now include complete versioned run manifests.
- Runtime identity states are now complete, missing, or invalid.
- Route-match metrics are derived from actual routes and authoritative eval
  cases instead of trusting the declared CSV boolean.
- Invalid result or eval-run identity evidence is rejected by whole-file and selected-scope
  summaries before it can influence behavioral or controlled-launch metrics.
- Informational latest-run selection now uses recorded review dates and
  offset-aware timestamps with a deterministic lexical run-ID tie-break.
- Public positioning now describes OpenEvalGate as a local release-assurance
  framework with bounded, evidence-backed recommendations.
- The README is shorter and links to detailed gate, scoring, and review-mode
  documentation.
- External guidance and adjacent tools are described as conceptual context and
  complementary workflows rather than formal alignment or official integration.
- Package metadata now uses the PEP 639 SPDX license expression and explicit
  license-file declaration supported by modern setuptools.
- Informational controlled-launch invariant failures no longer set documentation
  or shadow review critical-control status to `Fail`.
- Controlled-launch behavioral blockers and authorization now use only the
  selected run and candidate; reports distinguish unevaluated selection,
  invalid policy, invalid results, identity status, lifecycle status, missing provenance,
  unbound-result exclusion, and informational full-file metrics.
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
