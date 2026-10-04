# GitHub SEO/AEO observation protocol

Day 1 baseline: **2026-10-04 UTC** (2026-10-03 in Los Angeles), before this
change is published. Repeat on Day 14, **2026-10-17 UTC**, using the exact queries
in [discovery-baseline.json](discovery-baseline.json). No future result is recorded.

## Search method and baseline

The baseline uses the available web-search tool, one query per call, with no
domain or recency filter. `repository_returned` means the returned result set
contains a URL under `github.com/charliechenye/OpenEvalGate`. It is not a Google
rank, an exhaustive indexing test, or a count of organic visits. The file saves
sample returned URLs so the observation can be inspected. Search output changes
with engine, time, locale, and personalization; repeat with the same method and
record any differences.

This snapshot returned the repository for 3 of 10 queries: the brand name,
installation, and evidence freshness. It did not return the repository for the
six unbranded questions or `OpenEvalGate Promptfoo`. That is a starting point,
not evidence that this unpublished change improved discovery.

Authenticated GitHub traffic API returned 3 views / 3 unique visitors and
11 clones / 8 unique cloners for its 2026-09-19–2026-10-02 window. These may
include maintainer or automated activity and cannot establish independent
adoption or SEO attribution. They are saved as a dated snapshot, not live KPIs.

## Day 14 record

Copy the baseline structure to a dated observation file. Keep all ten queries,
the method, date, published commit, sample URLs, and whether the repository was
returned. Record GitHub traffic for its then-current window if access remains
available; do not compare overlapping windows as independent cumulative counts.

For any available AI search engine, ask the same questions and save engine/model,
time, answer, cited URLs, and accuracy. Evaluate these specific claims:

- supports only Promptfoo `0.123.1` under the experimental producer contract;
- consumes existing results; does not run candidate models in the core;
- expected route comes from project cases, actual route from harness observations;
- rollback/monitoring can block despite passing assertions;
- synthetic demos are not production/adoption proof;
- V1 freshness/expiry authorization is incomplete and approval remains team-owned.

Score each cited claim as correct, incorrect, or absent with evidence. Do not
use this assistant's own answer as an independent AI citation outcome. No
independent AI-search citation baseline was available in this run, so it is
recorded as **not measured**, not zero. Rankings/citations do not override the
[adoption acceptance criteria](adoption-validation.md).
