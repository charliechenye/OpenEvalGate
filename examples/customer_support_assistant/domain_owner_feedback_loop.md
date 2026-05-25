# Domain Owner Feedback Loop

| Field | Value |
| --- | --- |
| Domain area | Refund eligibility and escalation policy |
| Domain owner | Support Operations |
| Feedback source | support escalation |
| Observed behavior | Candidate assistant handled repeated refund history politely but did not escalate. |
| Expected behavior | Repeated refund history should route to human review before compensation is discussed. |
| Why current behavior is wrong or risky | It can reward abuse patterns and create expectations that support cannot honor. |
| Example user trace / synthetic case | `refund_abuse_history_002` |
| Proposed golden eval case | Keep `refund_abuse_history_002` as regression case after fix. |
| Proposed policy update | Add repeated-refund threshold to compiled policy context. |
| Risk tier | high |
| Approval needed | Support Operations and Customer Policy |
| Regression risk | Medium; over-escalation may increase handle time. |
| Metrics to monitor | Recontact rate, refund leakage, escalation correctness, complaint rate |
| Owner | Support Operations |
| Status | approved |
| Date reviewed | 2026-05-25 |
