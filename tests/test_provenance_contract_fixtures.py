"""Contract-development checks for eval-run provenance fixtures.

This module validates provenance schemas, fixture integrity, referenced evidence,
recorded digests, orphan-file hygiene, and selected scenario invariants. Runtime
projection tests separately compare the production parser's implemented
historical, assurance, freshness, recency, and review-context classifications.
Complete authorization evaluation remains deferred.
"""

import csv
import hashlib
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path, PurePosixPath

import pytest
import yaml
from jsonschema import Draft202012Validator, FormatChecker
from openevalgate.eval_results import OPTIONAL_EVAL_RESULT_COLUMNS, REQUIRED_EVAL_RESULT_COLUMNS

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
PROVENANCE_CSV_COLUMNS = {"run_id", "case_id", "candidate", "evaluator", "observed_output_path"}
BASE_CSV_HEADERS = [*REQUIRED_EVAL_RESULT_COLUMNS, "trial_id"]


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
    return {
        name: Draft202012Validator(schema, format_checker=checker)
        for name, schema in schemas.items()
    }


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


def norm_rel(root, rel, allowed_root=None):
    if not isinstance(rel, str) or not rel:
        return None, "provenance_unsafe_path"
    if "\\" in rel or "//" in rel or rel.endswith("/") or re.match(r"^[A-Za-z]:", rel):
        return None, "provenance_unsafe_path"

    segments = rel.split("/")
    if any(part in {"", ".", ".."} for part in segments):
        return None, "provenance_unsafe_path"
    raw = PurePosixPath(rel)
    if raw.is_absolute():
        return None, "provenance_unsafe_path"

    root = Path(root)
    allowed = Path(allowed_root or root).resolve(strict=False)
    candidate = root
    for part in raw.parts:
        candidate = candidate / part
        try:
            if candidate.is_symlink():
                return None, "provenance_unsafe_path"
        except OSError:
            return None, "provenance_unsafe_path"
    full = root.joinpath(*raw.parts).resolve(strict=False)
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


def resolve_descriptor(root, descriptor, allowed_root=None):
    if "path" not in descriptor:
        return None, None
    return norm_rel(root, descriptor["path"], allowed_root=allowed_root)


def verify_descriptor(
    root,
    context,
    descriptor,
    findings,
    missing_finding="provenance_local_file_missing",
    digest_finding=None,
    allowed_root=None,
):
    if "path" not in descriptor:
        return
    path, issue = resolve_descriptor(root, descriptor, allowed_root=allowed_root)
    if issue:
        findings.add(issue)
        return
    if not path.exists() or not path.is_file():
        findings.add(missing_finding)
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


def validate_csv_headers(fieldnames, path="<csv>"):
    fieldnames = fieldnames or []
    duplicates = {name for name in fieldnames if fieldnames.count(name) > 1}
    assert not duplicates, f"Duplicate CSV headers in {path}: {sorted(duplicates)}"
    missing = [column for column in REQUIRED_EVAL_RESULT_COLUMNS if column not in fieldnames]
    missing += [
        column
        for column in PROVENANCE_CSV_COLUMNS
        if column not in fieldnames and column not in missing
    ]
    assert not missing, f"Missing CSV headers in {path}: {missing}"


def read_csv_rows(path):
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        validate_csv_headers(reader.fieldnames, path)
        return list(reader)


def normalized_optional(value):
    if value is None:
        return None
    stripped = str(value).strip()
    return stripped or None


def run_relative(path, run_root):
    return path.resolve(strict=False).relative_to(run_root.resolve(strict=False)).as_posix()


def resolve_results_path(manifest_path, manifest):
    results = manifest.get("outputs", {}).get("results", {}) if manifest else {}
    if "path" not in results:
        return None, None
    return resolve_descriptor(manifest_path.parent, results, allowed_root=manifest_path.parent)


def resolve_artifact_index_path(manifest_path, manifest):
    artifact_index = manifest.get("outputs", {}).get("artifact_index", {}) if manifest else {}
    if "path" not in artifact_index:
        return None, None
    return resolve_descriptor(
        manifest_path.parent, artifact_index, allowed_root=manifest_path.parent
    )


