# Model Arena Guide

Public benchmarks are useful background information. They do not tell you which model should power your product.

An internal model arena compares candidate models against your golden eval set, your latency target, your cost target, and your safety requirements.

## What to compare

- Golden eval pass rate.
- Grounding and policy alignment.
- Escalation judgment.
- Tool/action safety.
- Latency distribution.
- Cost per request.
- Failure mode severity.

## Model garden

A model garden is the set of models your team can realistically operate. It should include strong frontier models, efficient smaller models, and fallback options. The best production model is the one that meets product behavior, safety, latency, cost, and operational constraints.

## Decision rule

Do not select a model because it wins a generic benchmark. Select it because it passes your launch gates with acceptable cost and latency.
