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

    def test_empty_target_can_be_previewed_and_installed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "codebase-convergence"
            target.mkdir()

            previewed = run_cli("--dry-run", "--target", str(target))

            self.assertEqual(0, previewed.returncode, previewed.stderr)
            preview = json.loads(previewed.stdout)
            self.assertEqual("empty", preview["status"])
            self.assertTrue(preview["installable"])
            self.assertEqual([], list(target.iterdir()))

            installed = run_cli("--install", "--target", str(target))
            checked = run_cli("--check", "--target", str(target))

            self.assertEqual(0, installed.returncode, installed.stderr)
            self.assertEqual(0, checked.returncode, checked.stderr)
            self.assertEqual("current", json.loads(checked.stdout)["status"])
            manifest = json.loads((target / ".codebase-convergence-install.json").read_text(encoding="utf-8"))
            self.assertEqual(sorted(manifest["files"]), preview["add"])

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

    def test_check_refuses_a_managed_file_replaced_by_an_internal_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "codebase-convergence"
            self.assertEqual(0, run_cli("--install", "--target", str(target)).returncode)
            skill_file = target / "SKILL.md"
            preserved_copy = target / "local-skill-copy.md"
            preserved_copy.write_bytes(skill_file.read_bytes())
            skill_file.unlink()
            skill_file.symlink_to(preserved_copy.name)

            result = run_cli("--check", "--target", str(target))

            self.assertNotEqual(0, result.returncode)
            self.assertTrue(skill_file.is_symlink())
            self.assertIn("symlink", result.stdout)

    def test_check_refuses_a_symlinked_install_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "codebase-convergence"
            self.assertEqual(0, run_cli("--install", "--target", str(target)).returncode)
            manifest = target / ".codebase-convergence-install.json"
            preserved_copy = target / "local-manifest-copy.json"
            preserved_copy.write_bytes(manifest.read_bytes())
            manifest.unlink()
            manifest.symlink_to(preserved_copy.name)

            result = run_cli("--check", "--target", str(target))

            self.assertNotEqual(0, result.returncode)
            self.assertTrue(manifest.is_symlink())
            self.assertIn("manifest must not be a symlink", result.stdout)

    def test_check_refuses_a_symlinked_target_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            real_target = root / "real" / "codebase-convergence"
            alias_target = root / "alias" / "codebase-convergence"
            real_target.parent.mkdir()
            alias_target.parent.mkdir()
            self.assertEqual(0, run_cli("--install", "--target", str(real_target)).returncode)
            alias_target.symlink_to(real_target, target_is_directory=True)

            result = run_cli("--check", "--target", str(alias_target))

            self.assertEqual(2, result.returncode)
            self.assertIn("target directory must not be a symlink", result.stdout)
            self.assertTrue(alias_target.is_symlink())

    def test_install_refuses_an_unmanaged_existing_target(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "codebase-convergence"
            target.mkdir()
            (target / "SKILL.md").write_text("legacy\n", encoding="utf-8")

            result = run_cli("--install", "--target", str(target))

            self.assertNotEqual(0, result.returncode)
            self.assertEqual("legacy\n", (target / "SKILL.md").read_text(encoding="utf-8"))

    def test_hidden_files_and_subdirectories_are_not_empty_targets(self) -> None:
        for name in (".keep", "notes"):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp_dir:
                target = Path(temp_dir) / "codebase-convergence"
                target.mkdir()
                entry = target / name
                if name == ".keep":
                    entry.write_text("keep\n", encoding="utf-8")
                else:
                    entry.mkdir()

                result = run_cli("--dry-run", "--target", str(target))

                self.assertEqual(2, result.returncode)
                self.assertEqual("unmanaged", json.loads(result.stdout)["status"])
                self.assertEqual([entry], list(target.iterdir()))

    def test_managed_update_preserves_unmanaged_extra_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "codebase-convergence"
            self.assertEqual(0, run_cli("--install", "--target", str(target)).returncode)
            extra = target / "local-notes.txt"
            extra.write_text("keep me\n", encoding="utf-8")

            result = run_cli("--install", "--target", str(target))

            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual("keep me\n", extra.read_text(encoding="utf-8"))
