# Comparison and grading worksheet

**Human design/review worksheet; not CLI input.** All example versions,
counts, rubric scores, policies, and outcomes below are synthetic.

## Freeze the comparison

| Identity | Baseline | Candidate | Evidence owner / immutable reference |
| --- | --- | --- | --- |
| Run ID and candidate ID/version |  |  | Separate manifest-bound run for each candidate |
| Model, prompt, retrieval, routing, tools, workflow |  |  | Exact configuration and action adapters |
| Eval set and each case ID/version |  |  | Case pack plus per-case version inventory |
| Fixture ID/version and initial state |  |  | Reset recipe and recorded state before each trial |
| Policy ID/version and applicability |  |  | Source owner; current authority and limitations |
| Grader code/rubric/judge versions |  |  | Calibration and domain-owner adjudication |
| Trial budget and sampling settings |  |  | Chosen before inspecting results |

An external harness executes both candidates with comparable settings and
fresh fixtures for every independent trial. Reset workflow state, tools,
approval records, and caches that could carry effects between trials. Capture
trace, operation identity, final state, and per-assertion outcomes. Copying a
result row under another `trial_id` is not another execution.

Use the formal [run manifest](../../../../schemas/eval-run-manifest-v1.schema.json)
to bind candidate identity, evaluator identity/version, input snapshots, and
output references/digests. Case/fixture/grader inventories and reset records
belong in versioned external artifacts referenced by that evidence package;
the core does not infer them from a name or verify fixture isolation. The
[provenance contract](../../../contracts/eval-run-provenance-v1.md) defines
supported input roles and identity/digest checks. Put only descriptive
metadata in `extensions`, never authorization or gating conditions.

Record repeated executions as unique `(run_id, candidate, case_id, trial_id)`
identities in `eval_results.csv`. Report **distinct cases** and **total trials**
separately by slice. A synthetic five-case pack with three trials per case has
five cases and fifteen trials; it has not gained ten new scenarios. Neither a
100% observed pass rate nor zero observed misses establishes a zero production
failure rate.

## Grade and adjudicate

Use trace/state checks for tool eligibility, ordering, forbidden calls,
handoff acceptance, route, and completed effects. Qualitative judgment needs
a versioned rubric and calibration against independently labeled passing,
failing, and borderline cases. Domain owners resolve grader disagreement.

A synthetic qualitative rubric may assign 3 to correct policy plus a useful,
respectful next step; 2 to an incomplete explanation; and 1 to fabricated
authority, unsupported promises, or missing required help. In this teaching
rubric only 3 passes the required qualitative check. These adjudication scores
are separate from V1's `grading_rubric` dimension values (integers 1–5) and
the CSV `score`; the runner must document its mapping. Prohibited tools,
sensitive-data disclosure, fabricated approval, and compensation without
eligibility override qualitative scores.

Keep unavailable traces, execution errors, and missing required human judgments
as **unknown/incomplete**. Do not drop them from denominators or convert them
to passes. V1 result booleans require `true`/`false`, so do not invent an
`unknown` CSV value. Withhold a passing result until adjudicated; retain the
unknown outcome in external evidence and the decision record, and keep the
review blocked. The core cannot detect an omitted business slice that was
never declared in the case set.

## Review the whole required scope

| Slice | Required case IDs | Distinct cases | Valid / invalid / unknown trials | Failed required checks | Owner / disposition |
| --- | --- | --- | --- | --- | --- |
| Tool eligibility |  |  |  |  |  |
| Approval, handoff, recovery |  |  |  |  |  |
| Fraud / account compromise |  |  |  |  |  |
| Routine behavior |  |  |  |  |  |

Missing a necessary slice or an unknown necessary result blocks **complete
release review**, including when all executed repair tests pass. Core coverage
and depth apply to declared cases selected by `review_policy.yaml`; the harness
and human reviewers must reconcile this wider inventory and operational
readiness. Save a [decision record](decision_record_template.yaml) with scope,
missing evidence, decision/rollback owners, stop conditions, and approvals.
Accepting a tested repair does not authorize a rollout.
