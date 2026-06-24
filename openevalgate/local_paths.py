"""Portable local evidence path validation."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath


_URI_OR_DRIVE_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")


@dataclass(frozen=True)
class LocalPathValidationResult:
    path: Path | None
    error: str | None


def resolve_local_evidence_path(
    base_dir: str | Path,
    serialized_path: str,
    *,
    allowed_root: str | Path | None = None,
    require_file: bool = True,
) -> LocalPathValidationResult:
    """Resolve a safe slash-serialized local evidence path."""

    if not isinstance(serialized_path, str) or not serialized_path:
        return LocalPathValidationResult(None, "unsafe")
    if "\x00" in serialized_path:
        return LocalPathValidationResult(None, "missing")
    if "\\" in serialized_path:
        return LocalPathValidationResult(None, "unsafe")
    if serialized_path.startswith(("/", "//")):
        return LocalPathValidationResult(None, "unsafe")
    if _URI_OR_DRIVE_PATTERN.match(serialized_path):
        return LocalPathValidationResult(None, "unsafe")

    segments = serialized_path.split("/")
    if any(segment == "" for segment in segments):
        return LocalPathValidationResult(None, "unsafe")
    if any(segment in {".", ".."} for segment in segments):
        return LocalPathValidationResult(None, "traversal")

    pure = PurePosixPath(serialized_path)
    if pure.is_absolute():
        return LocalPathValidationResult(None, "unsafe")

    base = Path(base_dir)
    allowed = Path(allowed_root if allowed_root is not None else base).resolve(strict=False)
    candidate = base
    for segment in pure.parts:
        candidate = candidate / segment
        try:
            if candidate.is_symlink():
                return LocalPathValidationResult(None, "symlink")
        except OSError:
            return LocalPathValidationResult(None, "symlink")

    try:
        resolved = base.joinpath(*pure.parts).resolve(strict=False)
    except (OSError, RuntimeError, ValueError):
        return LocalPathValidationResult(None, "missing")

    try:
        resolved.relative_to(allowed)
    except ValueError:
        return LocalPathValidationResult(None, "escape")

    if require_file and not resolved.is_file():
        return LocalPathValidationResult(None, "missing")
    return LocalPathValidationResult(resolved, None)
