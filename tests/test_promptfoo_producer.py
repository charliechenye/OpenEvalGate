from __future__ import annotations

import copy
import csv
import hashlib
import json
from pathlib import Path

import pytest

from openevalgate.output import report_output
from openevalgate.provenance import RunIdentityStatus, inspect_run_identity
from scripts import export_promptfoo_v1 as producer
from scripts import run_promptfoo_demo as demo


def _setup(tmp_path: Path) -> tuple[Path, list[str], dict]:
    project = tmp_path / "review"
    demo.prepare_project(project)
    args = demo.export_command(project)[2:]
    source = json.loads(demo.FIXTURE.read_text())
    return project, args, source


def _input(tmp_path: Path, args: list[str], source: dict) -> list[str]:
    path = tmp_path / "input.json"
    path.write_text(json.dumps(source), encoding="utf-8")
    args[args.index("--input") + 1] = str(path)
    return args


def _counts(source: dict) -> None:
    rows = source["results"]["results"]
    for key, reason in (("successes", 0), ("failures", 1), ("errors", 2)):
        source["results"]["stats"][key] = sum(row["failureReason"] == reason for row in rows)


def test_real_fixture_has_recorded_digests_and_no_private_paths() -> None:
    provenance = json.loads((demo.FIXTURE.parent / "provenance.json").read_text())
    assert provenance["promptfoo_version"] == producer.PROMPTFOO_VERSION
    assert provenance["synthetic"] is True
    for relative, digest in provenance["sha256"].items():
        assert (
            hashlib.sha256((demo.FIXTURE.parent.parent / relative).read_bytes()).hexdigest()
            == digest
        )
    assert b"/Users/" not in demo.FIXTURE.read_bytes()
    assert b"/private/tmp/" not in demo.FIXTURE.read_bytes()


def test_export_is_v1_valid_and_uses_case_authority(tmp_path: Path) -> None:
    project, args, source = _setup(tmp_path)
    source["results"]["results"][0]["testCase"]["metadata"]["openevalgate"]["expected_route"] = (
        "block"
    )
    before = {p.name: p.read_bytes() for p in project.iterdir() if p.is_file()}
    assert producer.main(_input(tmp_path, args, source)) == 0
    for name, data in before.items():
        assert (project / name).read_bytes() == data
    inspection = inspect_run_identity(project)
    assert inspection.status == RunIdentityStatus.COMPLETE
    assert inspection.classification.assurance.value == "verified"
    rows = list(csv.DictReader((project / "eval_results.csv").open()))
    invoice = next(row for row in rows if row["case_id"] == "invoice_explanation_001")
    assert invoice["expected_route"] == "show"
    assert invoice["actual_route"] == "show"
    assert invoice["route_match"] == "true"
    assert report_output(project)["status"] == "pass"


def test_same_eval_passes_but_missing_controls_block(tmp_path: Path) -> None:
    passing, args, _ = _setup(tmp_path)
    assert producer.main(args) == 0
    blocked = tmp_path / "blocked"
    demo.prepare_project(blocked, blocked=True)
    assert producer.main(demo.export_command(blocked)[2:]) == 0
    assert (passing / "eval_results.csv").read_bytes() == (
        blocked / "eval_results.csv"
    ).read_bytes()
    result = report_output(blocked)
    assert result["status"] == "blocked"
    assert {b["id"] for b in result["blockers"]} >= {"missing_rollback", "missing_monitoring"}


def test_exports_are_byte_identical_for_identical_inputs(tmp_path: Path) -> None:
    first, args, _ = _setup(tmp_path)
    assert producer.main(args) == 0
    second = tmp_path / "second"
    demo.prepare_project(second)
    assert producer.main(demo.export_command(second)[2:]) == 0
    paths = ["eval_results.csv", "run_manifest.yaml", "artifact_index.yaml"]
    paths += [str(p.relative_to(first)) for p in (first / "eval_runs").rglob("*") if p.is_file()]
    assert all((first / path).read_bytes() == (second / path).read_bytes() for path in paths)


