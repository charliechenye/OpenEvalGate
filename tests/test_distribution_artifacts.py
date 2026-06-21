from __future__ import annotations

import io
import stat
import tarfile
import zipfile
from importlib.metadata import version
from pathlib import Path

import pytest

from scripts.verify_distribution_artifacts import (
    VerificationError,
    normalize_archive_member,
    verify_distribution_artifacts,
    verify_sdist,
    verify_wheel,
)


ROOT = Path(__file__).resolve().parents[1]
VERSION = version("openevalgate")
DIST_INFO = f"openevalgate-{VERSION}.dist-info"
SDIST_ROOT = f"openevalgate-{VERSION}"


def _source_files() -> dict[str, bytes]:
    return {
        path.relative_to(ROOT).as_posix(): b"# fixture\n"
        for path in (ROOT / "openevalgate").rglob("*.py")
    }


def _wheel_files(
    *,
    name: str = "openevalgate",
    version: str = VERSION,
    dist_info: str = DIST_INFO,
) -> dict[str, bytes]:
    files = _source_files()
    files.update(
        {
            f"{dist_info}/METADATA": (
                f"Name: {name}\nVersion: {version}\n"
            ).encode(),
            f"{dist_info}/WHEEL": b"Wheel-Version: 1.0\n",
            f"{dist_info}/RECORD": b"",
            f"{dist_info}/entry_points.txt": (
                b"[console_scripts]\n"
                b"openevalgate = openevalgate.cli:main\n"
            ),
        }
    )
    return files


def _write_wheel(
    path: Path,
    files: dict[str, bytes] | None = None,
    *,
    extra_entries: list[tuple[zipfile.ZipInfo | str, bytes]] | None = None,
) -> None:
    with zipfile.ZipFile(path, "w") as archive:
        for name, payload in (files or _wheel_files()).items():
            archive.writestr(name, payload)
        for info, payload in extra_entries or []:
            if isinstance(info, str) and "\\" in info:
                raw_info = zipfile.ZipInfo("placeholder")
                raw_info.filename = info
                info = raw_info
            archive.writestr(info, payload)


def _add_tar_file(
    archive: tarfile.TarFile,
    name: str,
    payload: bytes,
) -> None:
    info = tarfile.TarInfo(name)
    info.size = len(payload)
    archive.addfile(info, io.BytesIO(payload))


def _sdist_files(
    *,
    name: str = "openevalgate",
    version: str = VERSION,
) -> dict[str, bytes]:
    files = {
        f"{SDIST_ROOT}/pyproject.toml": b"[project]\n",
        f"{SDIST_ROOT}/README.md": b"# Fixture\n",
        f"{SDIST_ROOT}/LICENSE": b"MIT\n",
        f"{SDIST_ROOT}/CHANGELOG.md": b"# Changelog\n",
        f"{SDIST_ROOT}/PKG-INFO": (
            f"Name: {name}\nVersion: {version}\n"
        ).encode(),
    }
    files.update(
        {
            f"{SDIST_ROOT}/{path}": payload
            for path, payload in _source_files().items()
        }
    )
    return files


def _write_sdist(
    path: Path,
    files: dict[str, bytes] | None = None,
    *,
    special_members: list[tarfile.TarInfo] | None = None,
) -> None:
    with tarfile.open(path, "w:gz") as archive:
        for name, payload in (files or _sdist_files()).items():
            _add_tar_file(archive, name, payload)
        for member in special_members or []:
            archive.addfile(member)


def _assert_error(
    expected: str,
    function,
    *args,
    **kwargs,
) -> None:
    with pytest.raises(VerificationError, match=expected):
        function(*args, **kwargs)


def test_distribution_verifier_rejects_missing_wheel(tmp_path: Path) -> None:
    _write_sdist(tmp_path / f"{SDIST_ROOT}.tar.gz")

    _assert_error(
        "expected exactly one wheel; found 0",
        verify_distribution_artifacts,
        project_root=ROOT,
        dist_dir=tmp_path,
        expected_version=VERSION,
    )


