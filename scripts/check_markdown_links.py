"""Check local Markdown links without requiring third-party tooling."""

from __future__ import annotations

import re
import sys
from pathlib import Path


LINK_PATTERN = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
SKIP_PARTS = {".git", ".venv", "venv", "__pycache__", ".mypy_cache", ".ruff_cache"}


def iter_markdown_files(root: Path) -> list[Path]:
    return sorted(
        path for path in root.rglob("*.md") if not any(part in SKIP_PARTS for part in path.parts)
    )


def local_link_target(raw_target: str) -> str | None:
    target = raw_target.strip().strip("<>")
    if not target or target.startswith("#"):
        return None
    if "://" in target or target.startswith(("mailto:", "tel:")):
        return None
    return target.split("#", 1)[0].split("?", 1)[0]


def find_broken_links(root: Path) -> list[str]:
    broken: list[str] = []
    for markdown_path in iter_markdown_files(root):
        text = markdown_path.read_text(encoding="utf-8")
        for match in LINK_PATTERN.finditer(text):
            target = local_link_target(match.group(1))
            if target is None:
                continue
            resolved = (markdown_path.parent / target).resolve()
            if not resolved.exists():
                broken.append(f"{markdown_path}:{target}")
    return broken


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    broken = find_broken_links(root)
    if broken:
        print("Broken local Markdown links:", file=sys.stderr)
        for item in broken:
            print(f"- {item}", file=sys.stderr)
        return 1
    print(f"Markdown link check passed ({len(iter_markdown_files(root))} files scanned).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