@pytest.mark.parametrize(
    "mutation",
    [
        "version",
        "format",
        "empty",
        "missing_grader",
        "missing_output",
        "invalid_json",
        "missing_route",
        "unknown_route",
        "duplicate",
        "unknown_case",
        "missing_trial",
        "candidate",
        "candidate_version",
        "grader_conflict",
        "score_conflict",
        "invalid_score",
        "boolean_score",
        "observation_type",
        "execution_error",
        "truncated",
        "prompt_type",
        "prompt_identity",
        "boolean_grader_score",
        "missing_identity",
        "duplicate_observation_key",
        "missing_provider_id",
    ],
)
def test_invalid_exports_leave_no_complete_or_partial_package(
    tmp_path: Path, mutation: str
) -> None:
    project, args, source = _setup(tmp_path)
    row = source["results"]["results"][0]
    mapping = row["testCase"]["metadata"]["openevalgate"]
    if mutation == "version":
        source["metadata"]["promptfooVersion"] = "0.123.2"
    elif mutation == "format":
        source["results"]["version"] = 2
    elif mutation == "empty":
        source["results"]["results"] = []
    elif mutation == "missing_grader":
        row["gradingResult"] = None
    elif mutation == "missing_output":
        row.pop("response")
    elif mutation == "invalid_json":
        row["response"]["output"] = "not structured JSON"
    elif mutation in {"missing_route", "unknown_route", "observation_type"}:
        observation = json.loads(row["response"]["output"])
        if mutation == "missing_route":
            observation.pop("route")
        elif mutation == "unknown_route":
            observation["route"] = "approve"
        else:
            observation["trajectory_pass"] = "true"
        row["response"]["output"] = json.dumps(observation)
    elif mutation == "duplicate":
        source["results"]["results"].append(copy.deepcopy(row))
        _counts(source)
    elif mutation == "unknown_case":
        mapping["case_id"] = "unknown"
    elif mutation == "missing_trial":
        mapping.pop("trial_id")
    elif mutation == "candidate":
        mapping["candidate_id"] = "another-candidate"
    elif mutation == "candidate_version":
        mapping["candidate_version"] = "another-version"
    elif mutation == "grader_conflict":
        row["gradingResult"]["pass"] = False
    elif mutation == "score_conflict":
        row["gradingResult"]["score"] = 0
    elif mutation == "invalid_score":
        row["score"] = 1.1
    elif mutation == "boolean_score":
        row["score"] = True
    elif mutation == "execution_error":
        row.update(success=False, failureReason=2, error="synthetic provider failure")
        _counts(source)
    elif mutation == "truncated":
        source["results"]["results"].pop()
    elif mutation == "prompt_type":
        row["promptIdx"] = False
    elif mutation == "prompt_identity":
        row["promptId"] = "conflicting-prompt"
    elif mutation == "boolean_grader_score":
        row["gradingResult"]["score"] = True
    elif mutation == "missing_identity":
        row["testCase"]["metadata"].pop("openevalgate")
    elif mutation == "duplicate_observation_key":
        row["response"]["output"] = '{"route":"show","route":"block"}'
    elif mutation == "missing_provider_id":
        row["provider"].pop("id")
    assert producer.main(_input(tmp_path, args, source)) == 1
    assert not any(
        (project / name).exists()
        for name in ("run_manifest.yaml", "eval_results.csv", "artifact_index.yaml")
    )
    assert not (project / "eval_runs/run_001").exists()


def test_assertion_failure_is_evidence_and_never_becomes_a_pass(tmp_path: Path) -> None:
    project, args, source = _setup(tmp_path)
    row = source["results"]["results"][0]
    row.update(success=False, score=0, failureReason=1)
    row["gradingResult"]["pass"] = False
    row["gradingResult"]["score"] = 0
    row["gradingResult"]["reason"] = "Synthetic assertion failed"
    _counts(source)
    assert producer.main(_input(tmp_path, args, source)) == 0
    assert report_output(project)["status"] == "blocked"


def test_selection_does_not_merge_another_candidate(tmp_path: Path) -> None:
    project, args, source = _setup(tmp_path)
    other = copy.deepcopy(source["results"]["results"][0])
    other["provider"]["id"] = "another-provider"
    other["testCase"]["metadata"]["openevalgate"]["candidate_id"] = "another-candidate"
    source["results"]["results"].append(other)
    _counts(source)
    assert producer.main(_input(tmp_path, args, source)) == 0
    assert len(list(csv.DictReader((project / "eval_results.csv").open()))) == 5


def test_pretty_printed_observation_is_preserved_exactly(tmp_path: Path) -> None:
    project, args, source = _setup(tmp_path)
    row = source["results"]["results"][0]
    output = json.dumps(json.loads(row["response"]["output"]), indent=2)
    row["response"]["output"] = output
    assert producer.main(_input(tmp_path, args, source)) == 0
    csv_row = next(
        item
        for item in csv.DictReader((project / "eval_results.csv").open())
        if item["case_id"] == row["testCase"]["metadata"]["openevalgate"]["case_id"]
    )
    assert (project / csv_row["observed_output_path"]).read_bytes() == (output + "\n").encode()


def test_symlinked_output_directory_is_rejected(tmp_path: Path) -> None:
    project, args, _ = _setup(tmp_path)
    outside = tmp_path / "outside"
    outside.mkdir()
    (project / "eval_runs").symlink_to(outside, target_is_directory=True)
    assert producer.main(args) == 1
    assert list(outside.iterdir()) == []
    assert not (project / "run_manifest.yaml").exists()


def test_refuses_overwrite_and_policy_conflict(tmp_path: Path) -> None:
    project, args, _ = _setup(tmp_path)
    conflicting = args.copy()
    conflicting[conflicting.index("--run-id") + 1] = "another-run"
    assert producer.main(conflicting) == 1
    assert producer.main(args) == 0
    original = (project / "run_manifest.yaml").read_bytes()
    assert producer.main(args) == 1
    assert (project / "run_manifest.yaml").read_bytes() == original


def test_publish_failure_removes_own_partial_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project, args, _ = _setup(tmp_path)
    original = Path.open

    def fail_manifest(self, mode="r", *positional, **keywords):
        if self == project / "run_manifest.yaml" and mode == "xb":
            raise OSError("synthetic interrupted publication")
        return original(self, mode, *positional, **keywords)

    monkeypatch.setattr(Path, "open", fail_manifest)
    assert producer.main(args) == 1
    assert not (project / "eval_results.csv").exists()
    assert not (project / "artifact_index.yaml").exists()
    assert not (project / "eval_runs/run_001").exists()
