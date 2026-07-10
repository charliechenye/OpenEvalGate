import csv
import re
from pathlib import Path

import yaml

from openevalgate.provenance import RunIdentityStatus, inspect_run_identity
from openevalgate.schema import load_eval_cases, validate_eval_cases


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_PROJECTS = {
    "customer_support_assistant": {
        "required_routes": {"answer", "clarify", "act", "approval", "escalate", "refuse"},
        "has_artifact_index": False,
    },
    "education_assistant": {
        "required_routes": {"answer", "clarify", "approval", "escalate", "refuse"},
        "has_artifact_index": False,
    },
    "presales_assistant": {
        "required_routes": {"answer", "clarify", "approval", "escalate", "refuse"},
        "has_artifact_index": False,
    },
    "subscription_support_assistant": {
        "required_routes": {"answer", "clarify", "approval", "escalate", "refuse"},
        "has_artifact_index": True,
    },
}


def test_example_boundary_suites_are_complete_and_valid() -> None:
    for project_name, expectations in EXAMPLE_PROJECTS.items():
        eval_path = ROOT / "examples" / project_name / "eval_cases.yaml"
        validation = validate_eval_cases(eval_path)
        cases = load_eval_cases(eval_path)
        synthetic_cases = [case for case in cases if case["case_type"] == "synthetic_boundary"]

        assert validation.valid, project_name
        assert synthetic_cases, project_name
        assert expectations["required_routes"].issubset(
            {case.get("expected_workflow_route") for case in cases}
        ), project_name

        for case in synthetic_cases:
            assert isinstance(case.get("boundary"), dict), case["id"]
            assert isinstance(case.get("expected_trajectory"), dict), case["id"]
            assert isinstance(case.get("expected_end_state"), dict), case["id"]
            assert case["expected_trajectory"]["required_events"], case["id"]
            assert case["expected_trajectory"]["prohibited_events"], case["id"]
            assert case["expected_end_state"]["assertions"], case["id"]


def test_canonical_examples_have_manifest_backed_run_identity() -> None:
    for project_name in EXAMPLE_PROJECTS:
        project = ROOT / "examples" / project_name
        inspection = inspect_run_identity(project)

        assert inspection.status == RunIdentityStatus.COMPLETE, project_name
        assert inspection.results_path == (project / "eval_results.csv").resolve(strict=False)
        assert inspection.identity is not None, project_name
        assert (project / "artifact_index.yaml").exists() == EXAMPLE_PROJECTS[project_name][
            "has_artifact_index"
        ], project_name


def test_escalation_contract_triggers_and_destinations_have_eval_coverage() -> None:
    for project_name in EXAMPLE_PROJECTS:
        project = ROOT / "examples" / project_name
        cases = load_eval_cases(project / "eval_cases.yaml")
        contract = yaml.safe_load(
            (project / "escalation_contract.yaml").read_text(encoding="utf-8")
        )["escalation_contract"]

        handoffs = [
            case["expected_handoff"]
            for case in cases
            if isinstance(case.get("expected_handoff"), dict)
        ]
        covered_trigger_ids = {handoff["trigger_id"] for handoff in handoffs}
        covered_destinations = {handoff["destination"] for handoff in handoffs}

        non_refusal_triggers = {
            trigger["id"] for trigger in contract["triggers"] if trigger["path"] != "refuse"
        }
        destinations = {destination["id"] for destination in contract["routing"]["destinations"]}

        assert non_refusal_triggers.issubset(covered_trigger_ids), project_name
        assert destinations.issubset(covered_destinations), project_name

        refusal_triggers = [
            trigger for trigger in contract["triggers"] if trigger["path"] == "refuse"
        ]
        if refusal_triggers:
            assert any(case.get("expected_workflow_route") == "refuse" for case in cases)


_METADATA_PATTERN = re.compile(
    r"^\s*(?:[-*]\s*)?(?:\*\*)?"
    r"(?P<label>Run ID|Case ID|Candidate|Evaluator)"
    r"\s*:\s*(?:\*\*)?\s*(?P<value>.*?)\s*$"
)


def _recognized_metadata(path: Path) -> dict[str, str]:
    metadata: dict[str, str] = {}
    if path.suffix.lower() != ".md":
        return metadata
    for line in path.read_text(encoding="utf-8").splitlines():
        match = _METADATA_PATTERN.match(line)
        if match:
            metadata[match.group("label")] = match.group("value").strip()
    return metadata


def test_example_eval_output_identity_is_internally_consistent() -> None:
    for project_name in EXAMPLE_PROJECTS:
        project = ROOT / "examples" / project_name
        results_path = project / "eval_results.csv"
        if not results_path.is_file():
            continue
        with results_path.open("r", encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        for row in rows:
            observed = (row.get("observed_output_path") or "").strip()
            if not observed:
                continue
            output = project / observed
            assert output.is_file(), f"{project_name}: missing {observed}"
            parts = Path(observed).parts
            if len(parts) >= 3 and parts[0] == "eval_runs":
                assert parts[1] == row["run_id"].strip(), f"{project_name}: {observed}"
            metadata = _recognized_metadata(output)
            expected = {
                "Run ID": row["run_id"].strip(),
                "Case ID": row["case_id"].strip(),
                "Candidate": row["candidate"].strip(),
                "Evaluator": row["evaluator"].strip(),
            }
            for label, value in metadata.items():
                assert value == expected[label], f"{project_name}: {observed} {label}"
