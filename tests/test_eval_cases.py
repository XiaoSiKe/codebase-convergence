from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT_ROOT / "scripts" / "eval_cases.py"


def load_module():
    spec = importlib.util.spec_from_file_location("eval_cases", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load eval_cases")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


class EvalCasesTests(unittest.TestCase):
    def test_case_validation_rejects_unsafe_allowed_paths_and_invalid_dirty_files(self) -> None:
        module = load_module()
        cases = module.load_cases()
        contract = module.load_contract()

        unsafe = copy.deepcopy(cases[0])
        unsafe["expected"]["allowed_changed_paths"] = ["../outside.py"]
        unsafe_errors = module.validate_cases([unsafe], contract)

        invalid_dirty = copy.deepcopy(cases[0])
        invalid_dirty["git"] = {"dirty_files": []}
        dirty_errors = module.validate_cases([invalid_dirty], contract)

        self.assertTrue(any("unsafe fixture path" in error for error in unsafe_errors))
        self.assertTrue(any("dirty_files must be an object" in error for error in dirty_errors))

    def test_case_catalog_is_valid_and_has_seventeen_unique_cases(self) -> None:
        result = run_cli("validate-cases")
        self.assertEqual(0, result.returncode, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(17, payload["case_count"])

    def test_result_contract_exposes_types_without_case_answers(self) -> None:
        result = run_cli("result-contract")
        self.assertEqual(0, result.returncode, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(["none", "decision-required", "architecture-exploration"], payload["fields"]["gate"]["allowed"])
        self.assertEqual(["none", "performed"], payload["fields"]["mutation"]["allowed"])
        self.assertTrue(
            {
                "finding-admission",
                "evidence-freshness",
                "remedy-validation",
                "alignment-map",
                "interface-tests",
                "locality-check",
            }.issubset(
                payload["fields"]["verification"]["allowed_items"]
            )
        )
        self.assertIn("karpathy-guidelines", payload["fields"]["routes"]["allowed_items"])
        self.assertNotIn("numeric-conflict", result.stdout)

    def test_materialize_does_not_expose_expected_result(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "numeric-conflict"
            result = run_cli("materialize", "--case", "numeric-conflict", "--output", str(output))

            self.assertEqual(0, result.returncode, result.stderr)
            self.assertTrue((output / "config" / "defaults.json").exists())
            self.assertFalse((output / "expected.json").exists())
            payload = json.loads(result.stdout)
            self.assertIn("检查并修好整个项目", payload["request"])

    def test_materialize_can_create_a_dirty_git_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "dirty-worktree"
            result = run_cli("materialize", "--case", "dirty-worktree", "--output", str(output))
            self.assertEqual(0, result.returncode, result.stderr)

            status = subprocess.run(
                ["git", "status", "--short"],
                cwd=output,
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertIn("notes.txt", status.stdout)

    def test_every_case_materializes_with_valid_python_syntax(self) -> None:
        cases = json.loads((PROJECT_ROOT / "evals" / "cases.json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as temp_dir:
            for case in cases:
                with self.subTest(case=case["id"]):
                    output = Path(temp_dir) / case["id"]
                    materialized = run_cli("materialize", "--case", case["id"], "--output", str(output))
                    self.assertEqual(0, materialized.returncode, materialized.stderr)
                    compiled = subprocess.run(
                        [sys.executable, "-m", "compileall", "-q", str(output)],
                        text=True,
                        capture_output=True,
                        check=False,
                    )
                    self.assertEqual(0, compiled.returncode, compiled.stderr)

    def test_result_contract_accepts_safe_decision_and_rejects_mutation(self) -> None:
        valid = {
            "gate": "decision-required",
            "mutation": "none",
            "routes": ["core"],
            "changed_files": [],
            "verification": ["baseline"],
            "paused": True,
            "claims_full_correctness": False,
        }
        invalid = {**valid, "mutation": "performed", "changed_files": ["README.md"]}

        with tempfile.TemporaryDirectory() as temp_dir:
            valid_path = Path(temp_dir) / "valid.json"
            invalid_path = Path(temp_dir) / "invalid.json"
            valid_path.write_text(json.dumps(valid), encoding="utf-8")
            invalid_path.write_text(json.dumps(invalid), encoding="utf-8")

            accepted = run_cli("validate-result", "--case", "numeric-conflict", "--result", str(valid_path))
            rejected = run_cli("validate-result", "--case", "numeric-conflict", "--result", str(invalid_path))

            self.assertEqual(0, accepted.returncode, accepted.stderr)
            self.assertNotEqual(0, rejected.returncode)

    def test_result_contract_rejects_invalid_field_types_without_traceback(self) -> None:
        invalid = {
            "gate": "decision-required",
            "mutation": "none",
            "routes": "core",
            "changed_files": [],
            "verification": ["baseline"],
            "paused": True,
            "claims_full_correctness": False,
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            result_path = Path(temp_dir) / "invalid.json"
            result_path.write_text(json.dumps(invalid), encoding="utf-8")

            result = run_cli("validate-result", "--case", "numeric-conflict", "--result", str(result_path))

            self.assertNotEqual(0, result.returncode)
            self.assertIn("list of strings", result.stdout)
            self.assertNotIn("Traceback", result.stderr)

    def test_cross_caller_case_requires_every_root_cause_change(self) -> None:
        cases = json.loads((PROJECT_ROOT / "evals" / "cases.json").read_text(encoding="utf-8"))
        case = next(item for item in cases if item["id"] == "bug-root-cause-across-callers")
        expected = case["expected"]
        incomplete = {
            "gate": expected["gate"],
            "mutation": expected["mutation"],
            "routes": expected["routes"],
            "changed_files": ["src/checkout.py"],
            "verification": expected["required_verification"],
            "paused": expected["paused"],
            "claims_full_correctness": expected["claims_full_correctness"],
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            result_path = Path(temp_dir) / "incomplete.json"
            result_path.write_text(json.dumps(incomplete), encoding="utf-8")
            result = run_cli(
                "validate-result",
                "--case",
                "bug-root-cause-across-callers",
                "--result",
                str(result_path),
            )

            self.assertNotEqual(0, result.returncode)
            self.assertIn("missing required paths", result.stdout)
