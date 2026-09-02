from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT_ROOT / "scripts" / "install_local.py"


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


class InstallLocalTests(unittest.TestCase):
    def test_dry_run_never_creates_the_target(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "codebase-convergence"
            result = run_cli("--dry-run", "--target", str(target))

            self.assertEqual(0, result.returncode, result.stderr)
            self.assertFalse(target.exists())
            self.assertEqual("missing", json.loads(result.stdout)["status"])

    def test_install_then_check_reports_current(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "codebase-convergence"
            installed = run_cli("--install", "--target", str(target))
            checked = run_cli("--check", "--target", str(target))

            self.assertEqual(0, installed.returncode, installed.stderr)
            self.assertEqual(0, checked.returncode, checked.stderr)
            self.assertTrue((target / "SKILL.md").exists())
            self.assertTrue((target / ".codebase-convergence-install.json").exists())
            self.assertEqual("current", json.loads(checked.stdout)["status"])

    def test_install_refuses_to_overwrite_a_locally_modified_managed_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "codebase-convergence"
            self.assertEqual(0, run_cli("--install", "--target", str(target)).returncode)
            skill_file = target / "SKILL.md"
            skill_file.write_text("local customization\n", encoding="utf-8")

            result = run_cli("--install", "--target", str(target))

            self.assertNotEqual(0, result.returncode)
            self.assertEqual("local customization\n", skill_file.read_text(encoding="utf-8"))

    def test_install_refuses_an_unmanaged_existing_target(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "codebase-convergence"
            target.mkdir()
            (target / "SKILL.md").write_text("legacy\n", encoding="utf-8")

            result = run_cli("--install", "--target", str(target))

            self.assertNotEqual(0, result.returncode)
            self.assertEqual("legacy\n", (target / "SKILL.md").read_text(encoding="utf-8"))

    def test_managed_update_preserves_unmanaged_extra_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "codebase-convergence"
            self.assertEqual(0, run_cli("--install", "--target", str(target)).returncode)
            extra = target / "local-notes.txt"
            extra.write_text("keep me\n", encoding="utf-8")

            result = run_cli("--install", "--target", str(target))

            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual("keep me\n", extra.read_text(encoding="utf-8"))