def test_distribution_verifier_rejects_multiple_wheels(tmp_path: Path) -> None:
    _write_wheel(tmp_path / "one.whl")
    _write_wheel(tmp_path / "two.whl")
    _write_sdist(tmp_path / f"{SDIST_ROOT}.tar.gz")

    _assert_error(
        "expected exactly one wheel; found 2",
        verify_distribution_artifacts,
        project_root=ROOT,
        dist_dir=tmp_path,
        expected_version=VERSION,
    )


def test_distribution_verifier_rejects_missing_sdist(tmp_path: Path) -> None:
    _write_wheel(tmp_path / "one.whl")

    _assert_error(
        "expected exactly one source distribution; found 0",
        verify_distribution_artifacts,
        project_root=ROOT,
        dist_dir=tmp_path,
        expected_version=VERSION,
    )


def test_distribution_verifier_rejects_multiple_sdists(tmp_path: Path) -> None:
    _write_wheel(tmp_path / "one.whl")
    _write_sdist(tmp_path / "one.tar.gz")
    _write_sdist(tmp_path / "two.tar.gz")

    _assert_error(
        "expected exactly one source distribution; found 2",
        verify_distribution_artifacts,
        project_root=ROOT,
        dist_dir=tmp_path,
        expected_version=VERSION,
    )


def test_wheel_rejects_missing_expected_package_file(tmp_path: Path) -> None:
    files = _wheel_files()
    del files["openevalgate/cli.py"]
    wheel = tmp_path / "missing.whl"
    _write_wheel(wheel, files)

    _assert_error(
        "openevalgate/cli.py.*expected runtime Python file is missing",
        verify_wheel,
        wheel,
        project_root=ROOT,
        expected_version=VERSION,
    )


def test_wheel_rejects_unexpected_package_module(tmp_path: Path) -> None:
    files = _wheel_files()
    files["openevalgate/surprise.py"] = b""
    wheel = tmp_path / "unexpected.whl"
    _write_wheel(wheel, files)

    _assert_error(
        "openevalgate/surprise.py.*unexpected runtime Python module",
        verify_wheel,
        wheel,
        project_root=ROOT,
        expected_version=VERSION,
    )


@pytest.mark.parametrize(
    ("path", "reason"),
    [
        ("openevalgate/__pycache__/cli.pyc", "forbidden directory"),
        ("openevalgate/cli.pyo", "compiled Python files are forbidden"),
    ],
)
def test_wheel_rejects_cache_and_compiled_files(
    tmp_path: Path,
    path: str,
    reason: str,
) -> None:
    files = _wheel_files()
    files[path] = b""
    wheel = tmp_path / "forbidden.whl"
    _write_wheel(wheel, files)

    _assert_error(
        reason,
        verify_wheel,
        wheel,
        project_root=ROOT,
        expected_version=VERSION,
    )


@pytest.mark.parametrize(
    ("name", "version", "reason"),
    [
        ("other-project", VERSION, "metadata project name"),
        ("openevalgate", "9.9.9", "metadata version"),
    ],
)
def test_wheel_rejects_incorrect_metadata(
    tmp_path: Path,
    name: str,
    version: str,
    reason: str,
) -> None:
    wheel = tmp_path / "metadata.whl"
    _write_wheel(wheel, _wheel_files(name=name, version=version))

    _assert_error(
        reason,
        verify_wheel,
        wheel,
        project_root=ROOT,
        expected_version=VERSION,
    )


def test_wheel_accepts_pep503_equivalent_metadata_name(tmp_path: Path) -> None:
    wheel = tmp_path / "metadata.whl"
    _write_wheel(wheel, _wheel_files(name="OpenEvalGate"))

    verify_wheel(
        wheel,
        project_root=ROOT,
        expected_version=VERSION,
    )


def test_wheel_rejects_missing_console_script(tmp_path: Path) -> None:
    files = _wheel_files()
    files[f"{DIST_INFO}/entry_points.txt"] = b"[console_scripts]\nother = x:y\n"
    wheel = tmp_path / "entry-points.whl"
    _write_wheel(wheel, files)

    _assert_error(
        "missing console script",
        verify_wheel,
        wheel,
        project_root=ROOT,
        expected_version=VERSION,
    )


