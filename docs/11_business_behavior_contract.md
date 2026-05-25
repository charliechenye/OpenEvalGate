# Business Behavior Contract

Agent behavior is a business contract, not an engineering guess.

Engineering builds the system. Product defines architecture and tradeoffs. Business, operations, policy, trust, safety, legal, and compliance owners define expected behavior.

Golden evals are the operating contract between business intent and agent execution.

## Why Golden Evals Matter

PRDs often describe goals. Golden eval cases describe behavior. They translate business intent into testable examples that the assistant must handle before launch.

Business owners should review eval cases, not just PRDs. A refund policy owner, support operations leader, compliance reviewer, or abuse specialist can often spot failure modes that a central AI team will miss.

## Contract Examples

- Compensation policy: when an assistant may recommend a credit, refund, or apology.
- Refund eligibility: what context must be checked before promising compensation.
- Escalation thresholds: when automation should stop and a human should decide.
- Compliance boundaries: what the assistant must refuse, escalate, or block.
- Abuse patterns: what user behavior indicates gaming, fraud, or unsafe automation pressure.

## Launch Readiness Impact

A system is not launch-ready until the relevant business owners agree that expected behavior, unacceptable behavior, tool permissions, and escalation thresholds are represented in the golden eval set.
