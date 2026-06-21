from __future__ import annotations

from importlib.metadata import version

import pytest

import openevalgate
from openevalgate.cli import main
from openevalgate.version import DISTRIBUTION_NAME


def test_public_version_matches_installed_distribution_metadata() -> None:
    assert openevalgate.__version__ == version(DISTRIBUTION_NAME)


def test_cli_version_uses_installed_distribution_metadata(
    capsys: pytest.CaptureFixture[str],
) -> None:
    installed_version = version(DISTRIBUTION_NAME)

    with pytest.raises(SystemExit) as exc_info:
        main(["--version"])

    assert exc_info.value.code == 0
    assert capsys.readouterr().out == f"openevalgate {installed_version}\n"
