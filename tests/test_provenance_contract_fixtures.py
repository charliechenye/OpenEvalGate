"""Contract-development checks for eval-run provenance fixtures.

This module validates provenance schemas, fixture integrity, referenced evidence,
recorded digests, orphan-file hygiene, and selected scenario invariants. It is
not the production provenance parser or classifier. PR 19 will implement complete
classification, finding precedence, authorization evaluation, and full comparison
against the normative expected outputs.
"""

import csv
import hashlib
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / "spec" / "fixtures" / "provenance" / "v1"
SCHEMAS = {
    "manifest": ROOT / "schemas" / "eval-run-manifest-v1.schema.json",
    "artifact_index": ROOT / "schemas" / "eval-run-artifact-index-v1.schema.json",
    "review_context": ROOT / "schemas" / "eval-run-review-context-v1.schema.json",
    "expected": ROOT / "schemas" / "eval-run-provenance-expected-v1.schema.json",
}
SINGLETON_ROLES = {
    "eval_cases",
    "evaluation_policy",
    "review_policy",
    "routing_policy",
    "escalation_contract",
    "action_risk_matrix",
}
CSV_HEADERS = [
    "run_id",
    "case_id",
    "candidate",
    "evaluator",
    "actual_route",
    "expected_route",
    "route_match",
    "passed",
    "score",
    "failure_category",
    "failure_reason",
    "observed_output_path",
    "reviewed_by",
    "reviewed_at",
    "notes",
    "trial_id",
]


def load_yaml(path):
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def schemas():
    loaded = {name: load_json(path) for name, path in SCHEMAS.items()}
    for schema in loaded.values():
        Draft202012Validator.check_schema(schema)
    return loaded


@pytest.fixture(scope="module")
def validators(schemas):
    checker = FormatChecker()
    return {name: Draft202012Validator(schema, format_checker=checker) for name, schema in schemas.items()}


def fixture_dirs():
    return sorted(p for p in FIXTURE_ROOT.iterdir() if p.is_dir() and any(p.iterdir()))


def schema_status(path, validator):
    if not path.exists():
        return "not_present"
    instance = load_yaml(path)
    return "invalid" if list(validator.iter_errors(instance)) else "valid"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_dt(value):
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def norm_rel(root, rel):
    raw = Path(rel)
    if raw.is_absolute() or re.match(r"^[A-Za-z]:[\\/]", rel):
        return None, "provenance_unsafe_path"
    parts = raw.parts
    if ".." in parts:
        return None, "provenance_unsafe_path"
    full = (root / raw).resolve(strict=False)
    allowed = root.resolve(strict=False)
    try:
        full.relative_to(allowed)
    except ValueError:
        return None, "provenance_unsafe_path"
    return full, None


def manifest_descriptor_paths(manifest):
    if not manifest:
        return []
    descriptors = []
    candidate = manifest.get("candidate", {})
    if isinstance(candidate.get("artifact"), dict):
        descriptors.append(("candidate_artifact", candidate["artifact"]))

    evaluation = manifest.get("evaluation", {})
    if isinstance(evaluation.get("policy"), dict):
        descriptors.append(("input", evaluation["policy"]))
    evaluator = evaluation.get("evaluator", {})
    if isinstance(evaluator.get("configuration"), dict):
        descriptors.append(("input", evaluator["configuration"]))
    if isinstance(evaluator.get("decision_policy"), dict):
        descriptors.append(("input", evaluator["decision_policy"]))
    for component in evaluator.get("components", []) or []:
        if isinstance(component.get("configuration"), dict):
            descriptors.append(("input", component["configuration"]))

    for desc in manifest.get("inputs", []) or []:
        descriptors.append(("input", desc))

    outputs = manifest.get("outputs", {})
    if isinstance(outputs.get("results"), dict):
        descriptors.append(("results", outputs["results"]))
    if isinstance(outputs.get("artifact_index"), dict):
        descriptors.append(("artifact_index", outputs["artifact_index"]))
    for desc in outputs.get("additional", []) or []:
        descriptors.append(("output", desc))
    return descriptors


