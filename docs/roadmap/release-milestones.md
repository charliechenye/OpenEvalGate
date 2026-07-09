# OpenEvalGate Release Milestones

This document defines the dependency order from private development to public visibility, the first substantive public release, and eventual stable `1.0.0` contracts.

## Milestone Sequence

```text
Private repository
  -> Public repository (pre-1.0, no stable-release claim)
  -> OpenEvalGate 0.2.0 public alpha
  -> 0.x adoption and compatibility stabilization
  -> OpenEvalGate 1.0.0 stable contracts
```

These milestones are intentionally separate. Public visibility is a disclosure, governance, and claim-safety decision. `0.2.0` is a product release. `1.0.0` is a compatibility commitment.

## Milestone A: Public Repository

### Goal

Make the current project safe and credible for public inspection without implying feature completeness, external validation, or stable compatibility.

### Required workstreams

1. Public positioning, limitations, and bounded claims.
2. Reproducible passing and blocked reference examples.
3. Governance, support, attribution, and release policies.
4. CI quality, dependency, and security checks.
5. Branch protection and repository security settings.
6. Current-tree and Git-history disclosure audit.
7. Exact-commit verification and public-launch freeze.

### Planned PR order

1. Reposition OpenEvalGate for public alpha and document limitations.
2. Validate and recompute behavioral evaluation evidence.
3. Define and implement the local eval-run provenance contract subset for controlled-launch evidence.
4. Add passing and blocked public reference scenarios.
5. Define public governance, support, and compatibility policies.
6. Add public-repository quality and security gates.
7. Audit repository contents for safe public disclosure.
8. Finalize OpenEvalGate public-alpha readiness.

Evidence-integrity work is included before public visibility because it protects the repository's central release-assurance claim. Product-expansion work is not.

### Public-visibility exit criteria

- Public claims are bounded and examples are clearly illustrative.
- No known malformed, contradictory, or stale evidence path can silently produce a permissive controlled-launch result.
- Governance, support, security reporting, and compatibility expectations are documented.
- Required CI and repository protections are enabled.
- The repository tree and history pass disclosure review.
- The exact visibility commit passes required checks and clean-wheel reproduction.
- The project remains explicitly pre-1.0.

### Deferred until after visibility

- scaffolding breadth;
- JSON and SARIF integration output;
- vendor adapters;
- hosted services;
- external case studies;
- stable `1.0.0` guarantees.

## Milestone B: OpenEvalGate 0.2.0

### Goal

Ship the first substantive public-alpha release around **evidence integrity and minimal adoption**.

### Required capabilities

- internally consistent eval-result validation;
- duplicate, timestamp, reference, and output-path validation;
- proposed run provenance contract and fixture-integrity checks for selected path, artifact-identity, digest, lifecycle, freshness, and recency branches, with the local runtime identity, digest, lifecycle, assurance, freshness, and recency subset implemented;
- controlled-launch evidence pinned to an explicit run;
- a minimal installed-wheel onboarding path;
- versioned JSON output and documented exit behavior;
- passing and blocked canonical examples;
- exact-release-commit verification and release artifacts.

### Release positioning

`0.2.0` is public alpha. It may make documented schema or policy changes in later `0.x` releases. It is not a stable compatibility promise.

## Milestone C: 0.x Adoption and Stabilization

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

Make a stable public-contract commitment.

### Required stability

- versioned schemas and migration rules;
- stable CLI commands and exit codes;
- stable machine-readable output;
- stable blocker identifiers and recommendation semantics;
- compatibility fixtures for supported prior schemas;
- tested deprecation, upgrade, and rollback procedures;
- operational provenance and freshness rules; the contract may be proposed earlier, but runtime enforcement is required for 1.0;
- independent adoption and integration evidence.

`1.0.0` should not be scheduled by calendar alone. It should follow demonstrated compatibility and adoption maturity.
