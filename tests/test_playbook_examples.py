"""Keep runnable playbook evidence on the public V1 validator path."""

from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator, FormatChecker

from openevalgate.escalation import validate_escalation_contract
from openevalgate.resources.schemas import load_schema
from openevalgate.schema import validate_eval_cases


ROOT = Path(__file__).resolve().parents[1]
GOLDEN = Path("docs/playbooks/golden-eval-set-playbook/examples")
ESCALATION = Path("docs/playbooks/human-escalation-playbook/examples")
PLAYBOOK_EXAMPLES = [
    (GOLDEN / "refund_agent_eval_cases.yaml", "eval-cases-v1.schema.json", validate_eval_cases),
    (GOLDEN / "education_assistant_eval_cases.yaml", "eval-cases-v1.schema.json", validate_eval_cases),
    (GOLDEN / "presales_assistant_eval_cases.yaml", "eval-cases-v1.schema.json", validate_eval_cases),
    (
        ESCALATION / "customer-support-refund/escalation-contract.yaml",
        "escalation-contract-v1.schema.json",
        validate_escalation_contract,
    ),
    (
        ESCALATION / "education-integrity/escalation-contract.yaml",
        "escalation-contract-v1.schema.json",
        validate_escalation_contract,
    ),
    (
        ESCALATION / "presales-commercial/escalation-contract.yaml",
        "escalation-contract-v1.schema.json",
        validate_escalation_contract,
    ),
]


@pytest.mark.parametrize("relative_path,schema_name,validator", PLAYBOOK_EXAMPLES)
def test_playbook_example_uses_formal_v1_schema_and_validator(
    relative_path, schema_name, validator
) -> None:
    path = ROOT / relative_path
    result = validator(path)
    assert result.valid, [(issue.path, issue.message) for issue in result.issues]
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    schema = Draft202012Validator(load_schema(schema_name), format_checker=FormatChecker())
    assert not list(schema.iter_errors(document))

    # Extensions in these teaching examples are metadata, never a hiding place
    # for unsupported policy or grading requirements. Owners here are contacts,
    # not approval authority. Allow new metadata deliberately when needed.
    nodes = [document]
    if "eval_cases" in document:
        nodes.extend(document["eval_cases"])
    else:
        nodes.append(document["escalation_contract"])
    for node in nodes:
        assert set(node.get("extensions", {})) <= {"source", "behavior_category", "owners"}


def test_migrated_behavior_and_gate_requirements_remain_visible() -> None:
    cases = {
        case["id"]: case
        for path, _, _ in PLAYBOOK_EXAMPLES[:3]
        for case in yaml.safe_load((ROOT / path).read_text(encoding="utf-8"))["eval_cases"]
    }
    refund = cases["refund_policy_boundary_001"]
    assert "preserve respectful tone" in refund["expected_behavior"]
    assert "issue refund without policy check" in refund["unacceptable_behavior"]
    assert "eligibility_check_before_compensation" in refund["expected_end_state"]["assertions"]
    assert refund["critical"] is True
    assert refund["release_gate"] == "critical_refund_tool_eligibility"

    integrity = cases["education_academic_integrity_001"]
    assert integrity["expected_route"] == "revise"
    assert integrity["expected_workflow_route"] == "refuse"
    assert "imply policy can be bypassed" in integrity["unacceptable_behavior"]
    assert "reveal_answer_key" in integrity["expected_trajectory"]["prohibited_events"]
    assert cases["presales_discount_boundary_002"]["expected_workflow_route"] == "escalate"

    contract = yaml.safe_load(
        (ROOT / ESCALATION / "customer-support-refund/escalation-contract.yaml").read_text()
    )["escalation_contract"]
    assert any("USD 25" in rule for rule in contract["boundaries"]["approval_required_when"])
    assert any("two attempts" in rule for rule in contract["boundaries"]["clarify_when"])
    assert any("close_case_without_resolution" in rule for rule in contract["boundaries"]["refuse_or_block_when"])
