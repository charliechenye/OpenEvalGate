from pathlib import Path

from openevalgate.resources.schemas import (
    ARTIFACT_INDEX_SCHEMA_NAME,
    MANIFEST_SCHEMA_NAME,
    REVIEW_CONTEXT_SCHEMA_NAME,
    load_schema,
    read_schema_bytes,
)


ROOT = Path(__file__).resolve().parents[1]


def test_packaged_schemas_match_normative_sources_byte_for_byte() -> None:
    expected = {
        MANIFEST_SCHEMA_NAME: ROOT / "schemas" / MANIFEST_SCHEMA_NAME,
        ARTIFACT_INDEX_SCHEMA_NAME: ROOT / "schemas" / ARTIFACT_INDEX_SCHEMA_NAME,
        REVIEW_CONTEXT_SCHEMA_NAME: ROOT / "schemas" / REVIEW_CONTEXT_SCHEMA_NAME,
    }

    for name, source in expected.items():
        assert read_schema_bytes(name) == source.read_bytes()


def test_packaged_schema_loading_uses_package_resources() -> None:
    manifest = load_schema(MANIFEST_SCHEMA_NAME)
    artifact_index = load_schema(ARTIFACT_INDEX_SCHEMA_NAME)
    review_context = load_schema(REVIEW_CONTEXT_SCHEMA_NAME)

    assert manifest["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert artifact_index["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert review_context["$schema"] == "https://json-schema.org/draft/2020-12/schema"
