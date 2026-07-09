# Automation Boundary Matrix

| Risk | Confidence | Route | Example | Required controls | Human role | Eval coverage |
| --- | --- | --- | --- | --- | --- | --- |
| Low | High | automate | Explain a verified invoice | Account and invoice lookup | None | invoice_explanation_001 |
| Medium | Low | clarify | Account or subscription is ambiguous | Ask one targeted verification question | None | missing_account_context_002 |
| High | High | approval | Cancellation or refund exception | Policy check, checkpoint, approval | Billing reviewer | cancellation_exception_003 |
| High | Low | escalate | Account-takeover signal | Pause sensitive actions, security route | Security specialist | account_takeover_004 |
| Prohibited | Any | block | Bypass authentication or payment controls | Deterministic block and audit event | Incident review if repeated | authentication_bypass_005 |
