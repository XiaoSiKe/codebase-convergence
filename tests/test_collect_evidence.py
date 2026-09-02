from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT_ROOT / "codebase-convergence" / "scripts" / "collect_evidence.py"


def load_module():
    spec = importlib.util.spec_from_file_location("collect_evidence", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load collect_evidence")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def snapshot(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in root.rglob("*")
        if path.is_file()
    }


class CollectEvidenceTests(unittest.TestCase):
    def test_collects_inventory_commands_and_git_without_writing(self) -> None:
        module = load_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            files = {
                "AGENTS.md": "docs/generated.md is generated; do not edit it manually.\n",
                "CONTEXT.md": "# Domain\n",
                "docs/adr/0001-example.md": "# Accepted decision\n",
                "docs/generated.md": "<!-- generated; do not edit -->\n",
                "docs/prose.md": ("ordinary explanation\n" * 8) + "The phrase do not edit is discussed here.\n",
                "package.json": json.dumps({"scripts": {"test": "python3 -m unittest"}}),
                "Makefile": "lint:\n\tpython3 -m compileall src\n",
                "schema/api.json": "{}\n",
                "migrations/001.sql": "select 1;\n",
                "src/app.py": "VALUE = 1\n",
                "scripts/generate.py": "TARGET = '<!-- generated; do not edit -->'\n",
                "tests/test_app.py": "# test\n",
            }
            for relative, content in files.items():
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")

            before = snapshot(root)
            evidence = module.collect_evidence(root)

            self.assertEqual(before, snapshot(root))
            self.assertIn("AGENTS.md", evidence["inventory"]["instruction_files"])
            self.assertIn("CONTEXT.md", evidence["inventory"]["domain_files"])
            self.assertIn("docs/adr/0001-example.md", evidence["inventory"]["adr_files"])
            self.assertIn("docs/generated.md", evidence["inventory"]["generated_files"])
            self.assertNotIn("docs/prose.md", evidence["inventory"]["generated_files"])
            self.assertNotIn("AGENTS.md", evidence["inventory"]["generated_files"])
            self.assertNotIn("scripts/generate.py", evidence["inventory"]["generated_files"])
            self.assertIn("schema/api.json", evidence["inventory"]["schema_files"])
            self.assertIn("migrations/001.sql", evidence["inventory"]["migration_files"])
            self.assertIn("tests/test_app.py", evidence["inventory"]["test_files"])
            self.assertIn("npm run test", evidence["available_commands"])
            self.assertIn("make lint", evidence["available_commands"])
            self.assertFalse(evidence["git"]["is_repository"])

    def test_skips_symlinks_instead_of_reading_outside_root(self) -> None:
        module = load_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "repo"
            root.mkdir()
            outside = Path(temp_dir) / "outside.md"
            outside.write_text("secret\n", encoding="utf-8")
            (root / "linked.md").symlink_to(outside)

            evidence = module.collect_evidence(root)

            self.assertEqual(["linked.md"], evidence["coverage"]["skipped_symlinks"])
            self.assertNotIn("linked.md", evidence["inventory"]["markdown_files"])
