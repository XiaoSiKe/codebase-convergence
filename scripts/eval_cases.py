#!/usr/bin/env python3
"""Validate, materialize, and score codebase-convergence eval cases."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path, PurePosixPath
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CASES_FILE = PROJECT_ROOT / "evals" / "cases.json"
CONTRACT_FILE = PROJECT_ROOT / "evals" / "result-contract.json"
EXPECTED_KEYS = {
    "allowed_changed_paths",
    "claims_full_correctness",
    "gate",
    "mutation",
    "paused",
    "required_verification",
    "routes",
}
RESULT_KEYS = {
    "changed_files",
    "claims_full_correctness",
    "gate",
    "mutation",
    "paused",
    "routes",
    "verification",
}


def load_cases() -> list[dict[str, Any]]:
    data = json.loads(CASES_FILE.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("eval catalog must be a JSON list")
    return data


def load_contract() -> dict[str, Any]:
    data = json.loads(CONTRACT_FILE.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("fields"), dict):
        raise ValueError("result contract must contain a fields object")
    return data


def safe_relative_path(raw: str) -> PurePosixPath:
    path = PurePosixPath(raw)
    if path.is_absolute() or not path.parts or ".." in path.parts or "." in path.parts:
        raise ValueError(f"unsafe fixture path: {raw}")
    return path


def validate_cases(cases: list[dict[str, Any]], contract: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    allowed_gates = set(contract["fields"]["gate"]["allowed"])
    allowed_mutations = set(contract["fields"]["mutation"]["allowed"])
    allowed_routes = set(contract["fields"]["routes"]["allowed_items"])
    allowed_verification = set(contract["fields"]["verification"]["allowed_items"])
    for index, case in enumerate(cases):
        label = case.get("id", f"index-{index}")
        if not isinstance(label, str) or not label:
            errors.append(f"case {index}: missing id")
            continue
        if label in seen:
            errors.append(f"{label}: duplicate id")
        seen.add(label)
        if not isinstance(case.get("request"), str) or not case["request"].strip():
            errors.append(f"{label}: missing request")
        files = case.get("files")
        if not isinstance(files, dict) or not files:
            errors.append(f"{label}: files must be a non-empty object")
        else:
            for raw_path, content in files.items():
                try:
                    safe_relative_path(raw_path)
                except ValueError as error:
                    errors.append(f"{label}: {error}")
                if not isinstance(content, str):
                    errors.append(f"{label}: fixture content for {raw_path} must be a string")
        expected = case.get("expected")
        if not isinstance(expected, dict) or set(expected) != EXPECTED_KEYS:
            errors.append(f"{label}: expected keys must be {sorted(EXPECTED_KEYS)}")
        else:
            if expected["gate"] not in allowed_gates:
                errors.append(f"{label}: unsupported gate {expected['gate']!r}")
            if expected["mutation"] not in allowed_mutations:
                errors.append(f"{label}: unsupported mutation {expected['mutation']!r}")
            if not set(expected["routes"]).issubset(allowed_routes):
                errors.append(f"{label}: unsupported route in {expected['routes']!r}")
            if not set(expected["required_verification"]).issubset(allowed_verification):
                errors.append(f"{label}: unsupported verification tag")
            if expected["claims_full_correctness"] is not False:
                errors.append(f"{label}: claims_full_correctness must be false")
        git = case.get("git", {})
        if not isinstance(git, dict):
            errors.append(f"{label}: git must be an object")
        else:
            for raw_path, content in git.get("dirty_files", {}).items():
                try:
                    safe_relative_path(raw_path)
                except ValueError as error:
                    errors.append(f"{label}: {error}")
                if not isinstance(content, str):
                    errors.append(f"{label}: dirty content for {raw_path} must be a string")
    return errors


def case_by_id(cases: list[dict[str, Any]], case_id: str) -> dict[str, Any]:
    for case in cases:
        if case["id"] == case_id:
            return case
    raise ValueError(f"unknown case: {case_id}")


def validate_output_directory(output: Path) -> Path:
    output = output.expanduser().resolve()
    forbidden = {Path("/").resolve(), Path.home().resolve(), PROJECT_ROOT.resolve()}
    if output in forbidden:
        raise ValueError(f"refusing broad output path: {output}")
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        raise ValueError(f"output must be missing or empty: {output}")
    return output


def write_fixture_file(output: Path, raw_path: str, content: str) -> None:
    relative = safe_relative_path(raw_path)
    target = output.joinpath(*relative.parts)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def materialize(case: dict[str, Any], output: Path) -> dict[str, Any]:
    output = validate_output_directory(output)
    output.mkdir(parents=True, exist_ok=True)
    for raw_path, content in case["files"].items():
        write_fixture_file(output, raw_path, content)

    git = case.get("git", {})
    if git.get("initial_commit"):
        commands = (
            ["git", "init", "-b", "main"],
            ["git", "add", "."],
            [
                "git",
                "-c",
                "user.name=Convergence Eval",
                "-c",
                "user.email=eval@example.invalid",
                "commit",
                "-m",
                "fixture baseline",
            ],
        )
        for command in commands:
            subprocess.run(command, cwd=output, text=True, capture_output=True, check=True)
        for raw_path, content in git.get("dirty_files", {}).items():
            write_fixture_file(output, raw_path, content)

    return {
        "case": case["id"],
        "request": case["request"],
        "path": str(output),
        "available_specialists": case.get("available_specialists", "current environment"),
    }


def validate_result(case: dict[str, Any], result: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(result, dict):
        return ["result must be a JSON object"]
    missing = RESULT_KEYS - set(result)
    if missing:
        return [f"missing result keys: {sorted(missing)}"]
    for key in ("routes", "changed_files", "verification"):
        if not isinstance(result[key], list) or not all(isinstance(item, str) for item in result[key]):
            errors.append(f"{key} must be a list of strings")
    for key in ("paused", "claims_full_correctness"):
        if not isinstance(result[key], bool):
            errors.append(f"{key} must be a boolean")
    if not isinstance(result["gate"], str) or not isinstance(result["mutation"], str):
        errors.append("gate and mutation must be strings")
    if errors:
        return errors

    expected = case["expected"]
    contract = load_contract()
    for key in ("gate", "mutation", "paused", "claims_full_correctness"):
        if result[key] != expected[key]:
            errors.append(f"{key}: expected {expected[key]!r}, got {result[key]!r}")

    if sorted(result["routes"]) != sorted(expected["routes"]):
        errors.append(f"routes: expected {expected['routes']!r}, got {result['routes']!r}")
    unsupported_routes = set(result["routes"]) - set(contract["fields"]["routes"]["allowed_items"])
    if unsupported_routes:
        errors.append(f"unsupported routes: {sorted(unsupported_routes)}")

    changed = set(result["changed_files"])
    allowed = set(expected["allowed_changed_paths"])
    unexpected_changes = changed - allowed
    if unexpected_changes:
        errors.append(f"changed_files contains forbidden paths: {sorted(unexpected_changes)}")
    if expected["mutation"] == "none" and changed:
        errors.append("mutation is forbidden but changed_files is not empty")
    if result["mutation"] == "performed" and not changed:
        errors.append("mutation is performed but changed_files is empty")
    if result["mutation"] == "none" and changed:
        errors.append("mutation is none but changed_files is not empty")

    unsupported_verification = set(result["verification"]) - set(
        contract["fields"]["verification"]["allowed_items"]
    )
    if unsupported_verification:
        errors.append(f"unsupported verification tags: {sorted(unsupported_verification)}")
    missing_verification = set(expected["required_verification"]) - set(result["verification"])
    if missing_verification:
        errors.append(f"missing verification: {sorted(missing_verification)}")
    return errors


def print_json(payload: Any) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("validate-cases")
    subparsers.add_parser("result-contract")

    materialize_parser = subparsers.add_parser("materialize")
    materialize_parser.add_argument("--case", required=True)
    materialize_parser.add_argument("--output", type=Path, required=True)

    result_parser = subparsers.add_parser("validate-result")
    result_parser.add_argument("--case", required=True)
    result_parser.add_argument("--result", type=Path, required=True)
    args = parser.parse_args()

    try:
        cases = load_cases()
        contract = load_contract()
        errors = validate_cases(cases, contract)
        if errors:
            print_json({"ok": False, "errors": errors})
            return 1

        if args.command == "validate-cases":
            print_json({"ok": True, "case_count": len(cases)})
            return 0

        if args.command == "result-contract":
            print_json(contract)
            return 0

        case = case_by_id(cases, args.case)
        if args.command == "materialize":
            print_json(materialize(case, args.output))
            return 0

        result = json.loads(args.result.read_text(encoding="utf-8"))
        errors = validate_result(case, result)
        print_json({"ok": not errors, "errors": errors})
        return 1 if errors else 0
    except (OSError, ValueError, json.JSONDecodeError, subprocess.CalledProcessError) as error:
        print_json({"ok": False, "error": str(error)})
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
