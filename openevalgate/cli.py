"""Command-line interface for OpenEvalGate."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from openevalgate.report import generate_report, write_report
from openevalgate.schema import validate_eval_cases
from openevalgate.validator import check_project


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="openevalgate",
        description="Validate GenAI launch-readiness artifacts and generate Markdown reports.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate", help="Validate a golden eval YAML file.")
    validate_parser.add_argument("eval_cases", type=Path)
    validate_parser.set_defaults(func=_validate)

    check_parser = subparsers.add_parser("check", help="Check a launch-readiness project directory.")
    check_parser.add_argument("project_dir", type=Path)
    check_parser.set_defaults(func=_check)

    report_parser = subparsers.add_parser("report", help="Generate a Markdown launch readiness report.")
    report_parser.add_argument("project_dir", type=Path)
    report_parser.add_argument("--output", "-o", type=Path, help="Output Markdown path.")
    report_parser.set_defaults(func=_report)

    return parser


def _validate(args: argparse.Namespace) -> int:
    result = validate_eval_cases(args.eval_cases)
    if result.valid:
        print(f"OK: {result.case_count} eval case(s) valid.")
        return 0
    print("Validation failed:")
    for issue in result.issues:
        print(f"- {issue.path}: {issue.message}")
    return 1


def _check(args: argparse.Namespace) -> int:
    result = check_project(args.project_dir)
    if result.valid:
        print(f"OK: {args.project_dir} contains required launch gate files.")
        if result.present_optional:
            print("Optional summaries found: " + ", ".join(result.present_optional))
        return 0

    print("Project check failed:")
    for missing in result.missing_required:
        print(f"- Missing required file: {missing}")
    for issue in result.issues:
        print(f"- {issue.path}: {issue.message}")
    return 1


def _report(args: argparse.Namespace) -> int:
    if args.output:
        target = write_report(args.project_dir, args.output)
        print(f"Wrote launch readiness report: {target}")
    else:
        print(generate_report(args.project_dir))
    return 0


if __name__ == "__main__":
    sys.exit(main())