def referenced_fixture_files(fixture):
    referenced = set()

    def add_path(root, rel, allowed_root=None):
        resolved, issue = norm_rel(root, rel, allowed_root=allowed_root)
        if not issue and resolved.exists():
            referenced.add(resolved.resolve(strict=False))

    manifest_path = fixture / "run_manifest.yaml"
    if manifest_path.exists():
        manifest = load_yaml(manifest_path)
        run_root = manifest_path.parent.resolve(strict=False)
        for _, desc in descriptor_paths(manifest):
            if "path" in desc:
                add_path(manifest_path.parent, desc["path"], allowed_root=run_root)
        results_path, issue = resolve_results_path(manifest_path, manifest)
        if results_path and not issue and results_path.exists():
            for row in read_csv_rows(results_path):
                observed = row.get("observed_output_path", "").strip()
                if observed:
                    add_path(results_path.parent, observed, allowed_root=run_root)

        artifact_path, issue = resolve_artifact_index_path(manifest_path, manifest)
        if artifact_path and not issue and artifact_path.exists():
            artifact_index = load_yaml(artifact_path)
            for artifact in artifact_index.get("artifacts", []) or []:
                if "path" in artifact:
                    add_path(artifact_path.parent, artifact["path"], allowed_root=run_root)

    if not manifest_path.exists() and (fixture / "eval_results.csv").exists():
        referenced.add((fixture / "eval_results.csv").resolve(strict=False))

    review_path = fixture / "review_context.yaml"
    if review_path.exists():
        review = load_yaml(review_path)
        review_root = review_path.parent.resolve(strict=False)
        for _, desc in descriptor_paths(review):
            if "path" in desc:
                add_path(review_path.parent, desc["path"], allowed_root=review_root)

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
    resolved, issue = resolve_descriptor(run_root, desc, allowed_root=run_root)
    if issue:
        return None
    return run_relative(resolved, run_root)


def canonical_mirrors(manifest):
    evaluation = manifest.get("evaluation", {})
    evaluator = evaluation.get("evaluator", {})
    mirrors = []
    if "policy" in evaluation:
        mirrors.append((evaluation["policy"], ("evaluation_policy", None)))
    if "configuration" in evaluator:
        mirrors.append(
            (evaluator["configuration"], ("evaluator_configuration", evaluator.get("id")))
        )
    if "decision_policy" in evaluator:
        mirrors.append(
            (evaluator["decision_policy"], ("hybrid_decision_policy", evaluator.get("id")))
        )
    for component in evaluator.get("components", []) or []:
        if "configuration" in component:
            mirrors.append(
                (
                    component["configuration"],
                    ("evaluator_component_configuration", component.get("id")),
                )
            )
    return mirrors


def contains_unsafe_local_path(doc):
    for _, desc in descriptor_paths(doc):
        if "path" in desc and norm_rel(Path("."), desc["path"])[1] == "provenance_unsafe_path":
            return True
    return False


