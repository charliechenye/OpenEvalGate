from pathlib import Path

from openevalgate.resources.schemas import (
    CORE_SCHEMA_NAMES,
    load_schema,
    read_schema_bytes,
)


ROOT = Path(__file__).resolve().parents[1]


def test_packaged_schemas_match_normative_sources_byte_for_byte() -> None:
    expected = {name: ROOT / "schemas" / name for name in CORE_SCHEMA_NAMES}

    for name, source in expected.items():
        assert read_schema_bytes(name) == source.read_bytes()


def test_packaged_schema_loading_uses_package_resources() -> None:
    for name in CORE_SCHEMA_NAMES:
        assert load_schema(name)["$schema"] == "https://json-schema.org/draft/2020-12/schema"
