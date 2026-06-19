# Automation Boundary Matrix

| Risk level | Confidence level | Action route | Examples | Required controls | Human role | Eval coverage |
| --- | --- | --- | --- | --- | --- | --- |
| Low | High | automate | Concept explanation | Course material retrieval | None | explain_photosynthesis_002 |
| Low | High | automate | Semantically equivalent concept explanation | Course material retrieval | None | concept_explanation_semantic_007 |
| Low | Low | clarify | Assessment type is unknown | Ask whether work is graded or practice | None | assessment_context_missing_006 |
| Medium | Low | escalate | Ambiguous assessment context | Academic-integrity check | Instructor review | graded_dispute_escalation_003 |
| Medium | Low | escalate | Accommodation or policy ambiguity | Accessibility policy lookup | Accessibility or course staff review | accommodation_policy_ambiguity_005 |
| High | Low | escalate | Learner safety concern | Safety protocol trigger | Learner safety review | learner_safety_escalation_004 |
| Prohibited | Any | block | Answer-key or direct graded-answer request | Hard block | Review if disputed | graded_answer_request_001, graded_answer_semantic_008 |
