"""Experimental, offline Promptfoo 0.123.1 producer for existing V1 evidence."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import re
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from openevalgate.eval_results import (
    OPTIONAL_EVAL_RESULT_COLUMNS,
    REQUIRED_EVAL_RESULT_COLUMNS,
    validate_eval_results,
)
from openevalgate.provenance import RunIdentityStatus, inspect_run_identity
from openevalgate.review_policy import validate_review_policy
from openevalgate.schema import load_eval_cases, validate_eval_cases

PROMPTFOO_VERSION = "0.123.1"
PRODUCER_VERSION = "1"
BOOLEAN_OBSERVATIONS = {
    "trajectory_pass",
    "end_state_pass",
    "prohibited_action_occurred",
    "payload_complete",
    "fallback_success",
    "resume_success",
    "late_escalation",
}
STRING_OBSERVATIONS = {
    "actual_workflow_route",
    "actual_destination",
    "actual_workflow_id",
    "actual_model_id",
    "routing_policy_version",
    "routing_reason",
}


class ProducerError(ValueError):
    """An export cannot become an unambiguous V1 evidence package."""


def _object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ProducerError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def _constant(value: str) -> Any:
    raise ProducerError(f"Non-finite JSON value: {value}")


def _json(raw: str) -> Any:
    return json.loads(raw, object_pairs_hook=_object, parse_constant=_constant)


def _text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise ProducerError(f"{name} must be a nonblank, trimmed string.")
    if "\n" in value or "\r" in value:
        raise ProducerError(f"{name} must be a single line.")
    return value


def _nonblank(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ProducerError(f"{name} must be nonblank text.")
    return value


def _mapping(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ProducerError(f"{name} must be an object.")
    return value


def _boolean(value: Any, name: str) -> bool:
    if type(value) is not bool:
        raise ProducerError(f"{name} must be a boolean.")
    return value


def _digest(data: bytes) -> dict[str, str]:
    return {"sha256": hashlib.sha256(data).hexdigest()}


def _yaml_bytes(data: dict[str, Any]) -> bytes:
    return yaml.safe_dump(data, sort_keys=False, allow_unicode=True).encode("utf-8")


def _validate_counts(summary: dict[str, Any], records: list[Any]) -> None:
    stats = _mapping(summary.get("stats"), "results.stats")
    actual = {"successes": 0, "failures": 0, "errors": 0}
    for item in records:
        record = _mapping(item, "result row")
        success = _boolean(record.get("success"), "success")
        reason = record.get("failureReason")
        if type(reason) is not int or reason not in (0, 1, 2):
            raise ProducerError("Unsupported failureReason in exported result.")
        if success != (reason == 0):
            raise ProducerError("Contradictory success/failureReason in exported result.")
        if type(record.get("promptIdx")) is not int or record["promptIdx"] < 0:
            raise ProducerError("promptIdx must be a non-negative integer.")
        actual[("successes", "failures", "errors")[reason]] += 1
    for name, count in actual.items():
        if type(stats.get(name)) is not int or stats[name] != count:
            raise ProducerError(f"Contradictory or truncated export: results.stats.{name}.")


def _validate_scope(project: Path, args: argparse.Namespace) -> None:
    if not project.is_dir():
        raise ProducerError("--project must be an existing review project.")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", args.run_id):
        raise ProducerError("--run-id must contain only letters, digits, underscores or hyphens.")
    for key in (
        "candidate_id",
        "candidate_version",
        "evaluator_id",
        "evaluator_version",
        "reviewed_by",
        "reviewed_at",
        "provider_id",
    ):
        _text(getattr(args, key), "--" + key.replace("_", "-"))
    if args.prompt_index < 0:
        raise ProducerError("--prompt-index must be non-negative.")
    policy = validate_review_policy(project)
    if not policy.policy_valid:
        raise ProducerError("Repair review_policy.yaml before exporting results.")
    scope = policy.policy.evaluation_scope if policy.policy else None
    if scope and (scope.run_id != args.run_id or scope.candidate != args.candidate_id):
        raise ProducerError("Explicit run/candidate identity conflicts with review_policy.yaml.")
    for name in ("eval_results.csv", "run_manifest.yaml", "artifact_index.yaml"):
        if (project / name).exists() or (project / name).is_symlink():
            raise ProducerError(f"Refusing to overwrite {name}; use a fresh review workspace.")
    if (project / "eval_runs").is_symlink():
        raise ProducerError("Refusing a symlinked eval_runs directory.")
    run_dir = project / "eval_runs" / args.run_id
    if run_dir.exists() or run_dir.is_symlink():
        raise ProducerError("Refusing to overwrite the selected run directory.")


def _row(
    record: dict[str, Any], cases: dict[str, dict[str, Any]], args: argparse.Namespace
) -> tuple[dict[str, str], bytes]:
    metadata = _mapping(
        _mapping(record.get("testCase"), "testCase").get("metadata"), "test metadata"
    )
    identity = _mapping(metadata.get("openevalgate"), "metadata.openevalgate")
    case_id = _text(identity.get("case_id"), "case_id")
    trial_id = _text(identity.get("trial_id"), "trial_id")
    if case_id not in cases:
        raise ProducerError(f"Unknown eval case: {case_id}")
    if (
        identity.get("candidate_id") != args.candidate_id
        or identity.get("candidate_version") != args.candidate_version
    ):
        raise ProducerError(f"Candidate identity conflicts with result metadata for {case_id}.")
    if record.get("error") or record.get("failureReason") == 2:
        raise ProducerError(
            f"Promptfoo execution error for {case_id}; no complete run is exported."
        )
    success = _boolean(record.get("success"), "success")
    grading = _mapping(record.get("gradingResult"), "gradingResult")
    if _boolean(grading.get("pass"), "gradingResult.pass") != success:
        raise ProducerError(f"Contradictory grading result for {case_id}.")
    if record.get("failureReason") != (0 if success else 1):
        raise ProducerError(f"Contradictory failureReason for {case_id}.")
    score = record.get("score")
    if (
        isinstance(score, bool)
        or not isinstance(score, (int, float))
        or not math.isfinite(score)
        or not 0 <= score <= 1
    ):
        raise ProducerError(f"score for {case_id} must be finite and within V1's [0, 1] range.")
    if "score" in grading:
        grader_score = grading["score"]
        if (
            isinstance(grader_score, bool)
            or not isinstance(grader_score, (int, float))
            or grader_score != score
        ):
            raise ProducerError(f"Contradictory grader score for {case_id}.")
    response = _mapping(record.get("response"), "response")
    raw_output = _nonblank(response.get("output"), "response.output")
    observation = _mapping(_json(raw_output), "structured observation")
    route = _text(observation.get("route"), "observation.route")
    if route not in {"show", "revise", "escalate", "block"}:
        raise ProducerError(f"Unsupported actual route for {case_id}: {route}")
    case = cases[case_id]
    expected = case["expected_route"]
    row = dict.fromkeys(REQUIRED_EVAL_RESULT_COLUMNS + OPTIONAL_EVAL_RESULT_COLUMNS, "")
    row.update(
        {
            "schema_version": "1",
            "run_id": args.run_id,
            "case_id": case_id,
            "trial_id": trial_id,
            "candidate": args.candidate_id,
            "evaluator": args.evaluator_id,
            "actual_route": route,
            "expected_route": expected,
            "route_match": str(route == expected).lower(),
            "passed": str(success).lower(),
            "score": str(float(score)),
            "reviewed_by": args.reviewed_by,
            "reviewed_at": args.reviewed_at,
            "notes": "Imported from a pinned Promptfoo export; producer metadata is declared evidence.",
        }
    )
    if not success:
        row["failure_category"] = "assertion_failure"
        row["failure_reason"] = _nonblank(grading.get("reason"), "failure reason")
    for field in BOOLEAN_OBSERVATIONS:
        if field in observation:
            row[field] = str(_boolean(observation[field], field)).lower()
    for field in STRING_OBSERVATIONS:
        if field in observation:
            value = observation[field]
            row[field] = "" if value == "" else _text(value, field)
    workflow = case.get("expected_workflow_route")
    if row["actual_workflow_route"] and workflow:
        row["workflow_route_match"] = str(row["actual_workflow_route"] == workflow).lower()
    handoff = case.get("expected_handoff") or {}
    destination = handoff.get("destination_id") if isinstance(handoff, dict) else None
    if row["actual_destination"] and destination:
        row["destination_match"] = str(row["actual_destination"] == destination).lower()
    return row, (raw_output + "\n").encode("utf-8")


def export_results(args: argparse.Namespace) -> int:
    project = args.project.resolve()
    _validate_scope(project, args)
    validation = validate_eval_cases(project / "eval_cases.yaml")
    if not validation.valid:
        raise ProducerError("Repair eval_cases.yaml before exporting results.")
    case_bytes = (project / "eval_cases.yaml").read_bytes()
    cases = {case["id"]: case for case in load_eval_cases(project / "eval_cases.yaml")}
    raw = args.input.read_bytes()
    source = _mapping(_json(raw.decode("utf-8")), "Promptfoo export")
    metadata = _mapping(source.get("metadata"), "export metadata")
    if metadata.get("promptfooVersion") != PROMPTFOO_VERSION:
        raise ProducerError(f"Only Promptfoo {PROMPTFOO_VERSION} exports are supported.")
    summary = _mapping(source.get("results"), "results summary")
    if type(summary.get("version")) is not int or summary["version"] != 3:
        raise ProducerError("Only the pinned version's EvaluateSummaryV3 JSON export is supported.")
    records = summary.get("results")
    if not isinstance(records, list) or not records:
        raise ProducerError("The export must contain result rows.")
    _validate_counts(summary, records)
    completed_at = _text(summary.get("timestamp"), "results.timestamp")
    try:
        timestamp = datetime.fromisoformat(completed_at.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ProducerError("results.timestamp must be an ISO timestamp.") from exc
    if timestamp.utcoffset() is None:
        raise ProducerError("results.timestamp must include a timezone.")
    rows: list[dict[str, str]] = []
    observations: dict[tuple[str, str], bytes] = {}
    prompt_ids: set[str] = set()
    for item in records:
        record = _mapping(item, "result row")
        provider = _mapping(record.get("provider"), "provider")
        provider_id = _text(provider.get("id"), "provider.id")
        if provider_id != args.provider_id or record.get("promptIdx") != args.prompt_index:
            continue
        prompt_ids.add(_text(record.get("promptId"), "promptId"))
        if len(prompt_ids) != 1:
            raise ProducerError("Selected prompt index has conflicting prompt identities.")
        row, output = _row(record, cases, args)
        key = (row["case_id"], row["trial_id"])
        if key in observations:
            raise ProducerError(f"Duplicate case/trial mapping: {key[0]} / {key[1]}")
        observations[key] = output
        rows.append(row)
    if not rows:
        raise ProducerError("No rows match the explicit provider/prompt selection.")
    run_prefix = f"eval_runs/{args.run_id}"
    files: dict[str, bytes] = {
        f"{run_prefix}/promptfoo-export.json": raw,
        f"{run_prefix}/inputs/eval_cases.yaml": case_bytes,
    }
    artifacts: list[dict[str, Any]] = []
    for row in sorted(rows, key=lambda row: (row["case_id"], row["trial_id"])):
        key = (row["case_id"], row["trial_id"])
        name = hashlib.sha256(json.dumps(key).encode()).hexdigest()
        path = f"{run_prefix}/observations/{name}.json"
        row["observed_output_path"] = path
        files[path] = observations[key]
        artifacts.append(
            {
                "artifact_id": name,
                "artifact_type": "json",
                "path": path,
                "case_id": key[0],
                "trial_id": key[1],
                "evaluator_ref": args.evaluator_id,
                "digest": _digest(observations[key]),
            }
        )
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(
        buffer,
        fieldnames=REQUIRED_EVAL_RESULT_COLUMNS + OPTIONAL_EVAL_RESULT_COLUMNS,
        lineterminator="\n",
    )
    writer.writeheader()
    writer.writerows(sorted(rows, key=lambda row: (row["case_id"], row["trial_id"])))
    files["eval_results.csv"] = buffer.getvalue().encode("utf-8")
    files["artifact_index.yaml"] = _yaml_bytes(
        {"schema_version": "1", "run_id": args.run_id, "artifacts": artifacts}
    )
    files["run_manifest.yaml"] = _yaml_bytes(
        {
            "schema_version": "1",
            "run": {"id": args.run_id, "status": "complete", "completed_at": completed_at},
            "candidate": {"id": args.candidate_id, "version": args.candidate_version},
            "producer": {"id": "openevalgate-promptfoo-example", "version": PRODUCER_VERSION},
            "evaluation": {
                "kind": args.evaluation_kind,
                "evaluator": {"id": args.evaluator_id, "version": args.evaluator_version},
                "framework": {"id": "promptfoo", "version": PROMPTFOO_VERSION},
            },
            "inputs": [
                {
                    "role": "eval_cases",
                    "path": f"{run_prefix}/inputs/eval_cases.yaml",
                    "digest": _digest(case_bytes),
                }
            ],
            "outputs": {
                "results": {
                    "path": "eval_results.csv",
                    "digest": _digest(files["eval_results.csv"]),
                },
                "artifact_index": {
                    "path": "artifact_index.yaml",
                    "digest": _digest(files["artifact_index.yaml"]),
                },
                "additional": [
                    {"path": f"{run_prefix}/promptfoo-export.json", "digest": _digest(raw)}
                ],
            },
            "extensions": {
                "promptfoo_eval_id": _text(source.get("evalId"), "evalId"),
                "provider_id": args.provider_id,
                "prompt_index": args.prompt_index,
            },
        }
    )
    with tempfile.TemporaryDirectory(prefix="openevalgate-producer-") as temporary:
        stage = Path(temporary)
        (stage / "eval_cases.yaml").write_bytes(case_bytes)
        if (project / "review_policy.yaml").is_file():
            (stage / "review_policy.yaml").write_bytes(
                (project / "review_policy.yaml").read_bytes()
            )
        for path, data in files.items():
            target = stage / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        identity = inspect_run_identity(stage)
        if identity.status != RunIdentityStatus.COMPLETE:
            raise ProducerError(
                "Generated provenance failed V1 validation: "
                + "; ".join(finding.message for finding in identity.findings)
            )
        result = validate_eval_results(stage, identity_inspection=identity)
        if not result.valid:
            raise ProducerError(
                "Generated results failed V1 validation: "
                + "; ".join(issue.message for issue in result.issues)
            )
        created: list[Path] = []
        run_dir = project / run_prefix
        owns_run_dir = False
        try:
            run_dir.parent.mkdir(exist_ok=True)
            run_dir.mkdir()
            owns_run_dir = True
            shutil.copytree(stage / run_prefix, run_dir, dirs_exist_ok=True)
            # The authoritative manifest is published last. Partial evidence fails closed.
            for name in ("artifact_index.yaml", "eval_results.csv", "run_manifest.yaml"):
                path = project / name
                with path.open("xb") as stream:
                    created.append(path)
                    stream.write(files[name])
        except OSError:
            for created_path in reversed(created):
                created_path.unlink(missing_ok=True)
            if owns_run_dir:
                shutil.rmtree(run_dir)
            raise
    return len(rows)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--project", type=Path, required=True)
    for name in (
        "run-id",
        "candidate-id",
        "candidate-version",
        "evaluator-id",
        "evaluator-version",
        "reviewed-by",
        "reviewed-at",
        "provider-id",
    ):
        parser.add_argument("--" + name, required=True)
    parser.add_argument("--prompt-index", type=int, required=True)
    parser.add_argument(
        "--evaluation-kind", choices=("deterministic", "model_judge"), required=True
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        count = export_results(args)
    except (ValueError, OSError, yaml.YAMLError) as exc:
        print(f"Promptfoo export rejected: {exc}", file=sys.stderr)
        return 1
    print(
        f"Exported {count} rows for {args.run_id}; existing controls and review context were not changed."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
