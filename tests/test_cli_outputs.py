from __future__ import annotations

import json
from pathlib import Path

from openevalgate.cli import main


ROOT = Path(__file__).resolve().parents[1]
CUSTOMER_SUPPORT = ROOT / "examples" / "customer_support_assistant"


def test_report_json_is_deterministic_and_machine_readable(
    capsys,
) -> None:
    assert main(["report", str(CUSTOMER_SUPPORT), "--format", "json"]) == 0
    first = capsys.readouterr().out
    assert main(["report", str(CUSTOMER_SUPPORT), "--format", "json"]) == 0
    second = capsys.readouterr().out

    assert first == second
    payload = json.loads(first)
    assert payload["schema_version"] == "1"
    assert payload["command"] == "report"
    assert payload["status"] == "blocked"
    assert payload["run_identity"]["classification"]["freshness"] == "current"
    assert all(not str(issue["path"]).startswith("/") for issue in payload["issues"])


def test_report_card_contains_bounded_decision_summary(capsys) -> None:
    assert main(["report", str(CUSTOMER_SUPPORT), "--format", "card"]) == 0
    card = capsys.readouterr().out

    assert "# OpenEvalGate Decision Card" in card
    assert "## Blockers" in card
    assert "critical_escalation_regression" in card
    assert "deployment authorization" in card


def test_report_fail_on_blocked_is_opt_in(capsys) -> None:
    assert main(["report", str(CUSTOMER_SUPPORT)]) == 0
    capsys.readouterr()
    assert main(["report", str(CUSTOMER_SUPPORT), "--fail-on-blocked"]) == 1
    capsys.readouterr()


def test_minimal_init_is_valid_but_not_ready_and_refuses_overwrite(
    tmp_path: Path,
    capsys,
) -> None:
    project = tmp_path / "assistant"
    assert main(["init", str(project), "--profile", "minimal"]) == 0
    output = capsys.readouterr().out
    assert "synthetic or placeholder" in output
    assert main(["validate", str(project / "eval_cases.yaml")]) == 0
    capsys.readouterr()
    assert main(["check", str(project)]) == 0
    capsys.readouterr()
    assert main(["report", str(project), "--format", "card"]) == 0
    card = capsys.readouterr().out
    assert "Not ready" in card
    assert main(["init", str(project), "--profile", "minimal"]) == 1
    assert "Refusing to initialize non-empty directory" in capsys.readouterr().out
