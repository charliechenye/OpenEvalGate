"""Installed OpenEvalGate distribution version."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version


DISTRIBUTION_NAME = "openevalgate"

try:
    __version__ = version(DISTRIBUTION_NAME)
except PackageNotFoundError:
    __version__ = "0+unknown"
