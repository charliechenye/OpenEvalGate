# Code Map

This map is navigational, not normative. Verify the current tree before editing, and use this file to avoid broad repository scanning.

## Start Here

1. Identify the behavior being changed.
2. Find the corresponding row.
3. Open the primary implementation and focused tests.
4. Follow imports only when necessary.

## Areas

| Area | Primary implementation | Focused tests | Notes / downstream contracts |
| --- | --- | --- | --- |
| CLI entry point, exit behavior, JSON, decision cards, and minimal scaffolding | `openevalgate/cli.py`, `openevalgate/output.py`, `openevalgate/init_project.py` | `tests/test_cli_outputs.py`, `tests/test_report.py`, `tests/test_project_inspection.py`, `tests/test_version.py` | Console script is declared in `pyproject.toml`; default text/Markdown output and exit codes remain compatibility-sensitive. |
| Eval-case schema and parsing | `openevalgate/schema.py` | `tests/test_schema.py`, `tests/test_example_boundary_suites.py` | Owns YAML loading, enum values, validation issues, public dataclasses, and critical-case helpers. |
| Eval-result parsing and validation | `openevalgate/eval_results.py` | `tests/test_eval_results.py` | Owns CSV parsing, row identity, route evidence, timestamps, latest-run selection, summaries, and behavioral metrics. |
| Eval-run provenance parsing and identity validation | `openevalgate/provenance.py`, `openevalgate/local_paths.py`, `openevalgate/resources/schemas/` | `tests/test_provenance.py`, `tests/test_provenance_fixtures.py`, `tests/test_provenance_contract_fixtures.py`, `tests/test_provenance_resources.py`, `tests/test_eval_results.py` | Owns packaged schema loading, deterministic root/scoped manifest selection, selected run/candidate identity, lifecycle findings, authoritative result source selection, output identity, artifact-index identity, local digest verification, historical envelope consistency, review-context validation, assurance, freshness, recency, scope-aware conventional unbound-result detection, and fail-closed identity invalidation. Complete authorization classification remains deferred. |
| Provenance freshness and release-context comparison | `openevalgate/provenance.py`, `openevalgate/report.py` | `tests/test_provenance.py`, `tests/test_provenance_fixtures.py`, `tests/test_provenance_contract_fixtures.py`, `tests/test_report.py` | Compares historical candidate and input descriptors with project-level `review_context.yaml`, classifies current, stale, unknown, acceptable, expired, and declared or verified evidence, and surfaces findings in reports. Authorization enforcement remains deferred. |
| Review policy and behavioral sufficiency | `openevalgate/review_policy.py` | `tests/test_review_policy.py`, `tests/test_assessment.py`, `tests/test_report.py` | Controls review modes, selected scope, coverage, thresholds, invariants, and fail-closed behavioral evidence. |
| Launch-gate parsing | `openevalgate/launch_gate_review.py` | `tests/test_hard_gate_policy.py`, `tests/test_project_inspection.py`, `tests/test_report.py` | Parses Markdown gate rows, aliases, placeholders, meaningful evidence, and raw source-line diagnostics. |
| Hard-gate policy | `openevalgate/hard_gate_policy.py` | `tests/test_hard_gate_policy.py`, `tests/test_project_inspection.py` | Owns standard gate registry, conditional applicability, gate blockers, aliases, and status classification. |
| Project inspection and blocker derivation | `openevalgate/project_inspection.py`, `openevalgate/validator.py`, `openevalgate/action_risk.py` | `tests/test_project_inspection.py`, `tests/test_validator.py` | Combines project files into structural checks, action-risk context, independent blockers, and launch-blocking inspection output. |
| Evidence scoring | `openevalgate/scorer.py` | `tests/test_hard_gate_policy.py`, `tests/test_report.py` | Owns gate score calculation and status normalization; scoring changes can alter recommendations and canonical reports. |
| Launch assessment and recommendation semantics | `openevalgate/assessment.py` | `tests/test_assessment.py`, `tests/test_report.py` | Converts scores, hard blockers, review mode, and behavioral sufficiency into readiness category, recommendation, and next actions. |
| Report rendering and report writing | `openevalgate/report.py` | `tests/test_report.py` | Owns Markdown sections, headings, canonical LF bytes, report summaries, and generated report output. |
| Routing-policy validation | `openevalgate/routing.py` | `tests/test_routing.py`, `tests/test_eval_results.py`, `tests/test_report.py` | Validates routing policy models, workflows, assignments, fallbacks, eval references, and route expectation summaries. |
| Escalation-contract validation | `openevalgate/escalation.py` | `tests/test_escalation.py`, `tests/test_project_inspection.py`, `tests/test_report.py` | Validates escalation destinations, triggers, approvals, handoff evidence, fallback, SLA, and critical escalation blockers. |
| Canonical examples and generated reports | `examples/*`, `openevalgate/report.py`, `openevalgate/cli.py` | `tests/test_report.py`, `tests/test_example_boundary_suites.py` | Canonical `generated_launch_report.md` files are generated artifacts; reproduce affected examples through the CLI. |
| Packaging and installed-wheel behavior | `pyproject.toml`, `openevalgate/__init__.py`, `openevalgate/version.py`, `scripts/verify_distribution_artifacts.py` | `tests/test_distribution_artifacts.py`, `tests/test_version.py` | Covers package metadata, included files, console script, version behavior, and installed-wheel smoke behavior. |
| CI workflow | `.github/workflows/ci.yml` | Local validation depends on the edited step | The workflow is the source of truth for required CI behavior, Python versions, canonical example checks, build, artifact verification, and wheel smoke testing. |

## High-Risk Change Boundaries

Review compatibility carefully before changing:

- schemas;
- blocker identifiers;
- scoring weights;
- review-mode semantics;
- CLI exit codes;
- report headings or canonical bytes;
- public dataclasses and positional constructors;
- generated example artifacts.

## Maintenance

Update this map when module ownership or focused-test ownership materially changes.
