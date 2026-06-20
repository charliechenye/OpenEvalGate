# OpenEvalGate Iteration Roadmap

This directory converts the public-readiness audit into bounded implementation iterations.

## Roadmap Structure

| Iteration | Primary outcome | Exit condition |
| --- | --- | --- |
| [Iteration 1](iteration-01-correctness-and-release-semantics.md) | Make launch decisions semantically correct and evidence-backed. | A high documentation score can no longer conceal failed observed behavior or critical controls. |
| [Iteration 2](iteration-02-public-repository-readiness.md) | Make the repository reproducible, attributable, secure, and easy to adopt. | A new contributor can install, run, understand, and cite the project from a clean environment. |
| [Iteration 3](iteration-03-adoption-and-external-validation.md) | Establish independent use, feedback, and ecosystem relevance. | External practitioners have applied the framework and produced verifiable feedback or contributions. |
| [Public Launch Checklist](public-launch-checklist.md) | Make the visibility decision explicit. | Every P0 launch condition is satisfied. |

The top-level [TODO.md](../../TODO.md) is the master backlog.

## Execution Rules

Every implementation task should include:

- A named owner.
- A linked issue or pull request.
- Acceptance criteria.
- Tests or reproducible validation steps.
- Documentation changes when public behavior changes.
- A changelog entry for user-visible behavior.

Do not mark a task complete because a file exists. Mark it complete only when its acceptance criteria pass.

## Priority Policy

### P0

A correctness, safety, reproducibility, attribution, or public-release blocker. P0 work must be completed before the repository becomes public.

### P1

Work required for a strong public launch but not required to prevent misleading or unsafe output.

### P2

Adoption, ecosystem, and expansion work that should follow a credible technical foundation.

## Public Communication Rule

Public documentation should explain practitioner value, implementation boundaries, and verifiable evidence. It should not discuss personal immigration strategy or make unsupported claims about industry influence.

Independent pilots, citations, presentations, and endorsements should be tracked in a separate evidence log. Sanitized case studies may be added to the repository when participants approve publication.
