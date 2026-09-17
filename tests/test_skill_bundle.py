import hashlib
import shutil
import tempfile
import unittest
import zipfile
from pathlib import Path

from scripts.build_skill import ROOT, build


class SkillBundleTests(unittest.TestCase):
    def test_repeatable_self_contained_archive_and_both_host_layouts(self):
        with tempfile.TemporaryDirectory(prefix="jstack bundle ") as temp:
            base = Path(temp)
            first = build(base / "first")
            second = build(base / "second")
            self.assertEqual(first.read_bytes(), second.read_bytes())
            expected = hashlib.sha256(first.read_bytes()).hexdigest()
            self.assertEqual(f"{expected}  jstack-mode.zip\n", (first.parent / "SHA256SUMS").read_text())
            with zipfile.ZipFile(first) as archive:
                names = archive.namelist()
                self.assertIn("jstack-mode/LICENSE", names)
                self.assertIn("jstack-mode/SKILL.md", names)
                self.assertEqual(8, sum("/playbooks/" in name for name in names))
                for name in names:
                    self.assertTrue(name.startswith("jstack-mode/"))
                    self.assertNotIn("..", Path(name).parts)
                    self.assertFalse(name.endswith(".py"))
                for host in (".agents", ".claude"):
                    project = base / host.removeprefix(".")
                    destination = project / host / "skills"
                    destination.mkdir(parents=True)
                    archive.extractall(destination)
                    installed = destination / "jstack-mode"
                    for original in (ROOT / "skills/jstack-mode").rglob("*"):
                        if original.is_file():
                            self.assertEqual(original.read_bytes(), (installed / original.relative_to(ROOT / "skills/jstack-mode")).read_bytes())
                    self.assertFalse((project / ".jstack").exists())
                    self.assertFalse((project / "AGENTS.md").exists())
                    self.assertFalse((project / "CLAUDE.md").exists())

    def test_missing_and_outside_references_refuse_publication(self):
        for link in ("missing.md", "../../LICENSE"):
            with self.subTest(link=link), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                shutil.copytree(ROOT / "skills", root / "skills")
                shutil.copy(ROOT / "LICENSE", root / "LICENSE")
                entry = root / "skills/jstack-mode/SKILL.md"
                entry.write_text(entry.read_text() + f"\n[required]({link})\n")
                with self.assertRaises(ValueError):
                    build(root / "dist", root=root)
                self.assertFalse((root / "dist/jstack-mode.zip").exists())

    def test_unexpected_files_do_not_leak_into_release(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            shutil.copytree(ROOT / "skills", root / "skills")
            shutil.copy(ROOT / "LICENSE", root / "LICENSE")
            (root / "skills/jstack-mode/private.log").write_text("private")
            with self.assertRaises(ValueError):
                build(root / "dist", root=root)
            self.assertFalse((root / "dist/jstack-mode.zip").exists())
