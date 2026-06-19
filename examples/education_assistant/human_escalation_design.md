# Human Escalation Design

## Boundary Summary

| Workflow | Resolve when | Clarify when | Escalate when | Approval required when | Refuse or block when | Owner |
| --- | --- | --- | --- | --- | --- | --- |
| Education integrity support | Request is for supported concept explanation or practice guidance grounded in course material. | Assessment status or learner intent is ambiguous. | Grading dispute, learner safety, accessibility, or policy exception needs staff judgment. | Instructor or staff must approve a hint, exception, or accommodation next step. | Learner asks for answer key, direct graded answer, or cheating assistance. | learning_product |

## Escalation Paths

| Escalation trigger | Boundary path | Human destination | User-facing handoff message | Human task payload | Minimum context passed | Priority level | SLA | Fallback path | Required human decision | Resume behavior | Feedback returned to system | Eval case coverage | Monitoring metric |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graded-work dispute | escalate | Instructor review | I need to route this to course staff so we respect the learning policy. | Learner request and course context. | Course ID, assessment type, policy boundary, proposed response. | medium | 1 business day | Course staff triage | allow hint / refuse / clarify / follow up | Agent resumes with approved guidance only | decision and reason | graded_dispute_escalation_003 | escalation correctness |
| Learner safety or crisis language | escalate | Learner safety review | I am going to route this for urgent support. | Safety review handoff. | Minimal relevant learner text, course context, safety trigger. | urgent | 30 minutes | Campus support protocol | safety handling decision | Agent stops normal tutoring path until safety route is complete | safety category only | learner_safety_escalation_004 | safety escalation latency |
| Accommodation or policy ambiguity | escalate | Accessibility policy review | This may need staff review so we apply the course policy correctly. | Accommodation or policy exception review. | Learner request, course context, policy conflict, prior assistant response. | high | 2 business days | Course staff triage | approve exception path / ask for documentation / route elsewhere | Agent provides only approved next step | policy decision and owner | accommodation_policy_ambiguity_005 | policy ambiguity rate |
| Direct graded answer request | refuse | None | I cannot provide the answer to a graded quiz, but I can help you understand the concept or practice a similar problem. | No human task unless the learner disputes the boundary. | Course policy and assessment type. | high |  | Instructor review if disputed | none | Offer allowed learning support | refusal category | graded_answer_request_001 | answer leakage rate |

## Durable State And Audit

| Requirement | Status | Notes |
| --- | --- | --- |
| Workflow checkpoint is created before handoff or approval | pass | Staff-review cases include course, assessment, and policy checkpoint. |
| Idempotency key prevents duplicate execution after resume | not_applicable | Assistant does not execute external actions in this example. |
| Handoff payload follows minimum-sufficient-context principle | pass | Safety path limits payload to relevant learner message and course context. |
| Reviewer identity and decision are recorded | partial | Instructor review owner exists; accessibility reviewer capture must be finalized. |
| Timeout behavior is defined | partial | Instructor and safety SLAs exist; fallback owner needs launch signoff. |
| Fallback destination is observable | partial | Course staff triage exists but dashboard is not complete. |
| Model, prompt, workflow, policy, and tool versions are captured | partial | Course policy version captured; prompt version evidence pending. |

## Launch Evidence

| Evidence | Linked artifact or case ID | Owner | Status |
| --- | --- | --- | --- |
| Under-escalation eval cases | graded_dispute_escalation_003, grade_dispute_semantic_009, learner_safety_escalation_004, learner_safety_semantic_010 | learning_product | present |
| Over-escalation eval cases | explain_photosynthesis_002, concept_explanation_semantic_007 | ai_quality | present |
| Explicit human request case | graded_dispute_escalation_003 | course_staff | present |
| Approval-required action case | accommodation_policy_ambiguity_005 | accessibility_services | present |
| Dependency failure or queue fallback case | course staff triage fallback | operations | planned |
| Human escalation gate in `launch_gate_review.md` | Human escalation gate | operations | partial |
