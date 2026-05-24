# Golden Eval Set Guide

The golden eval set is the behavioral PRD for a GenAI system. It defines what the assistant must do, must not do, when it should use tools, and when it should escalate.

## Case types

- **Historical production:** Real cases from support logs, sales chats, tickets, reviews, or pilot traffic.
- **Synthetic boundary:** Designed cases that sit near policy, eligibility, or safety thresholds.
- **Fresh drift sample:** Recent production requests that reveal changing user behavior, policy changes, or product drift.
- **Adversarial:** Requests that pressure the assistant into unsafe, ungrounded, or unauthorized behavior.
- **Regression:** Cases that previously failed or represent critical baseline behavior.

## What every case should prove

Every case should identify the user request, relevant context, retrieved context, risk tier, expected behavior, unacceptable behavior, expected tool behavior, expected route, grading rubric, policy reference, owner, and review date.

The eval case should be understandable to product, engineering, and trust/safety reviewers without reading the prompt.

## Coverage expectations

A launch-ready eval set should include common requests, high-frequency workflows, high-risk boundary cases, known abuse patterns, escalation cases, stale or missing context cases, and fresh drift samples.
