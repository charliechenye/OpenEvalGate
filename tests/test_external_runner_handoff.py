from pathlib import Path

import yaml

from openevalgate.provenance import RunIdentityStatus, inspect_run_identity


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "spec" / "fixtures" / "provenance" / "v1" / "langchain-external-runner"


def test_external_runner_fixture_is_valid_without_framework_dependency() -> None:
    manifest = yaml.safe_load((FIXTURE / "run_manifest.yaml").read_text(encoding="utf-8"))

    assert manifest["producer"] == {
        "id": "internal-langchain-eval-exporter",
        "version": "1.4.0",
    }
    assert manifest["evaluation"]["framework"] == {"id": "langchain", "version": "0.3.0"}
    assert inspect_run_identity(FIXTURE).status == RunIdentityStatus.COMPLETE
