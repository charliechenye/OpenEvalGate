# Two-week engineering adoption validation

The goal is to discover whether an engineer can review their own Agent change,
not to count stars or synthetic demos. The maintainer invites three engineers
who do not maintain OpenEvalGate. Invitations and external user trials have
not been performed by the coding agent.

## Trial protocol

Give each engineer the published commit, [installation](../installation.md),
and [Promptfoo tutorial](../integrations/promptfoo.md). Ask them to:

1. Install and reach the offline decision card; record elapsed time and errors.
2. Use their own Promptfoo `0.123.1` export, map case/trial/candidate identities,
   and replace synthetic control claims with team-owned evidence.
3. Generate a report and explain its recommendation, blockers, and next action.
4. If feasible, use the consumer workflow on an actual project change. Capture
   the run URL, exit behavior, and artifacts, including a blocked/error case.

Collect [adoption feedback](../../.github/ISSUE_TEMPLATE/adoption_feedback.yml)
or a private/redacted record with the same fields. Do not publish private traces.
Record the first failing command and the time spent on installation, mapping,
control completion, and report interpretation. Observe the trial before helping
so we can distinguish self-service success from maintainer-assisted success.

## Evidence ledger

| Trial | Independent engineer | Own-project report | Actual CI | Traceable feedback | Current state |
| --- | --- | --- | --- | --- | --- |
| A | Pending invitation | Pending | Pending | Pending | Not started |
| B | Pending invitation | Pending | Pending | Pending | Not started |
| C | Pending invitation | Pending | Pending | Pending | Not started |

Acceptance: two engineers produce reports from their own projects; one uses an
actual CI job; each counted outcome has shareable or privately reviewable proof.
A maintainer demo, clone, download, or synthetic fixture does not meet this bar.
Fix the most frequent observed obstacle first; count occurrence by independent
trial rather than repeated messages from one person. Do not invent feedback.

## GitHub content and discovery

[repository-metadata.json](../../.github/repository-metadata.json) is the prepared
description/topic draft. Apply it with the published content; it has not been
applied to the live repository by this change. Agent release review, Promptfoo
CI, rollback, and human escalation are keyword hypotheses with unvalidated
search volume. Use [discovery validation](discovery-validation.md) to compare
the same ten questions on Day 1 and Day 14.

The GitHub-only acceptance is clear answers, reachable installation/tutorial
links, executable examples, and accurate claims/citations. GitHub controls
crawling and page metadata. Search visibility and AI citations are measured
outcomes, not guarantees or substitutes for engineering adoption.