def review_context_descriptor_paths(review_context):
    if not review_context:
        return []
    descriptors = []
    candidate = review_context.get("candidate", {})
    if isinstance(candidate.get("artifact"), dict):
        descriptors.append(("candidate_artifact", candidate["artifact"]))
    for desc in review_context.get("inputs", []) or []:
        descriptors.append(("input", desc))
    return descriptors


def descriptor_paths(doc):
    if not doc:
        return []
    if "run" in doc or "outputs" in doc or "evaluation" in doc:
        return manifest_descriptor_paths(doc)
    return review_context_descriptor_paths(doc)


def resolve_descriptor(root, descriptor):
    if "path" not in descriptor:
        return None, None
    return norm_rel(root, descriptor["path"])


def verify_descriptor(root, context, descriptor, findings, missing_finding="provenance_local_file_missing", digest_finding=None):
    if "path" not in descriptor:
        return
    path, issue = resolve_descriptor(root, descriptor)
    if issue:
        findings.add(issue)
        return
    if not path.exists() or not path.is_file():
        findings.add(missing_finding)
        return
    if path.is_symlink():
        findings.add("provenance_unsafe_path")
        return
    if "digest" in descriptor:
        expected = descriptor["digest"].get("sha256")
        if expected != sha256(path):
            if digest_finding:
                findings.add(digest_finding)
            elif context == "results":
                findings.add("provenance_output_digest_mismatch")
            else:
                findings.add("provenance_input_digest_mismatch")


def read_csv_rows(path):
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == CSV_HEADERS, f"Unexpected CSV headers in {path}: {reader.fieldnames}"
        return list(reader)



def referenced_fixture_files(fixture):
    referenced = set()

    def add_path(root, rel):
        resolved, issue = norm_rel(root, rel)
        if not issue and resolved.exists():
            referenced.add(resolved.resolve(strict=False))

    manifest_path = fixture / "run_manifest.yaml"
    if manifest_path.exists():
        manifest = load_yaml(manifest_path)
        for _, desc in descriptor_paths(manifest):
            if "path" in desc:
                add_path(fixture.resolve(strict=False), desc["path"])
        outputs = manifest.get("outputs", {}) if manifest else {}
        results = outputs.get("results", {})
        if "path" in results:
            add_path(fixture.resolve(strict=False), results["path"])
        artifact_index = outputs.get("artifact_index", {})
        if "path" in artifact_index:
            add_path(fixture.resolve(strict=False), artifact_index["path"])
        if "path" in results and (fixture / results["path"]).exists():
            for row in read_csv_rows(fixture / results["path"]):
                observed = row.get("observed_output_path", "").strip()
                if observed:
                    add_path((fixture / results["path"]).parent.resolve(strict=False), observed)

    if not manifest_path.exists() and (fixture / "eval_results.csv").exists():
        referenced.add((fixture / "eval_results.csv").resolve(strict=False))

    artifact_path = fixture / "artifact_index.yaml"
    if artifact_path.exists():
        artifact_index = load_yaml(artifact_path)
        for artifact in artifact_index.get("artifacts", []) or []:
            if "path" in artifact:
                add_path(artifact_path.parent.resolve(strict=False), artifact["path"])

    review_path = fixture / "review_context.yaml"
    if review_path.exists():
        review = load_yaml(review_path)
        for _, desc in descriptor_paths(review):
            if "path" in desc:
                add_path(review_path.parent.resolve(strict=False), desc["path"])

    return referenced


def resource_key(desc):
    role = desc.get("role")
    if role in SINGLETON_ROLES:
        return (role, None)
    return (role, desc.get("name"))


def same_digest(a, b):
    return a.get("digest", {}).get("sha256") == b.get("digest", {}).get("sha256")


def norm_descriptor_path(run_root, desc):
    if "path" not in desc:
        return None
    resolved, issue = resolve_descriptor(run_root, desc)
    if issue:
        return None
    return resolved.relative_to(run_root.resolve(strict=False)).as_posix()


