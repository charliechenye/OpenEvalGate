# Observability Checklist

Observability is not launch readiness by itself. It is how the team learns whether launch assumptions remain true after users arrive.

## Minimum signals

- Request ID and response ID.
- User intent and supported use case.
- Retrieved context IDs and policy versions.
- Tool calls, action outcomes, and blocked actions.
- Output critic decision.
- Human escalation reason.
- User feedback.
- Latency and cost.
- Error and fallback path.
- Drift sample marker.

## Review cadence

Fresh drift samples should feed back into the golden eval set. Launch review should define who reviews samples, how often review happens, and what threshold triggers rollback or mitigation.

## Incident readiness

The team should know how to find the trace, identify the failed gate, pause the launch, notify owners, and add the incident case to the regression set.
