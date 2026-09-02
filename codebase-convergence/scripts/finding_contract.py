#!/usr/bin/env python3
"""Materialize and validate evidence freshness for convergence findings."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
from pathlib import Path, PurePosixPath
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_FILE = SKILL_ROOT / "references" / "finding.schema.json"


def load_schema() -> dict[str, Any]:
    data = json.loads(SCHEMA_FILE.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("finding schema must be a JSON object")
    return data


SCHEMA = load_schema()
FINGERPRINT_METHOD = SCHEMA["$defs"]["evidenceBasis"]["properties"]["method"]["const"]
HASH_PATTERN = re.compile(SCHEMA["$defs"]["fileBasis"]["properties"]["sha256"]["pattern"])
ID_PATTERN = re.compile(SCHEMA["properties"]["id"]["pattern"])
TOP_LEVEL_KEYS = set(SCHEMA["properties"])
REQUIRED_KEYS = set(SCHEMA["required"])
CATEGORIES = set(SCHEMA["properties"]["category"]["enum"])
SEVERITIES = set(SCHEMA["properties"]["severity"]["enum"])
CONFIDENCES = set(SCHEMA["properties"]["confidence"]["enum"])
FRESHNESS_VALUES = set(SCHEMA["properties"]["freshness"]["enum"])
DISPOSITIONS = set(SCHEMA["properties"]["disposition"]["enum"])
EVIDENCE_SCHEMA = SCHEMA["$defs"]["evidence"]
EVIDENCE_KEYS = set(EVIDENCE_SCHEMA["properties"])
EVIDENCE_KINDS = set(EVIDENCE_SCHEMA["properties"]["kind"]["enum"])
BASIS_SCHEMA = SCHEMA["$defs"]["evidenceBasis"]
BASIS_KEYS = set(BASIS_SCHEMA["properties"])
FILE_BASIS_SCHEMA = SCHEMA["$defs"]["fileBasis"]
FILE_BASIS_KEYS = set(FILE_BASIS_SCHEMA["properties"])
FILE_ROLES = set(FILE_BASIS_SCHEMA["properties"]["role"]["enum"])
FILE_STATES = set(FILE_BASIS_SCHEMA["properties"]["state"]["enum"])
OWNER_SCHEMA = SCHEMA["$defs"]["canonicalOwner"]
OWNER_KEYS = set(OWNER_SCHEMA["properties"])
OWNER_STATUSES = set(OWNER_SCHEMA["properties"]["status"]["enum"])


def print_json(payload: Any) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))


def read_json(path: str) -> dict[str, Any]:
    raw = sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("finding must be a JSON object")
    return data


def normalized_relative_path(raw: Any) -> str:
    if not isinstance(raw, str) or not raw:
        raise ValueError("path must be a non-empty string")
    if "\\" in raw:
        raise ValueError(f"path must use forward slashes: {raw!r}")
    path = PurePosixPath(raw)
    if path.is_absolute() or not path.parts or any(part in {"", ".", ".."} for part in path.parts):
        raise ValueError(f"unsafe repository-relative path: {raw!r}")
    if path.as_posix() != raw:
        raise ValueError(f"path must be normalized: {raw!r}")
    return raw


def repository_path(root: Path, raw: str) -> Path:
    normalized_relative_path(raw)
    candidate = root
    for part in PurePosixPath(raw).parts:
        candidate /= part
        if candidate.is_symlink():
            raise ValueError(f"symlink evidence is unsupported: {raw}")
    resolved = candidate.resolve()
    if not resolved.is_relative_to(root):
        raise ValueError(f"evidence path escapes repository: {raw}")
    return resolved


def file_digest(path: Path) -> str:
    return f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"


def observe_file(root: Path, raw_path: str, role: str) -> dict[str, Any]:
    path = repository_path(root, raw_path)
    if not path.exists():
        return {"path": raw_path, "role": role, "state": "absent", "sha256": None}
    if not path.is_file():
        raise ValueError(f"evidence path is not a regular file: {raw_path}")
    return {
        "path": raw_path,
        "role": role,
        "state": "present",
        "sha256": file_digest(path),
    }


def unexpected_keys(value: dict[str, Any], allowed: set[str], label: str, errors: list[str]) -> None:
    extra = set(value) - allowed
    if extra:
        errors.append(f"{label} has unsupported keys: {sorted(extra)}")


def non_empty_string(value: Any, label: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label} must be a non-empty string")


def enum_value(value: Any, allowed: set[str], label: str, errors: list[str]) -> None:
    if not isinstance(value, str) or value not in allowed:
        errors.append(f"{label} must be one of {sorted(allowed)}")


def validate_finding(finding: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    missing = REQUIRED_KEYS - set(finding)
    if missing:
        errors.append(f"missing required fields: {sorted(missing)}")
    unexpected_keys(finding, TOP_LEVEL_KEYS, "finding", errors)

    schema_version = finding.get("schema_version")
    if isinstance(schema_version, bool) or not isinstance(schema_version, int) or schema_version != 1:
        errors.append("schema_version must be the integer 1")
    finding_id = finding.get("id")
    if not isinstance(finding_id, str) or not ID_PATTERN.fullmatch(finding_id):
        errors.append("id must match F-<stable-identifier>")
    non_empty_string(finding.get("claim"), "claim", errors)
    non_empty_string(finding.get("impact"), "impact", errors)
    enum_value(finding.get("category"), CATEGORIES, "category", errors)
    enum_value(finding.get("severity"), SEVERITIES, "severity", errors)
    enum_value(finding.get("confidence"), CONFIDENCES, "confidence", errors)
    enum_value(finding.get("freshness"), FRESHNESS_VALUES, "freshness", errors)
    enum_value(finding.get("disposition"), DISPOSITIONS, "disposition", errors)

    evidence_paths: set[str] = set()
    evidence = finding.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        errors.append("evidence must be a non-empty array")
    else:
        for index, item in enumerate(evidence):
            label = f"evidence[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{label} must be an object")
                continue
            unexpected_keys(item, EVIDENCE_KEYS, label, errors)
            kind = item.get("kind")
            enum_value(kind, EVIDENCE_KINDS, f"{label}.kind", errors)
            non_empty_string(item.get("summary"), f"{label}.summary", errors)
            raw_path = item.get("path")
            if kind == "file" and raw_path is None:
                errors.append(f"{label} file evidence requires path")
            if raw_path is not None:
                try:
                    evidence_paths.add(normalized_relative_path(raw_path))
                except ValueError as error:
                    errors.append(f"{label}.path: {error}")
            start = item.get("start_line")
            end = item.get("end_line")
            if (start is None) != (end is None):
                errors.append(f"{label} must provide start_line and end_line together")
            if start is not None:
                if isinstance(start, bool) or not isinstance(start, int) or start < 1:
                    errors.append(f"{label}.start_line must be a positive integer")
                if isinstance(end, bool) or not isinstance(end, int) or end < 1:
                    errors.append(f"{label}.end_line must be a positive integer")
                if isinstance(start, int) and isinstance(end, int) and not isinstance(start, bool) and start > end:
                    errors.append(f"{label}.end_line must not precede start_line")
                if raw_path is None:
                    errors.append(f"{label} line ranges require path")

    basis_paths: set[str] = set()
    basis = finding.get("evidence_basis")
    if not isinstance(basis, dict):
        errors.append("evidence_basis must be an object")
    else:
        unexpected_keys(basis, BASIS_KEYS, "evidence_basis", errors)
        if basis.get("method") != FINGERPRINT_METHOD:
            errors.append(f"evidence_basis.method must be {FINGERPRINT_METHOD!r}")
        worktree = basis.get("worktree_fingerprint")
        if worktree is not None and (not isinstance(worktree, str) or not HASH_PATTERN.fullmatch(worktree)):
            errors.append("evidence_basis.worktree_fingerprint must be null or sha256:<64 lowercase hex>")
        files = basis.get("files")
        if not isinstance(files, list) or not files:
            errors.append("evidence_basis.files must be a non-empty array")
        else:
            for index, item in enumerate(files):
                label = f"evidence_basis.files[{index}]"
                if not isinstance(item, dict):
                    errors.append(f"{label} must be an object")
                    continue
                unexpected_keys(item, FILE_BASIS_KEYS, label, errors)
                raw_path = item.get("path")
                try:
                    normalized = normalized_relative_path(raw_path)
                    if normalized in basis_paths:
                        errors.append(f"duplicate evidence basis path: {normalized}")
                    basis_paths.add(normalized)
                except ValueError as error:
                    errors.append(f"{label}.path: {error}")
                enum_value(item.get("role"), FILE_ROLES, f"{label}.role", errors)
                state = item.get("state")
                enum_value(state, FILE_STATES, f"{label}.state", errors)
                digest = item.get("sha256")
                if state == "present" and (not isinstance(digest, str) or not HASH_PATTERN.fullmatch(digest)):
                    errors.append(f"{label}.sha256 must identify present file content")
                if state == "absent" and digest is not None:
                    errors.append(f"{label}.sha256 must be null for an absent file")

    missing_basis = evidence_paths - basis_paths
    if missing_basis:
        errors.append(f"file-backed evidence is missing from evidence_basis: {sorted(missing_basis)}")

    owner = finding.get("canonical_owner")
    if not isinstance(owner, dict):
        errors.append("canonical_owner must be an object")
    else:
        unexpected_keys(owner, OWNER_KEYS, "canonical_owner", errors)
        status = owner.get("status")
        enum_value(status, OWNER_STATUSES, "canonical_owner.status", errors)
        if status == "confirmed":
            try:
                owner_path = normalized_relative_path(owner.get("path"))
                if owner_path not in basis_paths:
                    errors.append("confirmed canonical_owner.path must be present in evidence_basis.files")
            except ValueError as error:
                errors.append(f"canonical_owner.path: {error}")
        elif status in {"disputed", "unknown"}:
            non_empty_string(owner.get("reason"), "canonical_owner.reason", errors)

    if finding.get("disposition") == "direct-repair" and finding.get("freshness") != "current":
        errors.append("direct-repair requires freshness current")
    if finding.get("disposition") == "direct-repair" and finding.get("confidence") != "confirmed":
        errors.append("direct-repair requires confirmed confidence")
    if finding.get("disposition") == "direct-repair" and isinstance(owner, dict) and owner.get("status") != "confirmed":
        errors.append("direct-repair requires a confirmed canonical owner")
    is_architecture = finding.get("category") == "architecture-candidate"
    architecture_disposition = finding.get("disposition") == "architecture-candidate"
    if is_architecture != architecture_disposition:
        errors.append("architecture-candidate category and disposition must be used together")
    return errors


def validate_line_ranges(root: Path, finding: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    line_counts: dict[str, int] = {}
    for index, item in enumerate(finding["evidence"]):
        raw_path = item.get("path")
        end = item.get("end_line")
        if raw_path is None or end is None:
            continue
        basis_entry = next(entry for entry in finding["evidence_basis"]["files"] if entry["path"] == raw_path)
        if basis_entry["state"] == "absent":
            errors.append(f"evidence[{index}] cannot cite lines in absent file {raw_path}")
            continue
        if raw_path not in line_counts:
            path = repository_path(root, raw_path)
            try:
                line_counts[raw_path] = len(path.read_text(encoding="utf-8", errors="replace").splitlines())
            except OSError as error:
                errors.append(f"cannot read line evidence {raw_path}: {error}")
                continue
        if end > line_counts[raw_path]:
            errors.append(
                f"evidence[{index}].end_line {end} exceeds {raw_path} line count {line_counts[raw_path]}"
            )
    return errors


def stamp_finding(root: Path, finding: dict[str, Any]) -> dict[str, Any]:
    stamped = copy.deepcopy(finding)
    basis = stamped.get("evidence_basis")
    if not isinstance(basis, dict):
        raise ValueError("evidence_basis must be an object")
    unexpected = set(basis) - BASIS_KEYS
    if unexpected:
        raise ValueError(f"evidence_basis has unsupported keys: {sorted(unexpected)}")
    files = basis.get("files")
    if not isinstance(files, list) or not files:
        raise ValueError("evidence_basis.files must name at least one relevant file")

    observed: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, item in enumerate(files):
        if not isinstance(item, dict):
            raise ValueError(f"evidence_basis.files[{index}] must be an object")
        unexpected = set(item) - FILE_BASIS_KEYS
        if unexpected:
            raise ValueError(f"evidence_basis.files[{index}] has unsupported keys: {sorted(unexpected)}")
        role = item.get("role")
        if role not in FILE_ROLES:
            raise ValueError(f"evidence_basis.files[{index}].role must be one of {sorted(FILE_ROLES)}")
        raw_path = item.get("path")
        normalized = normalized_relative_path(raw_path)
        if normalized in seen:
            raise ValueError(f"duplicate evidence path: {normalized}")
        seen.add(normalized)
        observed.append(observe_file(root, normalized, role))

    stamped_basis = {
        "method": FINGERPRINT_METHOD,
        "files": sorted(observed, key=lambda item: item["path"]),
    }
    if "worktree_fingerprint" in basis:
        stamped_basis["worktree_fingerprint"] = basis["worktree_fingerprint"]
    stamped["evidence_basis"] = stamped_basis
    stamped["freshness"] = "current"
    errors = validate_finding(stamped)
    errors.extend(validate_line_ranges(root, stamped))
    if errors:
        raise ValueError(f"invalid Finding draft: {'; '.join(errors)}")
    return stamped


def check_freshness(root: Path, finding: dict[str, Any]) -> tuple[dict[str, Any], int]:
    validation_errors = validate_finding(finding)
    if validation_errors:
        return {"ok": False, "errors": validation_errors}, 2

    observations: list[dict[str, Any]] = []
    differences: list[dict[str, Any]] = []
    unavailable: list[str] = []
    for recorded in finding["evidence_basis"]["files"]:
        try:
            current = observe_file(root, recorded["path"], recorded["role"])
            observations.append(current)
            if current["state"] != recorded["state"] or current["sha256"] != recorded["sha256"]:
                differences.append({"path": recorded["path"], "recorded": recorded, "current": current})
        except (OSError, ValueError) as error:
            unavailable.append(f"{recorded['path']}: {error}")

    freshness = "unknown" if unavailable else "stale" if differences else "current"
    line_errors = validate_line_ranges(root, finding) if freshness == "current" else []
    if line_errors:
        freshness = "unknown"
        unavailable.extend(line_errors)
    recorded_freshness = finding["freshness"]
    payload = {
        "ok": freshness == "current" and recorded_freshness == "current",
        "finding_id": finding["id"],
        "freshness": freshness,
        "recorded_freshness": recorded_freshness,
        "matches_recorded_freshness": freshness == recorded_freshness,
        "eligible_for_remedy_review": finding["disposition"] == "direct-repair" and freshness == "current",
        "differences": differences,
        "unavailable": unavailable,
        "observations": observations,
    }
    return payload, 0 if payload["ok"] else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    stamp_parser = subparsers.add_parser("stamp", help="Validate a Finding draft and fingerprint its relevant files")
    stamp_parser.add_argument("--root", type=Path, required=True)
    stamp_parser.add_argument("--finding", required=True, help="JSON file path, or - for standard input")

    check_parser = subparsers.add_parser("check", help="Validate a Finding and recompute evidence freshness")
    check_parser.add_argument("--root", type=Path, required=True)
    check_parser.add_argument("--finding", required=True, help="JSON file path, or - for standard input")
    args = parser.parse_args()

    try:
        finding = read_json(args.finding)
        root = args.root.expanduser().resolve()
        if not root.is_dir():
            raise ValueError(f"repository root is not a directory: {root}")
        if args.command == "stamp":
            print_json(stamp_finding(root, finding))
            return 0
        payload, returncode = check_freshness(root, finding)
        print_json(payload)
        return returncode
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print_json({"ok": False, "error": str(error)})
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