def canonical_mirrors(manifest):
    evaluation = manifest.get("evaluation", {})
    evaluator = evaluation.get("evaluator", {})
    mirrors = []
    if "policy" in evaluation:
        mirrors.append((evaluation["policy"], ("evaluation_policy", None)))
    if "configuration" in evaluator:
        mirrors.append((evaluator["configuration"], ("evaluator_configuration", evaluator.get("id"))))
    if "decision_policy" in evaluator:
        mirrors.append((evaluator["decision_policy"], ("hybrid_decision_policy", evaluator.get("id"))))
    for component in evaluator.get("components", []) or []:
        if "configuration" in component:
            mirrors.append((component["configuration"], ("evaluator_component_configuration", component.get("id"))))
    return mirrors


def validate_fixture(fixture, validators):
    expected = load_yaml(fixture / "expected.yaml")
    findings = set()
    schema = {
        "manifest": schema_status(fixture / "run_manifest.yaml", validators["manifest"]),
        "artifact_index": schema_status(fixture / "artifact_index.yaml", validators["artifact_index"]),
        "review_context": schema_status(fixture / "review_context.yaml", validators["review_context"]),
    }
    assert schema == expected["schema_validation"], fixture.name

    manifest_path = fixture / "run_manifest.yaml"
    artifact_path = fixture / "artifact_index.yaml"
    review_path = fixture / "review_context.yaml"
    manifest = load_yaml(manifest_path) if manifest_path.exists() else None
    artifact_index = load_yaml(artifact_path) if artifact_path.exists() else None
    review = load_yaml(review_path) if review_path.exists() else None

    if manifest is None:
        findings.add("provenance_manifest_absent")
        return findings

    if schema["manifest"] == "invalid":
        if manifest.get("schema_version") != "1":
            findings.add("provenance_unsupported_schema_version")
        elif "outputs" in manifest and "results" in manifest.get("outputs", {}) and "path" not in manifest["outputs"]["results"]:
            findings.add("provenance_results_path_required")
        else:
            findings.add("provenance_manifest_schema_invalid")
        return findings

    if schema["artifact_index"] == "invalid":
        findings.add("provenance_artifact_index_schema_invalid")
        return findings

    run_root = fixture.resolve(strict=False)
    for context, desc in descriptor_paths(manifest):
        digest_finding = "provenance_output_digest_mismatch" if context in {"results", "artifact_index", "output"} else "provenance_input_digest_mismatch"
        verify_descriptor(run_root, context, desc, findings, digest_finding=digest_finding)

    if "provenance_unsafe_path" in findings or "provenance_local_file_missing" in findings or "provenance_input_digest_mismatch" in findings or "provenance_output_digest_mismatch" in findings:
        return findings

    inputs = manifest.get("inputs", []) or []
    singleton_counts = {}
    for desc in inputs:
        role = desc.get("role")
        if role in SINGLETON_ROLES:
            singleton_counts[role] = singleton_counts.get(role, 0) + 1
    if any(count > 1 for count in singleton_counts.values()):
        findings.add("provenance_duplicate_singleton_role")
        return findings

    input_by_key = {}
    for desc in inputs:
        input_by_key.setdefault(resource_key(desc), []).append(desc)
    for fixed, key in canonical_mirrors(manifest):
        mirrors = input_by_key.get(key, [])
        if not mirrors:
            continue
        mirror = mirrors[0]
        mismatch = False
        if "path" in fixed or "path" in mirror:
            mismatch = mismatch or norm_descriptor_path(run_root, fixed) != norm_descriptor_path(run_root, mirror)
        if "uri" in fixed or "uri" in mirror:
            mismatch = mismatch or fixed.get("uri") != mirror.get("uri")
        if "digest" in fixed or "digest" in mirror:
            mismatch = mismatch or not same_digest(fixed, mirror)
        if mismatch:
            findings.add("provenance_duplicate_resource_mismatch")
            return findings

    evaluator = manifest["evaluation"]["evaluator"]
    components = evaluator.get("components", []) or []
    component_ids = [c.get("id") for c in components]
    if len(component_ids) != len(set(component_ids)):
        findings.add("provenance_duplicate_hybrid_component_id")
        return findings

    started = parse_dt(manifest.get("run", {}).get("started_at"))
    completed = parse_dt(manifest.get("run", {}).get("completed_at"))
    if started and completed and started > completed:
        findings.add("provenance_timestamp_order_invalid")
        return findings

    rows = read_csv_rows(fixture / manifest["outputs"]["results"]["path"])
    candidate_allowed = {manifest["candidate"]["id"], *manifest["candidate"].get("accepted_aliases", [])}
    evaluator_allowed = {evaluator["id"], *evaluator.get("accepted_aliases", [])}
    for row in rows:
        if row["run_id"].strip() != manifest["run"]["id"]:
            findings.add("provenance_run_id_mismatch")
            return findings
        if row["candidate"].strip() not in candidate_allowed:
            findings.add("provenance_candidate_alias_mismatch")
            return findings
        if row["evaluator"].strip() not in evaluator_allowed:
            findings.add("provenance_evaluator_alias_mismatch")
            return findings

    if artifact_index is not None:
        if artifact_index.get("run_id") != manifest["run"]["id"]:
            findings.add("provenance_artifact_identity_mismatch")
            return findings
        ids = [a["artifact_id"] for a in artifact_index.get("artifacts", [])]
        if len(ids) != len(set(ids)):
            findings.add("provenance_duplicate_artifact_id")
            return findings
        artifact_root = fixture.resolve(strict=False)
        norm_paths = []
        for artifact in artifact_index.get("artifacts", []):
            verify_descriptor(artifact_root, "artifact", artifact, findings, digest_finding="provenance_output_digest_mismatch")
            path, issue = resolve_descriptor(artifact_root, artifact)
            if issue:
                findings.add(issue)
            elif path:
                norm_paths.append(path.relative_to(run_root).as_posix())
            if artifact.get("evaluator_ref") and artifact["evaluator_ref"] not in {evaluator["id"], *component_ids}:
                findings.add("provenance_artifact_identity_mismatch")
        if findings:
            return findings
        if len(norm_paths) != len(set(norm_paths)):
            findings.add("provenance_duplicate_artifact_path")
            return findings
        artifact_entries_by_path = {}
        for norm_path, artifact in zip(norm_paths, artifact_index.get("artifacts", [])):
            artifact_entries_by_path.setdefault(norm_path, []).append(artifact)
        csv_root = fixture.resolve(strict=False)
        for row in rows:
            observed = row.get("observed_output_path", "").strip()
            if not observed:
                continue
            resolved, issue = norm_rel(csv_root, observed)
            if issue:
                findings.add(issue)
                return findings
            key = resolved.relative_to(run_root).as_posix()
            matches = artifact_entries_by_path.get(key, [])
            if len(matches) != 1:
                findings.add("provenance_artifact_identity_mismatch")
                return findings
            artifact = matches[0]
            if artifact.get("case_id") != row.get("case_id") or artifact.get("trial_id") != row.get("trial_id"):
                findings.add("provenance_artifact_identity_mismatch")
                return findings

    if review is not None:
        if schema["review_context"] == "invalid":
            findings.add("provenance_review_context_schema_invalid")
            return findings
        for desc in [review.get("candidate", {}).get("artifact"), *(review.get("inputs", []) or [])]:
            if not desc:
                continue
            verify_descriptor(run_root, "review_context", desc, findings, digest_finding="provenance_review_context_digest_mismatch")
        if "provenance_review_context_digest_mismatch" in findings or "provenance_unsafe_path" in findings or "provenance_local_file_missing" in findings:
            return findings
        current_by_key = {}
        for desc in review.get("inputs", []) or []:
            current_by_key.setdefault(resource_key(desc), []).append(desc)
        if any(len(matches) > 1 for matches in current_by_key.values()):
            findings.add("provenance_duplicate_current_resource")
            return findings
        policy = review.get("recency_policy")
        observed = parse_dt(review.get("observed_at"))
        if policy and completed and observed:
            if completed > observed + timedelta(seconds=policy["max_future_clock_skew_seconds"]):
                findings.add("provenance_future_timestamp_invalid")
                return findings

    status = manifest["run"]["status"]
    if status == "failed":
        findings.add("provenance_lifecycle_failed")
    elif status == "aborted":
        findings.add("provenance_lifecycle_incomplete")

    if review is None:
        findings.add("provenance_freshness_unknown")
        return findings

    # Freshness comparison.
    if review["candidate"].get("id") != manifest["candidate"]["id"] or review["candidate"].get("version") != manifest["candidate"].get("version"):
        findings.add("provenance_candidate_stale")
    elif "artifact" in manifest.get("candidate", {}):
        current_artifact = review.get("candidate", {}).get("artifact")
        if not current_artifact or "digest" not in current_artifact:
            findings.add("provenance_freshness_unknown")
        elif manifest["candidate"]["artifact"].get("digest", {}).get("sha256") != current_artifact.get("digest", {}).get("sha256"):
            findings.add("provenance_candidate_stale")

    current_inputs = review.get("inputs", []) or []
    current_by_key = {}
    for desc in current_inputs:
        current_by_key.setdefault(resource_key(desc), []).append(desc)
    for hist in inputs:
        matches = current_by_key.get(resource_key(hist), [])
        if len(matches) != 1:
            findings.add("provenance_freshness_unknown")
            continue
        current = matches[0]
        if "digest" not in hist or "digest" not in current:
            findings.add("provenance_freshness_unknown")
        elif hist["digest"]["sha256"] != current["digest"]["sha256"]:
            findings.add("provenance_evidence_stale")

    policy = review.get("recency_policy")
    if policy:
        if not completed:
            findings.add("provenance_recency_unknown")
        else:
            observed = parse_dt(review["observed_at"])
            if observed - completed > timedelta(days=policy["max_age_days"]):
                findings.add("provenance_evidence_expired")

    return findings


