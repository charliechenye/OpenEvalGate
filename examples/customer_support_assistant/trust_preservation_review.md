# Trust Preservation Review

| Question | Answer |
| --- | --- |
| What user trust does this assistant depend on? | Users must believe refund answers are honest, policy-grounded, and not designed to block help. |
| What would break that trust? | Unsupported refund promises, escalation blocking, ignoring emotional intensity, or blaming merchants without evidence. |
| What failures would users remember? | Being promised compensation and later denied, or being kept in automation when asking for human help. |
| What failures would cause platform-level damage? | Unauthorized compensation, safety escalation failure, or repeated complaints that automation hides policy nuance. |
| What short-term metric could mislead us? | Containment, because a contained refund session can still create recontact or complaint escalation. |
| What long-term metric protects the user relationship? | Durable resolution, recontact rate, complaint rate, and trust/sentiment for refund journeys. |
| How are tail risks bounded? | P0 checklist, high-risk evals, deterministic action gates, output critic, and human approval. |
| How does the system recover from mistakes? | Escalate, record failed case, add regression eval, update policy context, and rollback automation route if needed. |
| How does the system escalate gracefully? | It explains that a specialist is needed and passes order state, policy version, failed gate, and proposed route. |
| What evidence says users should trust this automation? | Golden eval coverage, action risk matrix, output critic rubric, escalation design, eval results, and launch gate signoff. |