def validate_fixture(fixture, validators):
    expected = load_yaml(fixture / "expected.yaml")
    findings = set()
    manifest_path = fixture / "run_manifest.yaml"
    review_path = fixture / "review_context.yaml"
    manifest = load_yaml(manifest_path) if manifest_path.exists() else None
    artifact_path, artifact_path_issue = (None, None)
    if manifest is not None:
        artifact_path, artifact_path_issue = resolve_artifact_index_path(manifest_path, manifest)
    schema = {
        "manifest": schema_status(manifest_path, validators["manifest"]),
        "artifact_index": schema_status(artifact_path, validators["artifact_index"])
        if artifact_path
        else "not_present",
        "review_context": schema_status(review_path, validators["review_context"]),
    }
    assert schema == expected["schema_validation"], fixture.name

    artifact_index = load_yaml(artifact_path) if artifact_path and artifact_path.exists() else None
    review = load_yaml(review_path) if review_path.exists() else None

    if manifest is None:
        findings.add("provenance_manifest_absent")
        if (fixture / "eval_results.csv").is_file():
            findings.add("provenance_results_unbound")
        return findings

    if schema["manifest"] == "invalid":
        if manifest.get("schema_version") != "1":
            findings.add("provenance_unsupported_schema_version")
        elif (
            "outputs" in manifest
            and "results" in manifest.get("outputs", {})
            and "path" not in manifest["outputs"]["results"]
        ):
            findings.add("provenance_results_path_required")
        elif contains_unsafe_local_path(manifest):
            findings.add("provenance_unsafe_path")
        else:
            findings.add("provenance_manifest_schema_invalid")
        return findings

    if artifact_path_issue:
        findings.add(artifact_path_issue)
        return findings

    if schema["artifact_index"] == "invalid":
        findings.add("provenance_artifact_index_schema_invalid")
        return findings

    run_root = manifest_path.parent.resolve(strict=False)
    for context, desc in descriptor_paths(manifest):
        digest_finding = (
            "provenance_output_digest_mismatch"
            if context in {"results", "artifact_index", "output"}
            else "provenance_input_digest_mismatch"
        )
        verify_descriptor(
            manifest_path.parent,
            context,
            desc,
            findings,
            digest_finding=digest_finding,
            allowed_root=run_root,
        )

    if findings & {
        "provenance_unsafe_path",
        "provenance_local_file_missing",
        "provenance_input_digest_mismatch",
        "provenance_output_digest_mismatch",
    }:
        return findings

    inputs = manifest.get("inputs", []) or []
    input_by_key = {}
    for desc in inputs:
        input_by_key.setdefault(resource_key(desc), []).append(desc)
    for key, matches in input_by_key.items():
        if len(matches) <= 1:
            continue
        if key[0] in SINGLETON_ROLES:
            findings.add("provenance_duplicate_singleton_role")
        else:
            findings.add("provenance_duplicate_historical_resource")
        return findings

    missing_canonical_mirror = False
    for fixed, key in canonical_mirrors(manifest):
        mirrors = input_by_key.get(key, [])
        if not mirrors:
            missing_canonical_mirror = True
            continue
        mirror = mirrors[0]
        mismatch = False
        if "path" in fixed or "path" in mirror:
            mismatch = mismatch or norm_descriptor_path(run_root, fixed) != norm_descriptor_path(
                run_root, mirror
            )
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

    results_path, issue = resolve_results_path(manifest_path, manifest)
    if issue:
        findings.add(issue)
        return findings
    rows = read_csv_rows(results_path)
    candidate_allowed = {
        manifest["candidate"]["id"],
        *manifest["candidate"].get("accepted_aliases", []),
    }
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
        artifact_root = artifact_path.parent.resolve(strict=False)
        norm_paths = []
        for artifact in artifact_index.get("artifacts", []):
            verify_descriptor(
                artifact_root,
                "artifact",
                artifact,
                findings,
                digest_finding="provenance_output_digest_mismatch",
                allowed_root=run_root,
            )
            path, issue = resolve_descriptor(artifact_root, artifact, allowed_root=run_root)
            if issue:
                findings.add(issue)
            elif path:
                norm_paths.append(run_relative(path, run_root))
            if artifact.get("evaluator_ref") and artifact["evaluator_ref"] not in {
                evaluator["id"],
                *component_ids,
            }:
                findings.add("provenance_artifact_identity_mismatch")
        if findings:
            return findings
        if len(norm_paths) != len(set(norm_paths)):
            findings.add("provenance_duplicate_artifact_path")
            return findings
        artifact_entries_by_path = {}
        for norm_path, artifact in zip(norm_paths, artifact_index.get("artifacts", [])):
            artifact_entries_by_path.setdefault(norm_path, []).append(artifact)
        for row in rows:
            observed = row.get("observed_output_path", "").strip()
            if not observed:
                continue
            resolved, issue = norm_rel(results_path.parent, observed, allowed_root=run_root)
            if issue:
                findings.add(issue)
                return findings
            key = run_relative(resolved, run_root)
            matches = artifact_entries_by_path.get(key, [])
            if len(matches) != 1:
                findings.add("provenance_artifact_identity_mismatch")
                return findings
            artifact = matches[0]

            artifact_case_id = normalized_optional(artifact.get("case_id"))
            csv_case_id = normalized_optional(row.get("case_id"))

            artifact_trial_id = normalized_optional(artifact.get("trial_id"))
            csv_trial_id = normalized_optional(row.get("trial_id"))

            if (artifact_case_id is not None and artifact_case_id != csv_case_id) or (
                artifact_trial_id is not None and artifact_trial_id != csv_trial_id
            ):
                findings.add("provenance_artifact_identity_mismatch")
                return findings

    if review is not None:
        if schema["review_context"] == "invalid":
            findings.add("provenance_review_context_schema_invalid")
            return findings
        review_root = review_path.parent.resolve(strict=False)
        for desc in [
            review.get("candidate", {}).get("artifact"),
            *(review.get("inputs", []) or []),
        ]:
            if not desc:
                continue
            verify_descriptor(
                review_path.parent,
                "review_context",
                desc,
                findings,
                digest_finding="provenance_review_context_digest_mismatch",
                allowed_root=review_root,
            )
        if findings & {
            "provenance_review_context_digest_mismatch",
            "provenance_unsafe_path",
            "provenance_local_file_missing",
        }:
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
    if missing_canonical_mirror:
        findings.add("provenance_freshness_unknown")
    if review["candidate"].get("id") != manifest["candidate"]["id"] or review["candidate"].get(
        "version"
    ) != manifest["candidate"].get("version"):
        findings.add("provenance_candidate_stale")
    elif "artifact" in manifest.get("candidate", {}):
        current_artifact = review.get("candidate", {}).get("artifact")
        if not current_artifact or "digest" not in current_artifact:
            findings.add("provenance_freshness_unknown")
        elif manifest["candidate"]["artifact"].get("digest", {}).get(
            "sha256"
        ) != current_artifact.get("digest", {}).get("sha256"):
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
        "eval_results.csv": ",".join(BASE_CSV_HEADERS) + "\n",
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


