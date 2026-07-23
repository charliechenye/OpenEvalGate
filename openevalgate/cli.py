"""Command-line interface for OpenEvalGate."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from openevalgate import __version__
from openevalgate.init_project import initialize_project
from openevalgate.output import (
    check_output,
    render_card,
    render_json,
    report_output,
    validate_output,
)
from openevalgate.project_inspection import inspect_project
from openevalgate.report import generate_report, write_report
from openevalgate.schema import validate_eval_cases


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="openevalgate",
        description="Validate GenAI launch-readiness artifacts and generate Markdown reports.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate", help="Validate a golden eval YAML file.")
    validate_parser.add_argument("eval_cases", type=Path)
    validate_parser.add_argument("--format", choices=("text", "json"), default="text")
    validate_parser.add_argument("--output", "-o", type=Path)
    validate_parser.set_defaults(func=_validate)

    check_parser = subparsers.add_parser(
        "check", help="Check a launch-readiness project directory."
    )
    check_parser.add_argument("project_dir", type=Path)
    check_parser.add_argument("--format", choices=("text", "json"), default="text")
    check_parser.add_argument("--output", "-o", type=Path)
    check_parser.set_defaults(func=_check)

    report_parser = subparsers.add_parser(
        "report", help="Generate a Markdown launch readiness report."
    )
    report_parser.add_argument("project_dir", type=Path)
    report_parser.add_argument(
        "--format",
        choices=("markdown", "card", "json"),
        default="markdown",
        help="Report format. The default Markdown format preserves the canonical report.",
    )
    report_parser.add_argument("--output", "-o", type=Path, help="Output path.")
    report_parser.add_argument(
        "--fail-on-blocked",
        action="store_true",
        help="Return exit code 1 when the report has a blocked recommendation.",
    )
    report_parser.set_defaults(func=_report)

    init_parser = subparsers.add_parser(
        "init", help="Create a deterministic minimal release-review project."
    )
    init_parser.add_argument("project_dir", type=Path)
    init_parser.add_argument("--profile", choices=("minimal",), default="minimal")
    init_parser.add_argument(
        "--force",
        action="store_true",
        help="Allow the minimal profile to overwrite its generated files.",
    )
    init_parser.set_defaults(func=_init)

    return parser


def _validate(args: argparse.Namespace) -> int:
    result = validate_eval_cases(args.eval_cases)
    if args.format == "json":
        _emit(render_json(validate_output(args.eval_cases)), args.output, "validation")
        return 0 if result.valid else 1
    lines: list[str]
    if result.valid:
        lines = [f"OK: {result.case_count} eval case(s) valid."]
    else:
        lines = ["Validation failed:"]
        lines.extend(f"- {issue.path}: {issue.message}" for issue in result.issues)
    _emit("\n".join(lines) + "\n", args.output, "validation")
    return 0 if result.valid else 1


def _check(args: argparse.Namespace) -> int:
    inspection = inspect_project(args.project_dir)
    if args.format == "json":
        _emit(render_json(check_output(args.project_dir)), args.output, "check")
        return 0 if inspection.valid else 1
    result = inspection.check
    lines: list[str]
    if inspection.valid:
        lines = [f"OK: {args.project_dir} contains required launch gate files."]
        if result.present_optional:
            lines.append("Optional summaries found: " + ", ".join(result.present_optional))
        lines.append(f"Run identity status: {inspection.run_identity_inspection.status.value}")
        lines.append("Artifact validation passed. This is not a launch recommendation.")
    else:
        lines = ["Project check failed:"]
        lines.extend(f"- Missing required file: {missing}" for missing in result.missing_required)
        lines.extend(f"- {issue.path}: {issue.message}" for issue in result.issues)
        lines.extend(f"- {issue.path}: {issue.message}" for issue in inspection.policy_issues)
        lines.append("Artifact validation failed. This is not a launch recommendation.")
    _emit("\n".join(lines) + "\n", args.output, "check")
    return 0 if inspection.valid else 1


def _report(args: argparse.Namespace) -> int:
    payload = report_output(args.project_dir)
    if args.format == "json":
        content = render_json(payload)
    elif args.format == "card":
        content = render_card(payload)
    elif args.output:
        target = write_report(args.project_dir, args.output)
        print(f"Wrote launch readiness report: {target}")
        return 1 if args.fail_on_blocked and payload["status"] == "blocked" else 0
    else:
        print(generate_report(args.project_dir))
        return 1 if args.fail_on_blocked and payload["status"] == "blocked" else 0
    _emit(content, args.output, f"{args.format} report")
    return 1 if args.fail_on_blocked and payload["status"] == "blocked" else 0


def _init(args: argparse.Namespace) -> int:
    try:
        written = initialize_project(args.project_dir, force=args.force)
    except ValueError as exc:
        print(f"Initialization failed: {exc}")
        return 1
    print(f"Initialized {args.profile} profile in {args.project_dir}.")
    for path in written:
        print(f"- {path.relative_to(args.project_dir)}")
    print("All generated evidence is synthetic or placeholder content and must be replaced.")
    return 0


def _emit(content: str, output: Path | None, label: str) -> int:
    if output is None:
        print(content, end="")
        return 0
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content, encoding="utf-8", newline="\n")
    print(f"Wrote {label}: {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
