"""Runtime JSON Schema resources for provenance validation."""

from __future__ import annotations

import json
from importlib import resources
from typing import Any


MANIFEST_SCHEMA_NAME = "eval-run-manifest-v1.schema.json"
ARTIFACT_INDEX_SCHEMA_NAME = "eval-run-artifact-index-v1.schema.json"


def read_schema_bytes(name: str) -> bytes:
    """Read a packaged schema resource by filename."""

    return resources.files(__package__).joinpath(name).read_bytes()


def load_schema(name: str) -> dict[str, Any]:
    """Load a packaged schema resource as JSON."""

    return json.loads(read_schema_bytes(name).decode("utf-8"))
