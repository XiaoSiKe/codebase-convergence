from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT_ROOT / "codebase-convergence" / "scripts" / "finding_contract.py"


def run_cli(*args: str, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=PROJECT_ROOT,
        text=True,
        input=input_text,
        capture_output=True,
        check=False,
    )


def finding_draft(path: str = "src/auth.py", role: str = "canonical-owner") -> dict[str, object]:
    return {
        "schema_version": 1,
        "id": "F-auth-001",
        "claim": "Suspended users are allowed by the current branch.",
        "category": "bug",
        "severity": "high",
        "confidence": "confirmed",
        "impact": "Suspended users can enter an authenticated flow.",
        "evidence": [
            {
                "kind": "file",
                "summary": "The suspended branch returns allow.",
                "path": path,
                "start_line": 1,
                "end_line": 1,
            }
        ],
        "evidence_basis": {"files": [{"path": path, "role": role}]},
        "canonical_owner": {"status": "confirmed", "path": path},
        "disposition": "direct-repair",
    }


def stamp(root: Path, draft: dict[str, object]) -> subprocess.CompletedProcess[str]:
    return run_cli(
        "stamp",
        "--root",
        str(root),
        "--finding",
        "-",
        input_text=json.dumps(draft),
    )


def check(root: Path, finding: dict[str, object]) -> subprocess.CompletedProcess[str]:
    return run_cli(
        "check",
        "--root",
        str(root),
        "--finding",
        "-",
        input_text=json.dumps(finding),
    )


class FindingContractTests(unittest.TestCase):
    def test_stamp_creates_valid_current_finding_eligible_for_remedy_review(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "src").mkdir()
            (root / "src" / "auth.py").write_text("ALLOW_SUSPENDED = True\n", encoding="utf-8")

            stamped = stamp(root, finding_draft())
            self.assertEqual(0, stamped.returncode, stamped.stdout)
            finding = json.loads(stamped.stdout)
            checked = check(root, finding)

            self.assertEqual("current", finding["freshness"])
            self.assertEqual("sha256-file-content-v1", finding["evidence_basis"]["method"])
            self.assertRegex(finding["evidence_basis"]["files"][0]["sha256"], r"^sha256:[0-9a-f]{64}$")
            self.assertEqual(0, checked.returncode, checked.stdout)
            self.assertTrue(json.loads(checked.stdout)["eligible_for_remedy_review"])

    def test_unrelated_change_stays_current_and_relevant_change_is_stale(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "src").mkdir()
            target = root / "src" / "auth.py"
            target.write_text("ALLOW_SUSPENDED = True\n", encoding="utf-8")
            finding = json.loads(stamp(root, finding_draft()).stdout)

            (root / "notes.md").write_text("unrelated\n", encoding="utf-8")
            unrelated = check(root, finding)
            target.write_text("ALLOW_SUSPENDED = False\n", encoding="utf-8")
            relevant = check(root, finding)

            self.assertEqual(0, unrelated.returncode, unrelated.stdout)
            self.assertEqual("current", json.loads(unrelated.stdout)["freshness"])
            self.assertEqual(1, relevant.returncode, relevant.stdout)
            self.assertEqual("stale", json.loads(relevant.stdout)["freshness"])
            self.assertFalse(json.loads(relevant.stdout)["eligible_for_remedy_review"])

    def test_absent_path_is_stamped_and_becomes_stale_when_created(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            draft = finding_draft("src/missing.py", "subject")
            draft["evidence"] = [
                {"kind": "command", "summary": "The required module is absent from the repository."}
            ]
            draft["canonical_owner"] = {
                "status": "unknown",
                "reason": "The missing module has no confirmed owner.",
            }
            draft["disposition"] = "observation"
            stamped = stamp(root, draft)
            self.assertEqual(0, stamped.returncode, stamped.stdout)
            finding = json.loads(stamped.stdout)
            self.assertEqual("absent", finding["evidence_basis"]["files"][0]["state"])

            (root / "src").mkdir()
            (root / "src" / "missing.py").write_text("VALUE = 1\n", encoding="utf-8")
            checked = check(root, finding)

            self.assertEqual(1, checked.returncode, checked.stdout)
            self.assertEqual("stale", json.loads(checked.stdout)["freshness"])

    def test_check_rejects_missing_fields_and_unbacked_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "src").mkdir()
            (root / "src" / "auth.py").write_text("VALUE = 1\n", encoding="utf-8")
            finding = json.loads(stamp(root, finding_draft()).stdout)
            del finding["impact"]
            finding["evidence"][0]["path"] = "src/other.py"

            result = check(root, finding)

            self.assertEqual(2, result.returncode)
            payload = json.loads(result.stdout)
            self.assertFalse(payload["ok"])
            self.assertTrue(any("impact" in error for error in payload["errors"]))
            self.assertTrue(any("missing from evidence_basis" in error for error in payload["errors"]))

    def test_stale_finding_cannot_claim_direct_repair_and_unsafe_paths_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "src").mkdir()
            (root / "src" / "auth.py").write_text("VALUE = 1\n", encoding="utf-8")
            finding = json.loads(stamp(root, finding_draft()).stdout)
            finding["freshness"] = "stale"

            invalid = check(root, finding)
            unsafe = stamp(root, finding_draft("../outside.py", "subject"))

            self.assertEqual(2, invalid.returncode)
            self.assertTrue(any("direct-repair" in error for error in json.loads(invalid.stdout)["errors"]))
            self.assertEqual(2, unsafe.returncode)
            self.assertIn("unsafe repository-relative path", unsafe.stdout)

    def test_direct_repair_requires_confirmed_confidence_and_owner(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "src").mkdir()
            (root / "src" / "auth.py").write_text("VALUE = 1\n", encoding="utf-8")
            draft = finding_draft("src/auth.py", "subject")
            draft["confidence"] = "probable"
            draft["canonical_owner"] = {
                "status": "unknown",
                "reason": "Ownership has not been established.",
            }

            result = stamp(root, draft)

            self.assertEqual(2, result.returncode)
            self.assertIn("confirmed confidence", result.stdout)
            self.assertIn("confirmed canonical owner", result.stdout)

    def test_out_of_range_line_evidence_is_unknown_after_repository_change(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "src").mkdir()
            (root / "src" / "auth.py").write_text("VALUE = 1\n", encoding="utf-8")
            finding = json.loads(stamp(root, finding_draft()).stdout)
            finding["evidence"][0]["end_line"] = 2

            result = check(root, finding)

            self.assertEqual(1, result.returncode)
            payload = json.loads(result.stdout)
            self.assertEqual("unknown", payload["freshness"])
            self.assertTrue(any("line count" in item for item in payload["unavailable"]))

    def test_stamp_rejects_symlinked_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            outside = root.parent / f"{root.name}-outside.py"
            outside.write_text("SECRET = True\n", encoding="utf-8")
            try:
                (root / "linked.py").symlink_to(outside)
                result = stamp(root, finding_draft("linked.py", "subject"))

                self.assertEqual(2, result.returncode)
                self.assertIn("symlink evidence is unsupported", result.stdout)
            finally:
                outside.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