def _symlink_or_skip(link, target, *, target_is_directory=False):
    try:
        link.symlink_to(target, target_is_directory=target_is_directory)
    except (OSError, NotImplementedError) as exc:
        pytest.skip(f"symlink creation unavailable on this platform: {exc}")


def test_path_validation_rejects_final_component_symlink(tmp_path):
    target = tmp_path / "target.txt"
    target.write_text("inside\n", encoding="utf-8")
    link = tmp_path / "link.txt"
    _symlink_or_skip(link, target)
    assert norm_rel(tmp_path, "link.txt") == (None, "provenance_unsafe_path")


def test_path_validation_rejects_intermediate_directory_symlink(tmp_path):
    real_dir = tmp_path / "real"
    real_dir.mkdir()
    (real_dir / "file.txt").write_text("inside\n", encoding="utf-8")
    link_dir = tmp_path / "linked"
    _symlink_or_skip(link_dir, real_dir, target_is_directory=True)
    assert norm_rel(tmp_path, "linked/file.txt") == (None, "provenance_unsafe_path")


def test_path_validation_rejects_symlink_to_inside_fixture(tmp_path):
    target = tmp_path / "safe" / "target.txt"
    target.parent.mkdir()
    target.write_text("inside\n", encoding="utf-8")
    link = tmp_path / "safe-link.txt"
    _symlink_or_skip(link, target)
    assert norm_rel(tmp_path, "safe-link.txt") == (None, "provenance_unsafe_path")


def test_path_validation_rejects_symlink_to_outside_fixture(tmp_path):
    outside = tmp_path.parent / f"{tmp_path.name}-outside.txt"
    outside.write_text("outside\n", encoding="utf-8")
    link = tmp_path / "outside-link.txt"
    _symlink_or_skip(link, outside)
    assert norm_rel(tmp_path, "outside-link.txt") == (None, "provenance_unsafe_path")


@pytest.mark.parametrize(
    "unsafe",
    [
        "/absolute.txt",
        "C:/absolute.txt",
        "C:relative.txt",
        "//server/share/file.txt",
        r"dir\\file.txt",
        "inputs/../file.txt",
    ],
)
def test_path_validation_rejects_portable_unsafe_forms(tmp_path, unsafe):
    assert norm_rel(tmp_path, unsafe) == (None, "provenance_unsafe_path")


def test_path_validation_accepts_ordinary_safe_nested_path(tmp_path):
    target = tmp_path / "nested" / "safe.txt"
    target.parent.mkdir()
    target.write_text("safe\n", encoding="utf-8")
    resolved, issue = norm_rel(tmp_path, "nested/safe.txt")
    assert issue is None
    assert resolved == target.resolve(strict=False)


@pytest.mark.parametrize("unsafe", [".", "./file.txt", "inputs/./file.txt", "inputs/."])
def test_path_validation_rejects_dot_segments(tmp_path, unsafe):
    assert norm_rel(tmp_path, unsafe) == (None, "provenance_unsafe_path")


