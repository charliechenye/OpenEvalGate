"""Eval-run identity inspection for provenance-gated evidence."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker

from openevalgate.local_paths import resolve_local_evidence_path
from openevalgate.resources.schemas import (
    ARTIFACT_INDEX_SCHEMA_NAME,
    MANIFEST_SCHEMA_NAME,
    load_schema,
)


class RunIdentityStatus(str, Enum):
    COMPLETE = "complete"
    LEGACY = "legacy"
    INVALID = "invalid"


@dataclass(frozen=True, kw_only=True)
class ProvenanceFinding:
    id: str
    path: str
    message: str


@dataclass(frozen=True, kw_only=True)
class EvaluatorIdentity:
    kind: str
    evaluator_id: str
    evaluator_version: str | None
    accepted_aliases: tuple[str, ...]
    component_ids: tuple[str, ...]


@dataclass(frozen=True, kw_only=True)
class RunIdentity:
    run_id: str
    run_status: str
    candidate_id: str
    candidate_version: str
    candidate_accepted_aliases: tuple[str, ...]
    evaluator: EvaluatorIdentity
    framework_id: str | None
    framework_version: str | None
    results_path: Path
    artifact_index_path: Path | None


@dataclass(frozen=True, kw_only=True)
class RunIdentityInspection:
    status: RunIdentityStatus
    manifest_path: Path | None
    identity: RunIdentity | None
    findings: tuple[ProvenanceFinding, ...]
    results_present: bool

    @property
    def authoritative_results_path(self) -> Path | None:
        if self.status == RunIdentityStatus.COMPLETE and self.identity is not None:
            return self.identity.results_path
        if self.status == RunIdentityStatus.LEGACY and self.results_present:
            return self.manifest_path
        return None


_FINDING_ORDER = {
    "provenance_unsupported_schema_version": 0,
    "provenance_results_path_required": 1,
    "provenance_manifest_schema_invalid": 2,
    "provenance_artifact_index_schema_invalid": 3,
    "provenance_unsafe_path": 4,
    "provenance_local_file_missing": 5,
    "provenance_run_id_mismatch": 6,
    "provenance_candidate_alias_mismatch": 7,
    "provenance_evaluator_alias_mismatch": 8,
    "provenance_artifact_identity_mismatch": 9,
    "provenance_duplicate_artifact_id": 10,
    "provenance_duplicate_artifact_path": 11,
    "provenance_duplicate_hybrid_component_id": 12,
    "provenance_lifecycle_failed": 13,
    "provenance_lifecycle_incomplete": 14,
    "provenance_manifest_absent": 15,
}

_MANIFEST_VALIDATOR = Draft202012Validator(
    load_schema(MANIFEST_SCHEMA_NAME),
    format_checker=FormatChecker(),
)
_ARTIFACT_INDEX_VALIDATOR = Draft202012Validator(
    load_schema(ARTIFACT_INDEX_SCHEMA_NAME),
    format_checker=FormatChecker(),
)


def inspect_run_identity(
    project_dir: str | Path,
    *,
    selected_run_id: str | None = None,
    selected_candidate: str | None = None,
) -> RunIdentityInspection:
    """Inspect the authoritative eval-run identity for a project."""

    root = Path(project_dir)
    root_results = root / "eval_results.csv"
    root_manifest = root / "run_manifest.yaml"
    selected_run = selected_run_id.strip() if selected_run_id else None
    selected_candidate_value = selected_candidate.strip() if selected_candidate else None

    authoritative: Path | None = None
    compare_root = False
    if selected_run:
        scoped = root / "eval_runs" / selected_run / "run_manifest.yaml"
        if scoped.is_file():
            authoritative = scoped
            compare_root = root_manifest.is_file()
        elif root_manifest.is_file():
            root_run = _read_declared_run_id(root_manifest)
            if root_run == selected_run:
                authoritative = root_manifest
    elif root_manifest.is_file():
        authoritative = root_manifest

    if authoritative is None:
        findings = ()
        if not root_results.is_file():
            findings = (
                ProvenanceFinding(
                    id="provenance_manifest_absent",
                    path=str(root / "run_manifest.yaml"),
                    message="No versioned run manifest was provided.",
                ),
            )
        return RunIdentityInspection(
            status=RunIdentityStatus.LEGACY,
            manifest_path=root_results if root_results.is_file() else None,
            identity=None,
            findings=findings,
            results_present=root_results.is_file(),
        )

    loaded = _load_manifest(authoritative)
    if loaded[0] is None:
        return _invalid(authoritative, loaded[1])
    manifest = loaded[0]
    identity, findings_tuple = _identity_from_manifest(authoritative, manifest)
    findings = list(findings_tuple)
    if identity is None:
        return _invalid(authoritative, list(findings_tuple))

    if selected_run and identity.run_id != selected_run:
        findings.append(
            ProvenanceFinding(
                id="provenance_run_id_mismatch",
                path=f"{authoritative}:run.id",
                message="Manifest run ID does not match the selected run.",
            )
        )
    if selected_candidate_value and selected_candidate_value not in {
        identity.candidate_id,
        *identity.candidate_accepted_aliases,
    }:
        findings.append(
            ProvenanceFinding(
                id="provenance_candidate_alias_mismatch",
                path=f"{authoritative}:candidate.id",
                message="Manifest candidate identity does not match the selected candidate.",
            )
        )

    if compare_root:
        root_loaded = _load_manifest(root_manifest)
        if root_loaded[0] is not None:
            root_identity, root_findings = _identity_from_manifest(root_manifest, root_loaded[0])
            if root_identity is not None and root_identity.run_id == identity.run_id:
                if _identity_signature(root_identity) != _identity_signature(identity):
                    findings.append(
                        ProvenanceFinding(
                            id="provenance_run_id_mismatch",
                            path=str(root_manifest),
                            message="Root and run-scoped manifests disagree for the selected run identity.",
                        )
                    )
            elif root_findings:
                findings.extend(root_findings)

    sorted_findings = _sort_findings(findings)
    invalid_findings = [f for f in sorted_findings if f.id not in _lifecycle_finding_ids()]
    return RunIdentityInspection(
        status=RunIdentityStatus.INVALID if invalid_findings else RunIdentityStatus.COMPLETE,
        manifest_path=authoritative,
        identity=None if invalid_findings else identity,
        findings=sorted_findings,
        results_present=identity.results_path.is_file(),
    )


def _read_declared_run_id(path: Path) -> str | None:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001 - non-authoritative malformed roots are ignored.
        return None
    if not isinstance(data, dict):
        return None
    run = data.get("run")
    if not isinstance(run, dict):
        return None
    value = run.get("id")
    return value if isinstance(value, str) else None


def _load_manifest(path: Path) -> tuple[dict[str, Any] | None, list[ProvenanceFinding]]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        return None, [
            ProvenanceFinding(
                id="provenance_manifest_schema_invalid",
                path=str(path),
                message=f"Could not parse run manifest: {exc}",
            )
        ]
    if not isinstance(data, dict):
        return None, [
            ProvenanceFinding(
                id="provenance_manifest_schema_invalid",
                path=str(path),
                message="Run manifest must be a YAML object.",
            )
        ]
    version = data.get("schema_version")
    if version != "1":
        return None, [
            ProvenanceFinding(
                id="provenance_unsupported_schema_version",
                path=f"{path}:schema_version",
                message='Run manifest schema_version must be exactly "1".',
            )
        ]
    results = data.get("outputs", {}).get("results") if isinstance(data.get("outputs"), dict) else None
    if isinstance(results, dict) and "path" not in results:
        return None, [
            ProvenanceFinding(
                id="provenance_results_path_required",
                path=f"{path}:outputs.results",
                message="Manifest results must declare a local path.",
            )
        ]
    errors = sorted(_MANIFEST_VALIDATOR.iter_errors(data), key=lambda item: list(item.path))
    if errors:
        return None, [
            ProvenanceFinding(
                id="provenance_manifest_schema_invalid",
                path=f"{path}:{'.'.join(str(part) for part in errors[0].path)}",
                message=errors[0].message,
            )
        ]
    return data, []


def _identity_from_manifest(
    path: Path,
    manifest: dict[str, Any],
) -> tuple[RunIdentity | None, list[ProvenanceFinding]]:
    findings: list[ProvenanceFinding] = []
    run = manifest["run"]
    candidate = manifest["candidate"]
    evaluation = manifest["evaluation"]
    evaluator = evaluation["evaluator"]
    kind = evaluation["kind"]

    component_ids = tuple(str(component["id"]) for component in evaluator.get("components", []) or [])
    if len(component_ids) != len(set(component_ids)):
        findings.append(
            ProvenanceFinding(
                id="provenance_duplicate_hybrid_component_id",
                path=f"{path}:evaluation.evaluator.components",
                message="Hybrid evaluator component IDs must be unique.",
            )
        )
        return None, _sort_findings(findings)

    results_resolution = resolve_local_evidence_path(
        path.parent,
        manifest["outputs"]["results"]["path"],
        allowed_root=path.parent,
        require_file=True,
    )
    if results_resolution.error is not None:
        findings.append(_path_finding(results_resolution.error, f"{path}:outputs.results.path"))
        return None, _sort_findings(findings)

    artifact_index_path: Path | None = None
    artifact_index = manifest["outputs"].get("artifact_index")
    if isinstance(artifact_index, dict) and "path" in artifact_index:
        artifact_resolution = resolve_local_evidence_path(
            path.parent,
            artifact_index["path"],
            allowed_root=path.parent,
            require_file=True,
        )
        if artifact_resolution.error is not None:
            findings.append(_path_finding(artifact_resolution.error, f"{path}:outputs.artifact_index.path"))
            return None, _sort_findings(findings)
        artifact_index_path = artifact_resolution.path

    run_status = str(run["status"])
    if run_status == "failed":
        findings.append(
            ProvenanceFinding(
                id="provenance_lifecycle_failed",
                path=f"{path}:run.status",
                message="The eval run lifecycle is failed.",
            )
        )
    elif run_status == "aborted":
        findings.append(
            ProvenanceFinding(
                id="provenance_lifecycle_incomplete",
                path=f"{path}:run.status",
                message="The eval run lifecycle is incomplete.",
            )
        )

    framework = evaluation.get("framework") or {}
    identity = RunIdentity(
        run_id=str(run["id"]),
        run_status=run_status,
        candidate_id=str(candidate["id"]),
        candidate_version=str(candidate["version"]),
        candidate_accepted_aliases=tuple(str(value) for value in candidate.get("accepted_aliases", ()) or ()),
        evaluator=EvaluatorIdentity(
            kind=str(kind),
            evaluator_id=str(evaluator["id"]),
            evaluator_version=str(evaluator["version"]) if "version" in evaluator else None,
            accepted_aliases=tuple(str(value) for value in evaluator.get("accepted_aliases", ()) or ()),
            component_ids=component_ids,
        ),
        framework_id=str(framework["id"]) if "id" in framework else None,
        framework_version=str(framework["version"]) if "version" in framework else None,
        results_path=results_resolution.path,
        artifact_index_path=artifact_index_path,
    )
    return identity, _sort_findings(findings)


def _path_finding(error: str, path: str) -> ProvenanceFinding:
    if error in {"missing", "symlink"}:
        return ProvenanceFinding(
            id="provenance_local_file_missing",
            path=path,
            message="Referenced local evidence is missing or is not a regular file.",
        )
    return ProvenanceFinding(
        id="provenance_unsafe_path",
        path=path,
        message="Referenced local evidence path is unsafe.",
    )


def _identity_signature(identity: RunIdentity) -> tuple[Any, ...]:
    return (
        identity.run_id,
        identity.run_status,
        identity.candidate_id,
        identity.candidate_version,
        identity.candidate_accepted_aliases,
        identity.evaluator.kind,
        identity.evaluator.evaluator_id,
        identity.evaluator.evaluator_version,
        identity.evaluator.accepted_aliases,
        identity.evaluator.component_ids,
        identity.framework_id,
        identity.framework_version,
        identity.results_path.resolve(strict=False),
        identity.artifact_index_path.resolve(strict=False) if identity.artifact_index_path else None,
    )


def _invalid(path: Path, findings: list[ProvenanceFinding]) -> RunIdentityInspection:
    return RunIdentityInspection(
        status=RunIdentityStatus.INVALID,
        manifest_path=path,
        identity=None,
        findings=tuple(_sort_findings(findings)),
        results_present=False,
    )


def _sort_findings(findings: list[ProvenanceFinding]) -> tuple[ProvenanceFinding, ...]:
    return tuple(sorted(findings, key=lambda item: (_FINDING_ORDER.get(item.id, 99), item.path, item.message)))


def _lifecycle_finding_ids() -> set[str]:
    return {"provenance_lifecycle_failed", "provenance_lifecycle_incomplete"}
