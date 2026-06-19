# Education Study Assistant

**Assistant type:** education
**Launch owner:** Learning Product Team
**Review date:** 2026-05-23

## Purpose

Help learners understand course material, practice concepts, and find next study steps without completing graded work on their behalf.

## Supported Use Cases

| Use case | User intent | Success criteria | Required context | Owner |
| --- | --- | --- | --- | --- |
| Concept explanation | Learner asks for clarification. | Assistant explains using course-approved material. | Course unit and learning objective. | Learning Product |
| Practice hint | Learner asks for help on practice. | Assistant gives hints without direct answer leakage. | Assignment type and honor policy. | Learning Product |

## Workflow And Capability Allocation

| Workflow or subagent | Job | Risk tier | Model assignment | Mandatory controls | Fallback | Owner |
| --- | --- | --- | --- | --- | --- | --- |
| Concept tutor | Explain course concepts | low | fixed: provisional platform default | Course grounding and learner-level context | Instructor review | Learning Product |
| Academic integrity support | Refuse answer leakage and offer allowed help | high | fixed: provisional platform default | Integrity policy, answer-key block, output critic | Instructor review | Learning Product |
| Instructor review | Resolve graded-work disputes | medium | none: human workflow | Assessment context and durable handoff | Integrity support | Course Staff |
| Learner safety review | Handle urgent learner-safety signals | high | none: human workflow | Urgent specialist route and minimized context | Instructor review | Learner Safety |

## Unsupported Use Cases

| Unsupported request | Required behavior | Escalation path | Policy reference |
| --- | --- | --- | --- |
| Graded answer request | Refuse to provide direct answer and offer learning support. | Instructor review. | academic_integrity_v1 |