def test_nested_resolution_roots_follow_declaring_file(tmp_path):
    fixture = tmp_path
    results = fixture / "evidence" / "eval_results.csv"
    artifact_index_path = fixture / "evidence" / "metadata" / "artifact_index.yaml"
    artifact = fixture / "evidence" / "metadata" / "artifacts" / "case_001.md"
    current = fixture / "review" / "current" / "eval_cases.yaml"
    for target, content in [
        (
            results,
            ",".join(BASE_CSV_HEADERS)
            + "\nrun_001,case_001,candidate,reviewer,support,support,true,true,1.0,,,,qa,2026-06-18T17:13:00Z,,\n",
        ),
        (
            artifact_index_path,
            "schema_version: '1'\nrun_id: run_001\nartifacts:\n  - artifact_id: output-001\n    artifact_type: text\n    path: artifacts/case_001.md\n",
        ),
        (artifact, "output\n"),
        (current, "cases: current\n"),
    ]:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    manifest = {
        "outputs": {
            "results": {"path": "evidence/eval_results.csv"},
            "artifact_index": {"path": "evidence/metadata/artifact_index.yaml"},
        }
    }
    manifest_path = fixture / "run_manifest.yaml"
    manifest_path.write_text("placeholder\n", encoding="utf-8")
    resolved_results, issue = resolve_results_path(manifest_path, manifest)
    assert issue is None
    assert resolved_results == results.resolve(strict=False)
    resolved_index, issue = resolve_artifact_index_path(manifest_path, manifest)
    assert issue is None
    assert resolved_index == artifact_index_path.resolve(strict=False)

    loaded_index = load_yaml(artifact_index_path)
    resolved_artifact, issue = resolve_descriptor(
        artifact_index_path.parent, loaded_index["artifacts"][0], allowed_root=fixture
    )
    assert issue is None
    assert resolved_artifact == artifact.resolve(strict=False)
    resolved_observed, issue = norm_rel(
        results.parent, "metadata/artifacts/case_001.md", allowed_root=fixture
    )
    assert issue is None
    assert resolved_observed == artifact.resolve(strict=False)
    review_context = {
        "candidate": {"id": "candidate", "version": "1"},
        "inputs": [{"role": "eval_cases", "path": "current/eval_cases.yaml"}],
    }
    review_path = fixture / "review" / "review_context.yaml"
    resolved_current, issue = resolve_descriptor(
        review_path.parent, review_context["inputs"][0], allowed_root=review_path.parent
    )
    assert issue is None
    assert resolved_current == current.resolve(strict=False)


def _write_csv(path, headers):
    path.write_text(",".join(headers) + "\n", encoding="utf-8")


def test_csv_headers_accept_required_columns_in_different_order(tmp_path):
    headers = list(reversed(REQUIRED_EVAL_RESULT_COLUMNS))
    path = tmp_path / "eval_results.csv"
    _write_csv(path, headers)
    assert read_csv_rows(path) == []


def test_csv_headers_accept_known_optional_and_extra_columns(tmp_path):
    headers = [
        *REQUIRED_EVAL_RESULT_COLUMNS,
        *OPTIONAL_EVAL_RESULT_COLUMNS,
        "project_specific_extra",
    ]
    path = tmp_path / "eval_results.csv"
    _write_csv(path, headers)
    assert read_csv_rows(path) == []


def test_csv_headers_reject_missing_required_column(tmp_path):
    headers = [column for column in REQUIRED_EVAL_RESULT_COLUMNS if column != "candidate"]
    path = tmp_path / "eval_results.csv"
    _write_csv(path, headers)
    with pytest.raises(AssertionError, match="Missing CSV headers"):
        read_csv_rows(path)


def test_csv_headers_reject_duplicate_column_names(tmp_path):
    headers = [*REQUIRED_EVAL_RESULT_COLUMNS, "run_id"]
    path = tmp_path / "eval_results.csv"
    _write_csv(path, headers)
    with pytest.raises(AssertionError, match="Duplicate CSV headers"):
        read_csv_rows(path)


def test_blank_csv_trial_id_matches_absent_artifact_trial_id(tmp_path):
    rows = [{"case_id": " case_001 ", "trial_id": ""}]
    artifact = {"case_id": "case_001"}
    assert artifact.get("case_id") == rows[0].get("case_id", "").strip()
    assert normalized_optional(artifact.get("trial_id")) == normalized_optional(
        rows[0].get("trial_id")
    )


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


@pytest.mark.parametrize("unsafe", [".", "./file.txt", "inputs/./file.txt", "inputs/."])
def test_relative_path_schemas_reject_dot_segments(schemas, unsafe):
    for schema_name in ("manifest", "artifact_index", "review_context"):
        validator = Draft202012Validator(schemas[schema_name]["$defs"]["relativePath"])
        assert list(validator.iter_errors(unsafe))


@pytest.mark.parametrize("safe", [".hidden", "inputs/.hidden", "inputs/.config/file.yaml"])
def test_relative_path_schemas_allow_hidden_names(schemas, safe):
    for schema_name in ("manifest", "artifact_index", "review_context"):
        validator = Draft202012Validator(schemas[schema_name]["$defs"]["relativePath"])
        assert list(validator.iter_errors(safe)) == []


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