def test_path_only_descriptors_are_schema_location_discovered():
    manifest = {
        "candidate": {"artifact": {"path": "inputs/candidate.yaml"}},
        "evaluation": {
            "policy": {"path": "inputs/evaluation_policy.yaml"},
            "evaluator": {"configuration": {"path": "inputs/evaluator_config.yaml"}},
        },
        "inputs": [{"role": "eval_cases", "path": "inputs/eval_cases.yaml"}],
        "outputs": {
            "results": {"path": "eval_results.csv"},
            "additional": [{"path": "outputs/summary.txt"}],
        },
    }
    review_context = {
        "candidate": {"artifact": {"path": "current/candidate.yaml"}},
        "inputs": [{"role": "eval_cases", "path": "current/eval_cases.yaml"}],
    }

    manifest_paths = {desc["path"] for _, desc in descriptor_paths(manifest)}
    review_paths = {desc["path"] for _, desc in descriptor_paths(review_context)}

    assert {
        "inputs/candidate.yaml",
        "inputs/evaluation_policy.yaml",
        "inputs/evaluator_config.yaml",
        "inputs/eval_cases.yaml",
        "eval_results.csv",
        "outputs/summary.txt",
    } <= manifest_paths
    assert {"current/candidate.yaml", "current/eval_cases.yaml"} <= review_paths


