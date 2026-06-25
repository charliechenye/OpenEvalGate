# OpenEvalGate

Local release assurance for production AI assistants and agents.

[![CI](https://github.com/charliechenye/OpenEvalGate/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/charliechenye/OpenEvalGate/actions/workflows/ci.yml?query=branch%3Amain)
[![Python 3.10-3.13](https://img.shields.io/badge/python-3.10--3.13-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

OpenEvalGate is an open-source, local release-assurance framework for production AI assistants and agents. It deterministically assesses declared review evidence and produces a bounded launch recommendation for the requested review stage.

It helps teams assemble and review evidence for three questions:

1. **Expected behavior:** Does observed behavior match a business-owned contract?
2. **Safe stopping boundaries:** Does autonomy end at the right point, with the right human destination and context?
3. **Release evidence:** Do eval results, critical controls, mitigations, owners, and rollback plans support the requested review stage?

OpenEvalGate does not run the candidate system. Teams run evaluations with their existing tools, record the results locally, and use the CLI to validate the evidence package, identify blockers, and generate a release-assurance report.

## The Production Problem

A demo or model benchmark can show that a system succeeded once. A release review must also examine whether it behaves consistently within policy, stops safely, transfers work correctly, and leaves operators able to observe and roll back the system.

```text
Intent + context + policy + risk + user-friction signals
                          |
                          v
              Escalation Control Surface
                          |
                          v
      Resolve | Clarify | Act | Approval | Escalate | Refuse
                               |
                               v
        Live handoff | async case | specialist review
              approval queue | safe fallback
```

OpenEvalGate assesses both under-escalation, which can create unsafe autonomy or false containment, and over-escalation, which can waste human capacity and increase user effort.

## Reference Scenarios

These repository-authored scenarios are synthetic and illustrative. They are not external production deployments, independent adoption evidence, or external validation of OpenEvalGate.

| Domain | Safe stopping boundary | Human path evidence | Failure demonstrated |
| --- | --- | --- | --- |
| [Customer support](examples/customer_support_assistant/generated_launch_report.md) | Refund approval, repeated failure, fraud signal, dependency outage | Live handoff, approval queue, async case, fraud operations | Under-escalation, wrong destination, false containment |
| [Presales](examples/presales_assistant/generated_launch_report.md) | Discount authority, roadmap claims, legal/security commitments | Account-owner follow-up, pricing approval, specialist review | Unsupported commitment, late escalation |
| [Education](examples/education_assistant/generated_launch_report.md) | Graded work, learner safety, accommodation exception | Instructor review, safety route, accessibility approval | Missing handoff context, unnecessary escalation, failed resume |

See the [examples index](examples/README.md) for scenario purposes, inputs, and reproduction commands.

## Quickstart

New to the repository? Start with [Getting Started for Practitioners](docs/00_getting_started_for_practitioners.md).

```bash
python -m pip install -e ".[dev]"
openevalgate --version
openevalgate validate examples/customer_support_assistant/eval_cases.yaml
openevalgate check examples/customer_support_assistant/
openevalgate report examples/customer_support_assistant/ \
  --output examples/customer_support_assistant/generated_launch_report.md
```

The generated report separates evidence completeness from observed behavior and critical controls:

```text
Structured escalation contract: valid
Destination SLA coverage: 100%
Required-escalation recall: 67%
Over-escalation rate: 33%
Destination accuracy: 33%
Context-preservation rate: 67%
Hard blocker: critical_escalation_regression
Recommendation: Not ready
```

High evidence completeness cannot override a high-risk case that failed to stop or reached the wrong human destination.

## How It Works

1. Define assistant scope, unsupported uses, and business-owned behavior.
2. Build golden eval cases from expected, boundary, adversarial, tail-risk, regression, and drift scenarios.
3. Define action risks, automation boundaries, human escalation, observability, rollback, and ownership.
4. Run the candidate assistant externally using an eval runner, internal harness, or manual review.
5. Save observed results in `eval_results.csv` and optional outputs in `eval_runs/`.
6. Validate the project and generate a local report.
7. Review the recommendation, blockers, mitigations, and required next actions.

The framework distinguishes:

- evidence completeness;
- behavioral-evidence status;
- critical-control status;
- maximum permitted review stage;
- final bounded recommendation.

The complete gate list, scoring weights, evidence bands, and hard-gate semantics are documented in [Launch Gates and Evidence Completeness Scoring](docs/launch-gates-and-evidence-scoring.md). Review modes, selected-run coverage, and controlled-launch behavioral sufficiency are documented in [Review Modes and Behavioral Sufficiency](docs/review-modes.md).

## Runtime Eval-Run Identity

The [Eval-Run Provenance Contract v1](docs/contracts/eval-run-provenance-v1.md) defines how a small `run_manifest.yaml` can wrap an existing OpenEvalGate-compatible `eval_results.csv`. Existing compatible CSVs do not need new provenance columns.

OpenEvalGate classifies selected eval-run identity as `complete`, `missing`, or `invalid`. `complete` means the run, candidate, evaluator, result CSV, output paths, recognized output metadata, and declared artifact-index identities are coherent. It does not mean the run lifecycle is complete, rows exist, the run passed, digests were verified, evidence is fresh or recent, behavioral evidence is sufficient, or controlled launch is authorized.

Projects may omit empirical results while documenting controls. Once a conventional `eval_results.csv` is present, an authoritative `run_manifest.yaml` is required.

A manifestless result file is surfaced as a provenance validation failure, while its rows are excluded from row validation, summaries, metrics, coverage, behavioral invariants, behavior-derived blockers, and launch authorization. No new CSV columns are required.

Artifact indexes remain optional. Digest verification, verified assurance, freshness and recency comparison, automatic provenance initialization, and `review_context.yaml` enforcement remain deferred.

Minimal manifest:

```yaml
schema_version: "1"

run:
  id: run_001
  status: complete

candidate:
  id: candidate_name
  version: candidate_version

evaluation:
  kind: human
  evaluator:
    id: human_review

outputs:
  results:
    path: eval_results.csv
```

## Where OpenEvalGate Fits

OpenEvalGate complements eval runners, observability platforms, runtime controls, security tooling, and internal review systems.

```text
Business intent / policy / trust risk
        |
        v
OpenEvalGate review artifacts and declared controls
        |
        v
External eval runners, candidate systems, traces, and runtime tools
        |
        v
eval_results.csv, observed outputs, incidents, and control evidence
        |
        v
OpenEvalGate validation, blockers, and bounded recommendation
```

Eval and LLMOps tools execute tests, collect traces, monitor behavior, or enforce runtime policy. OpenEvalGate consumes their outputs through local artifacts and organizes that evidence for a defined release review. It does not require an official vendor integration.

See [Research Context and Adjacent Tools](docs/16_research_evidence_and_competitive_landscape.md) for conceptual relationships with external guidance and tooling.

## Core Primitives

- **Business behavior contract:** expected and unacceptable behavior owned by product and domain stakeholders.
- **Golden eval set:** product-specific behavior expressed as reusable test cases.
- **Tail-risk review:** explicit treatment of rare, high-impact failures.
- **Action-risk matrix:** classification of tool and action risks, including required human review.
- **Automation boundary:** decisions about resolution, clarification, approval, escalation, refusal, and blocking.
- **Human escalation contract:** destinations, service levels, payloads, fallbacks, and durable resume behavior.
- **Evidence completeness:** documentation and review coverage, kept separate from behavioral quality.
- **Hard blockers:** critical controls that can prevent advancement regardless of aggregate score.
- **Review modes:** documentation, shadow-launch, and controlled-launch assessments with different evidence requirements.

For multi-agent systems, optional `routing_policy.yaml` evidence records fixed, adaptive, deterministic, and human paths per bounded workflow. A stronger model is not treated as an authorization or safety control.

## Who It Is For

- AI product managers and business or operations owners;
- ML, AI, and platform engineers;
- trust, safety, legal, compliance, and security reviewers;
- teams preparing a cross-functional review of an assistant or agent.

## Limitations and Non-Claims

OpenEvalGate is an early, pre-1.0 framework with practitioner-defined defaults and repository-authored synthetic examples.

- It does not execute candidate models, call LLM APIs, or evaluate live behavior by itself.
- It does not replace eval runners, observability systems, runtime guardrails, security controls, or organizational approval.
- It validates submitted artifacts and declared evidence; it does not independently verify that every claim in those artifacts is true, current, or complete.
- The current implementation validates core result identities, selected eval-run identity, expected-route consistency, duplicate identities, review timestamps, supplied output references, output identity metadata, artifact-index identity, and basic route-match derivation. It does not yet verify provenance digests, evidence freshness or recency, artifact-version pinning beyond declared runtime identity, enriched workflow-route claims, handoff claims, or every routing-policy and model-policy field.
- A recommendation is only as reliable as the quality, completeness, provenance, and freshness of the supplied evidence.
- A passing check, high evidence score, or bounded recommendation does not guarantee safe, reliable, compliant, or successful deployment.
- It does not certify compliance or provide legal, regulatory, security, or risk-management certification.
- References to NIST, ISO, OECD, OWASP, the EU AI Act, or other guidance describe conceptual relationships, not formal alignment, endorsement, partnership, or approval.
- References to external tools describe complementary workflows, not official integrations or vendor partnerships unless explicitly documented by both parties.
- Repository-authored scenarios are not external validation, independent adoption evidence, or proof of production performance.
- The scoring weights and thresholds are initial practitioner defaults, not scientific constants or a universal industry standard.
- Teams remain responsible for system design, evidence quality, runtime controls, monitoring, authorization, and release decisions.

## Templates and Playbooks

The repository includes local Markdown, YAML, and CSV templates for assistant scope, behavior contracts, eval cases and results, action risk, automation boundaries, escalation, output review, observability, metrics, launch gates, and reports.

Practitioner playbooks include:

- [Golden Eval Set Playbook](docs/playbooks/golden-eval-set-playbook/README.md)
- [Synthetic Boundary Case Guide](docs/17_synthetic_boundary_case_guide.md)
- [Routing Playbook](docs/playbooks/routing/README.md)
- [Human Escalation Playbook](docs/playbooks/human-escalation-playbook/README.md)

## Repository Structure

```text
docs/          Guides, methodology, and playbooks.
templates/     Copyable review artifacts.
examples/      Synthetic, illustrative assistant scenarios.
openevalgate/  Deterministic local Python CLI.
tests/         Schema, policy, assessment, and report tests.
```

## Maintainer, Citation, and Contribution

OpenEvalGate was created and is maintained by [Chenye Zhu](https://chenyezhu.com/) and is released under the [MIT License](LICENSE).

For references, use [CITATION.cff](CITATION.cff). Release history is in [CHANGELOG.md](CHANGELOG.md). Contributions should follow [CONTRIBUTING.md](CONTRIBUTING.md) and the [Code of Conduct](CODE_OF_CONDUCT.md). Report suspected vulnerabilities according to [SECURITY.md](SECURITY.md).

Keep the CLI small, deterministic, local-first, and dependency-light.
