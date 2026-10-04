# 0.1.1 integration preflight — 2026-10-04 UTC

This records local implementation and validation, not a published release or
independent adoption. Branch: `next-batch-iteration`. Base HEAD:
`5ccac23a8ddb0b30ae60cfdf696026dba4e06e2d`. Public `main` at inspection:
`71ac2a846fe2112393c672cac4939234f27abdf3`.

## Existing branch review

Eight existing preparatory commits separate the branch from `main`. The
executable/package changes are the `0.1.1` version declaration, additive
decision-card headings/checklist, and distribution verification against the
declared project version. The rest is practitioner/release guidance. The
assessment, schemas, blocker IDs, scoring, and exit contract are unchanged by
that range and by this integration. Existing canonical report bytes are unchanged.

## Delivered files and behavior

- `scripts/export_promptfoo_v1.py`: experimental pinned JSON producer with
  explicit identities, authoritative project cases, observations, V1 manifests,
  digests, pre-publication validation, and overwrite refusal.
- `scripts/run_promptfoo_demo.py`, `examples/integrations/promptfoo/`: a real
  `0.123.1` export from a synthetic provider, hash provenance, offline pass/block
  comparison, and consumer-repository workflow template.
- `scripts/review_evidence_ci.sh`, `.github/workflows/ci.yml`: saved diagnostics,
  upstream/blocked/error exit propagation, installed-wheel integration smoke,
  verified package checksums/source SHA, and CI artifact upload.
- `tests/test_promptfoo_producer.py`, `tests/test_promptfoo_ci.py`: success,
  assertion failure, execution error, missing observations/identity, malformed
  exports, duplicate/conflicting mappings, reproducibility, rollback on write
  failure, invalid evidence, and `tee` failure coverage.
- `README.md`, `docs/installation.md`, `docs/00_getting_started_for_practitioners.md`,
  `docs/integrations/promptfoo.md`, `docs/integrations/github-actions.md`: aligned
  first experience, conversion/tutorial answers, CI installation, and V1 limits.
- `.github/repository-metadata.json`, `.github/ISSUE_TEMPLATE/adoption_feedback.yml`,
  `docs/development/adoption-validation.md`, `docs/development/discovery-baseline.json`,
  `docs/development/discovery-validation.md`: prepared metadata, actual Day 1
  search/traffic baseline, and independent-trial intake. Live metadata is unchanged.
- `CHANGELOG.md`, `docs/releases/0.1.1.md`, `docs/architecture/code-map.md`: release
  candidate text, handoff instructions, and navigation.

## Local validation

Host: macOS ARM64, Python 3.12. Final focused producer checks: **36 passed**;
CI helper checks and distribution/version checks also passed. Final broader
pytest with four workers: **789 passed**. Ruff check/format, scoped mypy,
Bandit, compileall, Markdown links, and `git diff --check` passed.

The initial dependency audit found vulnerabilities in existing development
tools `pip` and `urllib3`. Updating them to `26.2.1` / `2.8.0` made the audit
pass with no known dependency vulnerabilities. OpenEvalGate itself is skipped
by that database because it is not on PyPI. Production dependency declarations
were not changed; CI now upgrades pip before its audited development install.

Executed the consumer workflow's command block with a simulated upstream
process and actual producer/CLI: success exits `0`; upstream execution error,
export error, invalid project, and blocked review each exit `1`, retaining
diagnostics. The raw format fixture itself came from actual Promptfoo `0.123.1`
execution, not from the upstream simulation. Workflow YAML and Bash syntax pass.
The final installed-wheel Python block from CI also runs successfully locally.

Both wheel and sdist were built from the same final package source, inspected,
and installed in separate clean environments outside the checkout. The wheel
reproduced all four canonical reports byte-for-byte; the offline producer/demo
and CI helper returned `0` / `1` as expected. Identical demo CSVs were verified.
Candidate `SHA256SUMS` was checked successfully.

Fresh environment + no-cache source installation + first decision card +
offline Promptfoo demo took **7.43 seconds** in a local source snapshot.
Network Git clone and installing Python itself are excluded. This is a local
measurement, not a universal installation-time guarantee.

## Pending release and adoption

Candidate packages are local **uncommitted review builds**, not exact-tag
artifacts. After explicit commit/push authorization, run GitHub's Python matrix,
review/merge, build from the same clean `v0.1.1` tag commit, and attach the
verified wheel/sdist/checksums using [release text](../releases/0.1.1.md).
No commit, push, tag, or Release publication was performed in this run.

The experiment supports only the pinned export/observation contract and does
not independently verify tool traces or control effectiveness. V1 stale/expired
authorization enforcement remains incomplete, as explicitly accepted for this
scope. No core contract or production dependency was changed.

Three non-maintainer invitations, two own-project reports, one real CI adoption,
and the Day 14 search/AI citation observation remain pending. No independent
trial, search growth, or AI citation success is claimed by these local checks.
