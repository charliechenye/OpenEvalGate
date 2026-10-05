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
    (
        ESCALATION / "approval-recovery/eval_cases.yaml",
        "eval-cases-v1.schema.json",
        validate_eval_cases,
    ),
    (
        ESCALATION / "approval-recovery/escalation-contract.yaml",
        "escalation-contract-v1.schema.json",
        validate_escalation_contract,
    ),
]


def test_all_runnable_playbook_examples_are_in_the_lightweight_check() -> None:
    discovered = set((ROOT / GOLDEN).glob("*.yaml"))
    discovered.update((ROOT / ESCALATION).glob("*/escalation-contract.yaml"))
    discovered.update((ROOT / ESCALATION).glob("*/eval_cases.yaml"))
    assert discovered == {ROOT / path for path, _, _ in PLAYBOOK_EXAMPLES}


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
        metadata = node.get("extensions", {})
        assert set(metadata) <= {"source", "behavior_category", "owners"}
        if "source" in metadata:
            assert isinstance(metadata["source"], str)
        if "behavior_category" in metadata:
            assert isinstance(metadata["behavior_category"], list)
            assert all(isinstance(tag, str) for tag in metadata["behavior_category"])
        if "owners" in metadata:
            assert set(metadata["owners"]) == {"product", "policy", "engineering"}
            assert all(isinstance(contact, str) for contact in metadata["owners"].values())


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


def test_recovery_teaching_contract_validates_linked_cases() -> None:
    root = ROOT / ESCALATION / "approval-recovery"
    result = validate_escalation_contract(root / "escalation-contract.yaml", root / "eval_cases.yaml")
    assert result.valid, [(issue.path, issue.message) for issue in result.issues]
    cases = yaml.safe_load((root / "eval_cases.yaml").read_text())["eval_cases"]
    cases_by_id = {case["id"]: case for case in cases}
    assert set(cases_by_id) == {
        "rejected_approval", "expired_approval", "late_approval", "duplicate_callback",
        "edited_action", "conflicting_triggers", "unknown_tool_result", "autonomous_recovery",
        "mismatched_approval_binding", "valid_approval_resume",
    }
    # V1 has one workflow route. The simultaneous specialist obligation must
    # survive the refusal in observable trace/state assertions.
    conflict = cases_by_id["conflicting_triggers"]
    assert conflict["expected_workflow_route"] == "refuse"
    assert "create_fraud_case" in conflict["expected_trajectory"]["required_events"]
    assert "fraud_case_accepted" in conflict["expected_end_state"]["assertions"]
