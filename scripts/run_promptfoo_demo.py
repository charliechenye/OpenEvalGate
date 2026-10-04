"""Run the synthetic Promptfoo handoff offline in a new review workspace."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "examples/integrations/promptfoo/fixtures/export.json"
SOURCE = ROOT / "examples/subscription_support_assistant"


def prepare_project(target: Path, *, blocked: bool = False) -> None:
    if target.exists():
        raise ValueError("Demo output must be a new directory; existing work is never overwritten.")
    shutil.copytree(
        SOURCE,
        target,
        ignore=shutil.ignore_patterns(
            "eval_results.csv",
            "run_manifest.yaml",
            "artifact_index.yaml",
            "generated_launch_report.md",
            "eval_runs",
            "__pycache__",
        ),
    )
    # This comparison context belongs to the synthetic demo, not a user's release.
    context_path = target / "review_context.yaml"
    context = yaml.safe_load(context_path.read_text(encoding="utf-8"))
    context["observed_at"] = json.loads(FIXTURE.read_text(encoding="utf-8"))["results"]["timestamp"]
    context_path.write_text(yaml.safe_dump(context, sort_keys=False), encoding="utf-8")
    if blocked:
        gates = target / "launch_gate_review.md"
        content = gates.read_text(encoding="utf-8")
        content = content.replace("| Rollback gate | pass |", "| Rollback gate | fail |")
        content = content.replace("| Observability gate | pass |", "| Observability gate | fail |")
        gates.write_text(content, encoding="utf-8")


def export_command(target: Path) -> list[str]:
    return [
        sys.executable,
        str(ROOT / "scripts/export_promptfoo_v1.py"),
        "--input",
        str(FIXTURE),
        "--project",
        str(target),
        "--run-id",
        "run_001",
        "--candidate-id",
        "subscription-support",
        "--candidate-version",
        "2026.06.18-rc1",
        "--evaluator-id",
        "synthetic-route-assertions",
        "--evaluator-version",
        "1",
        "--evaluation-kind",
        "deterministic",
        "--reviewed-by",
        "synthetic-demo",
        "--reviewed-at",
        json.loads(FIXTURE.read_text(encoding="utf-8"))["results"]["timestamp"],
        "--provider-id",
        "synthetic-subscription",
        "--prompt-index",
        "0",
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--blocked-controls", action="store_true")
    args = parser.parse_args(argv)
    try:
        prepare_project(args.output, blocked=args.blocked_controls)
        subprocess.run(export_command(args.output), check=True)
        from openevalgate.cli import main as cli

        checked = cli(["check", str(args.output)])
        reported = cli(["report", str(args.output), "--format", "card", "--fail-on-blocked"])
        return checked or reported
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        print(f"Synthetic demo failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
