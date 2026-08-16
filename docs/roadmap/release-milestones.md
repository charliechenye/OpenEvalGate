# OpenEvalGate Release Milestones

This document defines the dependency order from public release preparation to
the stable-core `0.1.0` release, product-scope maturation, and eventual
`1.0.0` adoption-backed stability.

## Milestone Sequence

```text
Public repository
  -> OpenEvalGate 0.1.0 stable Core Compatibility v1
  -> product-scope and adoption hardening
  -> 1.0.0 full-scope stability and adoption evidence
```

These milestones are intentionally separate. Public visibility is a disclosure,
governance, and claim-safety decision. `0.1.0` is a stable promise for the
defined core, while `1.0.0` is the later commitment for full product scope and
external adoption evidence.

## Milestone A: Public Repository

### Goal

Make the defined core safe, credible, versioned, and ready for a public stable
contract without implying feature completeness or external validation.

### Required workstreams

1. Public positioning, limitations, and bounded claims.
2. Reproducible passing and blocked reference examples.
3. Governance, support, attribution, and release policies.
4. CI quality, dependency, and security checks.
5. Branch protection and repository security settings.
6. Current-tree and Git-history disclosure audit.
7. Exact-commit verification and public-launch freeze.

### Planned PR order

1. Define Core Compatibility v1 and document limitations.
2. Validate and recompute behavioral evaluation evidence.
3. Define and implement the local eval-run provenance contract subset for controlled-launch evidence.
4. Add passing and blocked public reference scenarios.
5. Define public governance, support, and compatibility policies.
6. Add public-repository quality and security gates.
7. Audit repository contents for safe public disclosure.
8. Finalize OpenEvalGate stable-core readiness.

Evidence-integrity work is included before public visibility because it protects the repository's central release-assurance claim. Product-expansion work is not.

### Public-visibility exit criteria

- Public claims are bounded and examples are clearly illustrative.
- No known malformed, contradictory, or stale evidence path can silently produce a permissive controlled-launch result.
- Governance, support, security reporting, and compatibility expectations are documented.
- Required CI and repository protections are enabled.
- The repository tree and history pass disclosure review.
- The exact visibility commit passes required checks and clean-wheel reproduction.
- The stable promise is limited to Core Compatibility v1.

### Deferred until after the `0.1.0` release

- scaffolding breadth;
- SARIF integration output;
- vendor adapters;
- hosted services;
- external case studies;
- full product-scope `1.0.0` guarantees.

## Milestone B: Product-Scope and Adoption Hardening

### Goal

Extend evidence integrity and gather adoption evidence without silently
changing Core Compatibility v1.

### Required capabilities

- internally consistent eval-result validation;
- duplicate, timestamp, reference, and output-path validation;
- proposed run provenance contract and fixture-integrity checks for selected path, artifact-identity, digest, lifecycle, freshness, and recency branches, with the local runtime identity, digest, lifecycle, assurance, freshness, and recency subset implemented;
- controlled-launch evidence pinned to an explicit run;
- a minimal installed-wheel onboarding path;
- versioned JSON output, decision-card output, and documented exit behavior;
- passing and blocked canonical examples;
- exact-release-commit verification and release artifacts.

### Release positioning

Later releases may introduce a separately versioned contract. They do not
change V1 semantics, blocker IDs, JSON envelopes, or evidence schemas without
an explicit compatibility process.

## Milestone C: Adoption and Full-Scope Stabilization

### Goal

Test the framework outside the maintainer's own examples and stabilize contracts based on real practitioner usage.

### Required evidence

- three to five design partners contacted;
- at least two completed end-to-end external reviews;
- structured, permission-aware feedback;
- at least one external issue, review, or contribution;
- at least one sanitized case study;
- one integration chosen from demonstrated demand;
- migration experience across at least one schema revision.

### Product focus

- reduce onboarding friction;
- stabilize machine-readable contracts;
- separate normative specification from practitioner guidance;
- refine defaults using evidence rather than intuition;
- preserve fail-closed behavior during migration.

## Milestone D: OpenEvalGate 1.0.0

### Goal

Make a stable full-product-scope commitment.

### Required stability

- demonstrated V1 compatibility stewardship and any V2 migration rules;
- stable full-product-scope CLI commands and exit codes;
- stable machine-readable output across the expanded product;
- stable blocker identifiers and recommendation semantics across the expanded product;
- compatibility fixtures for supported contracts;
- tested deprecation, upgrade, and rollback procedures;
- operational provenance and freshness rules; the contract may be proposed earlier, but runtime enforcement is required for 1.0;
- independent adoption and integration evidence.

`1.0.0` should not be scheduled by calendar alone. It should follow demonstrated compatibility and adoption maturity.
