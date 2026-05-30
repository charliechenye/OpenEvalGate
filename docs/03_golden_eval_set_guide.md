# Golden Eval Set Guide

The golden eval set is the behavioral PRD for a GenAI system. It defines what the assistant must do, must not do, when it should use tools, and when it should escalate.

For a step-by-step practitioner workflow, see the [Golden Eval Set Playbook](playbooks/golden-eval-set-playbook/README.md).

## Case types

- **Historical production:** Real cases from support logs, sales chats, tickets, reviews, or pilot traffic.
- **Synthetic boundary:** Designed cases that sit near policy, eligibility, or safety thresholds.
- **Fresh drift sample:** Recent production requests that reveal changing user behavior, policy changes, or product drift.
- **Adversarial:** Requests that pressure the assistant into unsafe, ungrounded, or unauthorized behavior.
- **Regression:** Cases that previously failed or represent critical baseline behavior.

## What every case should prove

Every case should identify the user request, relevant context, retrieved context, risk tier, expected behavior, unacceptable behavior, expected tool behavior, expected route, grading rubric, policy reference, owner, and review date.

The eval case should be understandable to product, engineering, and trust/safety reviewers without reading the prompt.

## How outputs feed back

OpenEvalGate V1 does not call candidate models. Run the candidate assistant system in your eval platform or internal harness, then save the results back into the project.

Recommended loop:

1. Curate `eval_cases.yaml`.
2. Run each case against the candidate assistant externally.
3. Save one row per case result in `eval_results.csv`.
4. Save important observed outputs under `eval_runs/<run_id>/`.
5. Regenerate the launch readiness report.
6. Convert failures into new eval cases, model arena notes, output critic updates, launch gate mitigations, or rollback criteria.

The result row is the bridge between "we have a golden eval set" and "we know how the candidate system behaved."

## Coverage expectations

A launch-ready eval set should include common requests, high-frequency workflows, high-risk boundary cases, known abuse patterns, escalation cases, stale or missing context cases, and fresh drift samples.