def test_path_only_descriptors_are_referenced_checked_and_not_orphans(tmp_path):
    fixture = tmp_path
    files = {
        "inputs/candidate.yaml": "candidate: local\n",
        "inputs/evaluation_policy.yaml": "policy: local\n",
        "inputs/evaluator_config.yaml": "config: local\n",
        "inputs/eval_cases.yaml": "cases: local\n",
        "outputs/summary.txt": "summary\n",
        "current/eval_cases.yaml": "cases: local\n",
        "eval_results.csv": ",".join(CSV_HEADERS) + "\n",
    }
    for rel, content in files.items():
        target = fixture / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    (fixture / "run_manifest.yaml").write_text(
        """
schema_version: "1"
run:
  id: run_001
  status: complete
candidate:
  id: candidate
  version: "1"
  artifact:
    path: inputs/candidate.yaml
evaluation:
  kind: deterministic
  evaluator:
    id: deterministic-checker
    version: "1"
    configuration:
      path: inputs/evaluator_config.yaml
  policy:
    path: inputs/evaluation_policy.yaml
inputs:
  - role: eval_cases
    path: inputs/eval_cases.yaml
outputs:
  results:
    path: eval_results.csv
  additional:
    - path: outputs/summary.txt
""".lstrip(),
        encoding="utf-8",
    )
    (fixture / "review_context.yaml").write_text(
        """
schema_version: "1"
candidate:
  id: candidate
  version: "1"
inputs:
  - role: eval_cases
    path: current/eval_cases.yaml
""".lstrip(),
        encoding="utf-8",
    )

    referenced = referenced_fixture_files(fixture)
    for rel in files:
        assert (fixture / rel).resolve(strict=False) in referenced

    findings = set()
    manifest = load_yaml(fixture / "run_manifest.yaml")
    review_context = load_yaml(fixture / "review_context.yaml")
    for context, desc in descriptor_paths(manifest):
        verify_descriptor(fixture, context, desc, findings)
    for context, desc in descriptor_paths(review_context):
        verify_descriptor(fixture, context, desc, findings)
    assert findings == set()

    exempt = {"run_manifest.yaml", "review_context.yaml"}
    orphans = [
        p.relative_to(fixture).as_posix()
        for p in fixture.rglob("*")
        if p.is_file() and p.name not in exempt and p.resolve(strict=False) not in referenced
    ]
    assert orphans == []


