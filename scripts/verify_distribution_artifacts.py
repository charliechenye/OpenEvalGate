"""Verify OpenEvalGate wheel and source-distribution contents."""

from __future__ import annotations

import argparse
import configparser
import re
import stat
import sys
import tarfile
import zipfile
from email.parser import Parser
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path, PurePosixPath
from typing import Iterable


DISTRIBUTION_NAME = "openevalgate"
FORBIDDEN_DIRECTORIES = {
    ".git",
    ".github",
    ".pytest_cache",
    ".test-tmp",
    "__pycache__",
    "build",
    "dist",
    "docs",
    "examples",
    "scripts",
    "tests",
}
SDIST_FORBIDDEN_DIRECTORIES = {
    ".git",
    ".pytest_cache",
    ".test-tmp",
    "__pycache__",
    "build",
    "dist",
}


class VerificationError(Exception):
    """Raised when a distribution artifact violates its contract."""


def _fail(artifact: str, path: str | Path, reason: str) -> None:
    raise VerificationError(f"{artifact}: {str(path)!r}: {reason}")


def normalize_archive_member(
    name: str,
    *,
    artifact: str,
) -> str:
    """Return a safe normalized POSIX member path."""
    if "\x00" in name:
        _fail(artifact, name, "archive member contains a NUL character")
    if "\\" in name:
        _fail(artifact, name, "archive member contains a backslash")
    if name.startswith("/"):
        _fail(artifact, name, "absolute archive path is forbidden")
    if re.match(r"^[A-Za-z]:", name):
        _fail(artifact, name, "Windows drive-prefixed archive path is forbidden")

    components = name.split("/")
    if ".." in components:
        _fail(artifact, name, "archive path traversal is forbidden")

    normalized_components = [
        component for component in components if component not in {"", "."}
    ]
    if not normalized_components:
        _fail(artifact, name, "archive member has an empty normalized path")
    return PurePosixPath(*normalized_components).as_posix()


def _normalize_members(
    names: Iterable[str],
    *,
    artifact: str,
) -> list[str]:
    normalized: list[str] = []
    originals_by_normalized: dict[str, str] = {}
    for original in names:
        member = normalize_archive_member(original, artifact=artifact)
        if member in originals_by_normalized:
            first = originals_by_normalized[member]
            _fail(
                artifact,
                original,
                f"duplicate normalized archive path {member!r}; first seen as {first!r}",
            )
        originals_by_normalized[member] = original
        normalized.append(member)
    return normalized


def _validate_zip_member_type(info: zipfile.ZipInfo, artifact: str) -> None:
    mode = info.external_attr >> 16
    file_type = stat.S_IFMT(mode)
    if info.is_dir():
        if file_type not in {0, stat.S_IFDIR}:
            _fail(artifact, info.filename, "unsupported ZIP directory member type")
        return
    if file_type not in {0, stat.S_IFREG}:
        if file_type == stat.S_IFLNK:
            reason = "ZIP symbolic links are forbidden"
        else:
            reason = "unsupported ZIP special member type"
        _fail(artifact, info.filename, reason)


def _validate_tar_member_type(member: tarfile.TarInfo, artifact: str) -> None:
    if member.isfile() or member.isdir():
        return
    if member.issym():
        reason = "TAR symbolic links are forbidden"
    elif member.islnk():
        reason = "TAR hard links are forbidden"
    elif member.ischr() or member.isblk():
        reason = "TAR device members are forbidden"
    elif member.isfifo():
        reason = "TAR FIFO members are forbidden"
    else:
        reason = "unsupported TAR special member type"
    _fail(artifact, member.name, reason)


