# Golden Eval Set Review Agenda

Use this agenda before the first launch gate and after major model, prompt, retrieval, tool, policy, or workflow changes.

## 1. Product Scope Recap

- What system are we evaluating?
- What user intents are in scope?
- What behaviors must the system demonstrate?
- What behaviors are explicitly out of scope?

## 2. Coverage Review

- Do we cover top production intents?
- Do we cover high-risk boundary cases?
- Do we cover known historical failures?
- Do we cover tool-using scenarios?
- Do we cover tool-prohibited scenarios?
- Do we cover escalation-required cases?
- Do we cover refusal/block cases?
- Do we cover fresh production drift samples?

## 3. Expected Behavior Review

- Are expected behaviors specific enough?
- Are must-do and must-not-do requirements clear?
- Are policy references correct?
- Are ambiguous cases assigned to owners?
- Would two reviewers grade the case the same way?

## 4. Scoring Review

- Which checks are deterministic?
- Which checks are rubric-based?
- Which checks use human review?
- Which checks inspect traces or tool calls?
- Which high-risk cases should not rely only on model judgment?

## 5. Release Gate Review

- Which slices block launch?
- Which slices can ship with monitoring?
- What thresholds are acceptable?
- Who approves exceptions?
- What would trigger rollback?

## 6. Maintenance Review

- Who owns eval set updates?
- How often are fresh production samples reviewed?
- How are incidents converted into eval cases?
- How are cases versioned?
- Which cases are stale and should be retired or updated?

## Questions To Force Clarity

- Which eval case would we be most embarrassed to fail in production?
- Which case is most likely to be hidden by aggregate accuracy?
- Which case requires deterministic enforcement rather than model judgment?
- Which case would damage user trust even if the final answer sounds plausible?
- Which case has unclear ownership?
