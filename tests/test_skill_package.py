from __future__ import annotations

import re
import unittest
from collections import defaultdict, deque
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = PROJECT_ROOT / "codebase-convergence"
SKILL_FILE = SKILL_ROOT / "SKILL.md"


def markdown_links(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    return re.findall(r"\[[^\]]+\]\(([^)]+)\)", text)


def local_markdown_targets(path: Path) -> list[Path]:
    targets: list[Path] = []
    for raw_target in markdown_links(path):
        target = raw_target.split("#", 1)[0]
        if not target or "://" in target or target.startswith(("mailto:", "#")):
            continue
        targets.append((path.parent / target).resolve())
    return targets


def frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\n(.*?)\n---\n", text, flags=re.DOTALL)
    if not match:
        return {}

    values: dict[str, str] = {}
    for line in match.group(1).splitlines():
        key, separator, value = line.partition(":")
        if separator:
            values[key.strip()] = value.strip().strip('"')
    return values


class SkillPackageTests(unittest.TestCase):
    def test_skill_identity_matches_package_directory(self) -> None:
        metadata = frontmatter(SKILL_FILE)
        self.assertEqual(metadata.get("name"), SKILL_ROOT.name)
        description = metadata.get("description", "").lower()
        self.assertIn("contradictory", description)
        self.assertIn("fix bugs", description)
        self.assertIn("review code", description)
        self.assertIn("during active maintenance", description)

    def test_dual_core_is_built_in_instead_of_optional_routing(self) -> None:
        skill = SKILL_FILE.read_text(encoding="utf-8")
        routing = (SKILL_ROOT / "references" / "specialist-routing.md").read_text(encoding="utf-8")

        self.assertIn("## Two inseparable core disciplines", skill)
        self.assertIn("Precise execution", skill)
        self.assertIn("Deep-Module convergence", skill)
        self.assertNotRegex(routing, r"\| Coding or refactoring risks.*karpathy-guidelines")

    def test_every_local_markdown_link_exists_and_stays_in_project(self) -> None:
        for source in PROJECT_ROOT.rglob("*.md"):
            if ".git" in source.parts:
                continue
            for target in local_markdown_targets(source):
                with self.subTest(source=source, target=target):
                    self.assertTrue(target.is_relative_to(PROJECT_ROOT.resolve()))
                    self.assertTrue(target.exists())

    def test_every_reference_is_reachable_from_skill_entrypoint(self) -> None:
        markdown_files = {path.resolve() for path in SKILL_ROOT.rglob("*.md")}
        reachable: set[Path] = set()
        queue: deque[Path] = deque([SKILL_FILE.resolve()])

        while queue:
            source = queue.popleft()
            if source in reachable:
                continue
            reachable.add(source)
            for target in local_markdown_targets(source):
                if target.suffix == ".md" and target not in reachable:
                    queue.append(target)

        self.assertEqual(markdown_files, reachable)

    def test_ui_metadata_uses_public_name_and_exact_invocation(self) -> None:
        metadata = (SKILL_ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn('display_name: "代码整理修复大师"', metadata)
        self.assertIn("$codebase-convergence", metadata)

        short_description = re.search(r'^  short_description: "(.+)"$', metadata, re.MULTILINE)
        self.assertIsNotNone(short_description)
        assert short_description is not None
        self.assertGreaterEqual(len(short_description.group(1)), 25)
        self.assertLessEqual(len(short_description.group(1)), 64)

    def test_long_guidance_is_not_duplicated_across_documents(self) -> None:
        owners: dict[str, list[Path]] = defaultdict(list)
        for path in SKILL_ROOT.rglob("*.md"):
            text = path.read_text(encoding="utf-8")
            for paragraph in re.split(r"\n\s*\n", text):
                normalized = " ".join(paragraph.split())
                if len(normalized) >= 180 and not normalized.startswith(("|", "```")):
                    owners[normalized].append(path)

        duplicates = {
            paragraph: paths
            for paragraph, paths in owners.items()
            if len(set(paths)) > 1
        }
        self.assertEqual({}, duplicates)


if __name__ == "__main__":
    unittest.main()
