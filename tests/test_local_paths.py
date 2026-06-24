from pathlib import Path

import pytest

from openevalgate.local_paths import resolve_local_evidence_path


def _write(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("ok\n", encoding="utf-8")
    return path


def _symlink_or_skip(link: Path, target: Path, *, target_is_directory: bool = False) -> None:
    try:
        link.symlink_to(target, target_is_directory=target_is_directory)
    except (NotImplementedError, OSError) as exc:
        pytest.skip(f"Symlink creation is unavailable: {exc}")


def test_safe_nested_posix_path_resolves_on_windows_host(tmp_path: Path) -> None:
    target = _write(tmp_path / "eval_runs" / "run_001" / "output.md")

    result = resolve_local_evidence_path(tmp_path, "eval_runs/run_001/output.md")

    assert result.error is None
    assert result.path == target.resolve(strict=False)


@pytest.mark.parametrize(
    "unsafe",
    [
        r"dir\file.md",
        r"C:\private\output.md",
        "C:/private/output.md",
        "C:relative/output.md",
        r"\\server\share\output.md",
        ".",
        "./file.md",
        "a/./b.md",
        "..",
        "a/../b.md",
        "/absolute.md",
        "//server/share/output.md",
        "https://example.com/output.md",
    ],
)
def test_unsafe_serialized_paths_are_rejected(tmp_path: Path, unsafe: str) -> None:
    assert resolve_local_evidence_path(tmp_path, unsafe).error is not None


def test_hidden_files_and_directories_are_allowed(tmp_path: Path) -> None:
    hidden_file = _write(tmp_path / ".hidden")
    hidden_nested = _write(tmp_path / ".config" / "file.yaml")

    assert (
        resolve_local_evidence_path(tmp_path, ".hidden").path
        == hidden_file.resolve(strict=False)
    )
    assert (
        resolve_local_evidence_path(tmp_path, ".config/file.yaml").path
        == hidden_nested.resolve(strict=False)
    )


def test_missing_required_file_is_rejected(tmp_path: Path) -> None:
    result = resolve_local_evidence_path(tmp_path, "missing/output.md")

    assert result.error == "missing"
    assert result.path is None


def test_final_symlink_is_rejected(tmp_path: Path) -> None:
    target = _write(tmp_path / "target.md")
    link = tmp_path / "link.md"
    _symlink_or_skip(link, target)

    assert resolve_local_evidence_path(tmp_path, "link.md").error == "symlink"


def test_intermediate_symlink_is_rejected(tmp_path: Path) -> None:
    real = tmp_path / "real"
    _write(real / "output.md")
    link = tmp_path / "linked"
    _symlink_or_skip(link, real, target_is_directory=True)

    assert resolve_local_evidence_path(tmp_path, "linked/output.md").error == "symlink"


def test_containment_escape_is_rejected(tmp_path: Path) -> None:
    target = _write(tmp_path / "outside.md")
    allowed = tmp_path / "allowed"
    allowed.mkdir()

    result = resolve_local_evidence_path(tmp_path, target.name, allowed_root=allowed)

    assert result.error == "escape"
    assert result.path is None
