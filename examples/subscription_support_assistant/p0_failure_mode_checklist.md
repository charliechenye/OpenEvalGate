# P0 Failure Mode Checklist

| Failure mode | Worst outcome | Risk | Prevented by | Detected by | Escalated by | Blocked by | Eval coverage | Owner | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Unauthorized payment mutation | Account takeover or financial loss | prohibited | Authentication and action gate | Security audit event | Account security review | Deterministic block | authentication_bypass_005 | Trust and Safety | covered |
| Unapproved cancellation refund | Financial loss and false promise | high | Policy and approval checkpoint | Approval queue monitor | Billing Operations | Refund action gate | cancellation_exception_003 | Billing Policy | covered |
| Missed takeover escalation | Sensitive action proceeds under attack | high | Security signal filter | Security incident monitor | Security specialist | Sensitive-action pause | account_takeover_004 | Trust and Safety | covered |