def test_wheel_rejects_malformed_dist_info_name(tmp_path: Path) -> None:
    wheel = tmp_path / "malformed.whl"
    _write_wheel(
        wheel,
        _wheel_files(dist_info=f"OpenEvalGate-{VERSION}.dist-info"),
    )

    _assert_error(
        "unexpected .dist-info directory",
        verify_wheel,
        wheel,
        project_root=ROOT,
        expected_version=VERSION,
    )


def test_wheel_rejects_multiple_dist_info_directories(tmp_path: Path) -> None:
    files = _wheel_files()
    files["other-1.0.dist-info/METADATA"] = b"Name: other\nVersion: 1.0\n"
    wheel = tmp_path / "multiple.whl"
    _write_wheel(wheel, files)

    _assert_error(
        "expected exactly one top-level .dist-info directory",
        verify_wheel,
        wheel,
        project_root=ROOT,
        expected_version=VERSION,
    )


@pytest.mark.parametrize(
    ("unsafe_path", "reason"),
    [
        ("/absolute.py", "absolute archive path"),
        ("C:/drive.py", "Windows drive-prefixed"),
        ("openevalgate/../escape.py", "path traversal"),
    ],
)
def test_wheel_rejects_unsafe_member_paths(
    tmp_path: Path,
    unsafe_path: str,
    reason: str,
) -> None:
    wheel = tmp_path / "unsafe.whl"
    _write_wheel(
        wheel,
        extra_entries=[(unsafe_path, b"")],
    )

    _assert_error(
        reason,
        verify_wheel,
        wheel,
        project_root=ROOT,
        expected_version=VERSION,
    )


def test_normalizer_rejects_nul_member_path() -> None:
    _assert_error(
        "NUL character",
        normalize_archive_member,
        "openevalgate/\x00bad.py",
        artifact="fixture.whl",
    )


def test_normalizer_rejects_backslash_member_path() -> None:
    _assert_error(
        "contains a backslash",
        normalize_archive_member,
        r"openevalgate\bad.py",
        artifact="fixture.whl",
    )


def test_wheel_rejects_duplicate_normalized_members(tmp_path: Path) -> None:
    wheel = tmp_path / "duplicate.whl"
    _write_wheel(
        wheel,
        extra_entries=[
            ("openevalgate/duplicate.txt", b"one"),
            ("openevalgate/./duplicate.txt", b"two"),
        ],
    )

    _assert_error(
        "duplicate normalized archive path",
        verify_wheel,
        wheel,
        project_root=ROOT,
        expected_version=VERSION,
    )


def test_wheel_rejects_zip_symlink(tmp_path: Path) -> None:
    symlink = zipfile.ZipInfo("openevalgate/link.py")
    symlink.create_system = 3
    symlink.external_attr = (stat.S_IFLNK | 0o777) << 16
    wheel = tmp_path / "symlink.whl"
    _write_wheel(wheel, extra_entries=[(symlink, b"target")])

    _assert_error(
        "ZIP symbolic links are forbidden",
        verify_wheel,
        wheel,
        project_root=ROOT,
        expected_version=VERSION,
    )


@pytest.mark.parametrize(
    ("member_type", "reason"),
    [
        (tarfile.SYMTYPE, "TAR symbolic links are forbidden"),
        (tarfile.LNKTYPE, "TAR hard links are forbidden"),
        (tarfile.CHRTYPE, "TAR device members are forbidden"),
        (tarfile.FIFOTYPE, "TAR FIFO members are forbidden"),
    ],
)
def test_sdist_rejects_special_members(
    tmp_path: Path,
    member_type: bytes,
    reason: str,
) -> None:
    member = tarfile.TarInfo(f"{SDIST_ROOT}/unsafe")
    member.type = member_type
    member.linkname = "target"
    sdist = tmp_path / "unsafe.tar.gz"
    _write_sdist(sdist, special_members=[member])

    _assert_error(
        reason,
        verify_sdist,
        sdist,
        project_root=ROOT,
        expected_version=VERSION,
    )


def test_sdist_rejects_incorrect_metadata_name_and_version(tmp_path: Path) -> None:
    sdist = tmp_path / "metadata.tar.gz"
    _write_sdist(sdist, _sdist_files(name="other", version="9.9.9"))

    _assert_error(
        "metadata project name",
        verify_sdist,
        sdist,
        project_root=ROOT,
        expected_version=VERSION,
    )
