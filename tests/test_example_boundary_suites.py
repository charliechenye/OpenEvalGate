from pathlib import Path

import yaml

from openevalgate.schema import load_eval_cases, validate_eval_cases


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_PROJECTS = {
    "customer_support_assistant": {
        "required_routes": {"answer", "clarify", "act", "approval", "escalate", "refuse"},
    },
    "education_assistant": {
        "required_routes": {"answer", "clarify", "approval", "escalate", "refuse"},
    },
    "presales_assistant": {
        "required_routes": {"answer", "clarify", "approval", "escalate", "refuse"},
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
            trigger["id"]
            for trigger in contract["triggers"]
            if trigger["path"] != "refuse"
        }
        destinations = {
            destination["id"]
            for destination in contract["routing"]["destinations"]
        }

        assert non_refusal_triggers.issubset(covered_trigger_ids), project_name
        assert destinations.issubset(covered_destinations), project_name

        refusal_triggers = [
            trigger for trigger in contract["triggers"] if trigger["path"] == "refuse"
        ]
        if refusal_triggers:
            assert any(case.get("expected_workflow_route") == "refuse" for case in cases)