def test_schemas_are_draft_2020_12_valid(schemas):
    assert set(schemas) == {"manifest", "artifact_index", "review_context", "expected"}


def test_format_assertions_are_enabled(validators):
    manifest = {
        "schema_version": "1",
        "run": {"id": "run_001", "status": "complete", "started_at": "not-a-date-time"},
        "candidate": {"id": "candidate", "version": "1", "artifact": {"uri": "not a uri"}},
        "evaluation": {"kind": "human", "evaluator": {"id": "reviewer"}},
        "outputs": {"results": {"path": "eval_results.csv"}},
    }
    messages = [e.message for e in validators["manifest"].iter_errors(manifest)]
    assert any("date-time" in m for m in messages)
    assert any("uri" in m for m in messages)


def test_fixture_inventory_matches_readme():
    dirs = {p.name for p in fixture_dirs()}
    readme = (FIXTURE_ROOT / "README.md").read_text(encoding="utf-8")
    inventory = set(re.findall(r"^\| `([^`]+)` \|", readme, flags=re.MULTILINE))
    assert inventory == dirs


@pytest.mark.parametrize("fixture", fixture_dirs(), ids=lambda p: p.name)
def test_expected_yaml_is_valid(fixture, validators):
    expected_path = fixture / "expected.yaml"
    assert expected_path.exists(), fixture.name
    errors = list(validators["expected"].iter_errors(load_yaml(expected_path)))
    assert not errors, [e.message for e in errors]


@pytest.mark.parametrize("fixture", fixture_dirs(), ids=lambda p: p.name)
def test_fixture_documents_and_findings(fixture, validators):
    expected = load_yaml(fixture / "expected.yaml")
    findings = validate_fixture(fixture, validators)
    assert findings == set(expected["findings"]), fixture.name


@pytest.mark.parametrize("fixture", fixture_dirs(), ids=lambda p: p.name)
def test_fixture_has_no_orphan_evidence_files(fixture):
    exempt_names = {
        "expected.yaml",
        "run_manifest.yaml",
        "review_context.yaml",
        "README.md",
    }
    referenced = referenced_fixture_files(fixture)
    orphans = []
    for path in fixture.rglob("*"):
        if not path.is_file() or path.name in exempt_names:
            continue
        if path.resolve(strict=False) not in referenced:
            orphans.append(path.relative_to(fixture).as_posix())
    assert orphans == [], fixture.name