def _pep503_normalize(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def _wheel_escape(value: str) -> str:
    return re.sub(r"[^\w\d.]+", "_", value, flags=re.UNICODE)


def _parse_metadata(text: str, artifact: str, path: str) -> tuple[str, str]:
    metadata = Parser().parsestr(text)
    name = metadata.get("Name")
    metadata_version = metadata.get("Version")
    if not name:
        _fail(artifact, path, "metadata is missing Name")
    if not metadata_version:
        _fail(artifact, path, "metadata is missing Version")
    return name, metadata_version


def _validate_metadata(
    text: str,
    *,
    artifact: str,
    path: str,
    expected_version: str,
) -> None:
    name, metadata_version = _parse_metadata(text, artifact, path)
    if _pep503_normalize(name) != _pep503_normalize(DISTRIBUTION_NAME):
        _fail(
            artifact,
            path,
            f"metadata project name {name!r} is not equivalent to {DISTRIBUTION_NAME!r}",
        )
    if metadata_version != expected_version:
        _fail(
            artifact,
            path,
            f"metadata version {metadata_version!r} does not match expected "
            f"version {expected_version!r}",
        )


def _validate_forbidden_paths(
    paths: Iterable[str],
    *,
    artifact: str,
    forbidden_directories: set[str],
    skip_first_component: bool = False,
) -> None:
    for path in paths:
        parts = PurePosixPath(path).parts
        checked_parts = parts[1:] if skip_first_component else parts
        forbidden = next(
            (part for part in checked_parts if part in forbidden_directories),
            None,
        )
        if forbidden is not None:
            _fail(artifact, path, f"forbidden directory {forbidden!r}")
        if path.endswith((".pyc", ".pyo")):
            _fail(artifact, path, "compiled Python files are forbidden")


def _read_zip_text(
    archive: zipfile.ZipFile,
    original_by_normalized: dict[str, str],
    normalized_path: str,
    artifact: str,
) -> str:
    try:
        payload = archive.read(original_by_normalized[normalized_path])
        return payload.decode("utf-8")
    except (KeyError, UnicodeDecodeError) as exc:
        _fail(artifact, normalized_path, f"cannot read UTF-8 metadata: {exc}")
    raise AssertionError("unreachable")


def verify_wheel(
    wheel_path: Path,
    *,
    project_root: Path,
    expected_version: str,
) -> None:
    artifact = wheel_path.name
    try:
        with zipfile.ZipFile(wheel_path) as archive:
            infos = archive.infolist()
            for info in infos:
                _validate_zip_member_type(info, artifact)
            normalized = _normalize_members(
                (info.filename for info in infos),
                artifact=artifact,
            )
            original_by_normalized = dict(
                zip(normalized, (info.filename for info in infos))
            )
            normalized_set = set(normalized)

            print(f"{artifact} contents:")
            for path in sorted(normalized):
                print(path)

            _validate_forbidden_paths(
                normalized,
                artifact=artifact,
                forbidden_directories=FORBIDDEN_DIRECTORIES,
            )

            expected_dist_info = (
                f"{_wheel_escape(DISTRIBUTION_NAME)}-"
                f"{_wheel_escape(expected_version)}.dist-info"
            )
            dist_info_directories = {
                PurePosixPath(path).parts[0]
                for path in normalized
                if PurePosixPath(path).parts[0].endswith(".dist-info")
            }
            if len(dist_info_directories) != 1:
                _fail(
                    artifact,
                    ".",
                    "expected exactly one top-level .dist-info directory; "
                    f"found {sorted(dist_info_directories)!r}",
                )
            dist_info = next(iter(dist_info_directories))
            if dist_info != expected_dist_info:
                _fail(
                    artifact,
                    dist_info,
                    f"unexpected .dist-info directory; expected {expected_dist_info!r}",
                )

            allowed_roots = {"openevalgate", dist_info}
            for path in normalized:
                root = PurePosixPath(path).parts[0]
                if root not in allowed_roots:
                    _fail(artifact, path, f"unexpected top-level wheel path {root!r}")

            expected_python = {
                path.relative_to(project_root).as_posix()
                for path in (project_root / "openevalgate").rglob("*.py")
            }
            expected_package_data = {
                path.relative_to(project_root).as_posix()
                for path in (project_root / "openevalgate" / "resources").rglob("*.json")
            }
            wheel_python = {
                path
                for path in normalized
                if path.startswith("openevalgate/") and path.endswith(".py")
            }
            for missing in sorted(expected_python - wheel_python):
                _fail(artifact, missing, "expected runtime Python file is missing")
            for unexpected in sorted(wheel_python - expected_python):
                _fail(artifact, unexpected, "unexpected runtime Python module")
            for missing in sorted(expected_package_data - normalized_set):
                _fail(artifact, missing, "expected runtime package data file is missing")

            required_metadata = {"METADATA", "WHEEL", "RECORD", "entry_points.txt"}
            for filename in sorted(required_metadata):
                path = f"{dist_info}/{filename}"
                if path not in normalized_set:
                    _fail(artifact, path, "required wheel metadata file is missing")

            metadata_path = f"{dist_info}/METADATA"
            _validate_metadata(
                _read_zip_text(
                    archive,
                    original_by_normalized,
                    metadata_path,
                    artifact,
                ),
                artifact=artifact,
                path=metadata_path,
                expected_version=expected_version,
            )

            entry_points_path = f"{dist_info}/entry_points.txt"
            entry_points = configparser.ConfigParser(interpolation=None)
            try:
                entry_points.read_string(
                    _read_zip_text(
                        archive,
                        original_by_normalized,
                        entry_points_path,
                        artifact,
                    )
                )
            except configparser.Error as exc:
                _fail(
                    artifact,
                    entry_points_path,
                    f"malformed entry-point metadata: {exc}",
                )
            if not entry_points.has_section("console_scripts"):
                _fail(
                    artifact,
                    entry_points_path,
                    "missing [console_scripts] section",
                )
            target = entry_points.get(
                "console_scripts",
                "openevalgate",
                fallback=None,
            )
            if target != "openevalgate.cli:main":
                _fail(
                    artifact,
                    entry_points_path,
                    "missing console script "
                    "'openevalgate = openevalgate.cli:main'",
                )
    except (OSError, zipfile.BadZipFile) as exc:
        _fail(artifact, wheel_path, f"cannot open wheel: {exc}")


def _read_tar_text(
    archive: tarfile.TarFile,
    member_by_normalized: dict[str, tarfile.TarInfo],
    normalized_path: str,
    artifact: str,
) -> str:
    try:
        extracted = archive.extractfile(member_by_normalized[normalized_path])
        if extracted is None:
            _fail(artifact, normalized_path, "metadata path is not a regular file")
        return extracted.read().decode("utf-8")
    except (KeyError, OSError, UnicodeDecodeError) as exc:
        _fail(artifact, normalized_path, f"cannot read UTF-8 metadata: {exc}")
    raise AssertionError("unreachable")


def verify_sdist(
    sdist_path: Path,
    *,
    project_root: Path,
    expected_version: str,
) -> None:
    artifact = sdist_path.name
    try:
        with tarfile.open(sdist_path, "r:gz") as archive:
            members = archive.getmembers()
            for member in members:
                _validate_tar_member_type(member, artifact)
            normalized = _normalize_members(
                (member.name for member in members),
                artifact=artifact,
            )
            member_by_normalized = dict(zip(normalized, members))
            normalized_set = set(normalized)

            print(f"{artifact} contents:")
            for path in sorted(normalized):
                print(path)

            roots = {PurePosixPath(path).parts[0] for path in normalized}
            if len(roots) != 1:
                _fail(
                    artifact,
                    ".",
                    f"expected exactly one top-level archive root; found {sorted(roots)!r}",
                )
            root = next(iter(roots))
            _validate_forbidden_paths(
                normalized,
                artifact=artifact,
                forbidden_directories=SDIST_FORBIDDEN_DIRECTORIES,
                skip_first_component=True,
            )

            required = {
                "pyproject.toml",
                "README.md",
                "LICENSE",
                "CHANGELOG.md",
                "PKG-INFO",
            }
            required.update(
                path.relative_to(project_root).as_posix()
                for path in (project_root / "openevalgate").rglob("*.py")
            )
            required.update(
                path.relative_to(project_root).as_posix()
                for path in (project_root / "openevalgate" / "resources").rglob("*.json")
            )
            for relative_path in sorted(required):
                archive_path = f"{root}/{relative_path}"
                if archive_path not in normalized_set:
                    _fail(artifact, archive_path, "required sdist file is missing")

            pkg_info_path = f"{root}/PKG-INFO"
            _validate_metadata(
                _read_tar_text(
                    archive,
                    member_by_normalized,
                    pkg_info_path,
                    artifact,
                ),
                artifact=artifact,
                path=pkg_info_path,
                expected_version=expected_version,
            )
    except (OSError, tarfile.TarError) as exc:
        _fail(artifact, sdist_path, f"cannot open source distribution: {exc}")


def _single_artifact(
    dist_dir: Path,
    pattern: str,
    description: str,
) -> Path:
    matches = sorted(dist_dir.glob(pattern))
    if len(matches) != 1:
        _fail(
            "dist",
            dist_dir,
            f"expected exactly one {description}; found "
            f"{len(matches)}: {[path.name for path in matches]!r}",
        )
    return matches[0]


def verify_distribution_artifacts(
    *,
    project_root: Path,
    dist_dir: Path,
    expected_version: str,
) -> tuple[Path, Path]:
    """Verify the single wheel and sdist in a distribution directory."""
    project_root = project_root.resolve()
    dist_dir = dist_dir.resolve()
    wheel_path = _single_artifact(dist_dir, "*.whl", "wheel")
    sdist_path = _single_artifact(
        dist_dir,
        "*.tar.gz",
        "source distribution",
    )
    verify_wheel(
        wheel_path,
        project_root=project_root,
        expected_version=expected_version,
    )
    verify_sdist(
        sdist_path,
        project_root=project_root,
        expected_version=expected_version,
    )
    return wheel_path, sdist_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Verify OpenEvalGate wheel and source-distribution contents."
    )
    parser.add_argument("--dist-dir", type=Path, default=Path("dist"))
    args = parser.parse_args(argv)
    project_root = Path(__file__).resolve().parents[1]
    try:
        expected_version = version(DISTRIBUTION_NAME)
    except PackageNotFoundError:
        print(
            "dist: '.': installed development distribution metadata for "
            "'openevalgate' is unavailable",
            file=sys.stderr,
        )
        return 1

    try:
        verify_distribution_artifacts(
            project_root=project_root,
            dist_dir=args.dist_dir,
            expected_version=expected_version,
        )
    except VerificationError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(
        f"Verified OpenEvalGate wheel and source distribution version "
        f"{expected_version}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
