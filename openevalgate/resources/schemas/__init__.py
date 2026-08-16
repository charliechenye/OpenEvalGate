"""Runtime JSON Schema resources for provenance validation."""

from __future__ import annotations

import json
from importlib import resources
from typing import Any


MANIFEST_SCHEMA_NAME = "eval-run-manifest-v1.schema.json"
ARTIFACT_INDEX_SCHEMA_NAME = "eval-run-artifact-index-v1.schema.json"
REVIEW_CONTEXT_SCHEMA_NAME = "eval-run-review-context-v1.schema.json"
EVAL_CASES_SCHEMA_NAME = "eval-cases-v1.schema.json"
REVIEW_POLICY_SCHEMA_NAME = "review-policy-v1.schema.json"
ROUTING_POLICY_SCHEMA_NAME = "routing-policy-v1.schema.json"
ESCALATION_CONTRACT_SCHEMA_NAME = "escalation-contract-v1.schema.json"
EVAL_RESULTS_SCHEMA_NAME = "eval-results-v1.schema.json"
ACTION_RISK_MATRIX_SCHEMA_NAME = "action-risk-matrix-v1.schema.json"
CLI_OUTPUT_SCHEMA_NAME = "cli-output-v1.schema.json"

CORE_SCHEMA_NAMES = (
    EVAL_CASES_SCHEMA_NAME,
    REVIEW_POLICY_SCHEMA_NAME,
    ROUTING_POLICY_SCHEMA_NAME,
    ESCALATION_CONTRACT_SCHEMA_NAME,
    MANIFEST_SCHEMA_NAME,
    ARTIFACT_INDEX_SCHEMA_NAME,
    REVIEW_CONTEXT_SCHEMA_NAME,
    EVAL_RESULTS_SCHEMA_NAME,
    ACTION_RISK_MATRIX_SCHEMA_NAME,
    CLI_OUTPUT_SCHEMA_NAME,
)


def read_schema_bytes(name: str) -> bytes:
    """Read a packaged schema resource by filename."""

    return resources.files(__package__).joinpath(name).read_bytes()


def load_schema(name: str) -> dict[str, Any]:
    """Load a packaged schema resource as JSON."""

    return json.loads(read_schema_bytes(name).decode("utf-8"))
