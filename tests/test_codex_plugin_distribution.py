"""Isolated positive/negative cases for the source-of-truth plugin mirror."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "sync-codex-plugin.py"


class PluginDistributionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.create_fixture(self.root)

    def create_fixture(self, root):
        src = root / "visual-design-review"
        (src / "references").mkdir(parents=True)
        (src / "SKILL.md").write_text(
            "---\nname: visual-design-review\ndescription: Design review.\n---\n"
            "\n[ref](references/guide.md)\n", encoding="utf-8"
        )
        (src / "references" / "guide.md").write_text("canonical", encoding="utf-8")
        for rel in [".agents/plugins/marketplace.json",
                    "plugins/visual-design-review/.codex-plugin/plugin.json"]:
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / rel, path)

    def run_script(self, flag, root=None):
        return subprocess.run([sys.executable, str(SCRIPT), flag,
                               "--root", str(root or self.root)],
                              capture_output=True, text=True)

    def make_directory_link(self, link, target):
        if os.name == "nt":
            result = subprocess.run(
                ["cmd.exe", "/d", "/c", "mklink", "/J", str(link), str(target)],
                capture_output=True, text=True
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue(link.is_junction())
        else:
            link.symlink_to(target, target_is_directory=True)

    def remove_directory_link(self, link):
        if os.name == "nt" and link.is_junction():
            link.rmdir()
        elif link.is_symlink():
            link.unlink()

    def test_sync_then_check(self):
        self.assertEqual(self.run_script("--write").returncode, 0)
        self.assertEqual(self.run_script("--check").returncode, 0)

    def test_unsynced_source_fails(self):
        self.assertEqual(self.run_script("--write").returncode, 0)
        (self.root / "visual-design-review/references/guide.md").write_text("edited")
        self.assertNotEqual(self.run_script("--check").returncode, 0)

    def test_missing_reference_fails(self):
        self.assertEqual(self.run_script("--write").returncode, 0)
        (self.root / "plugins/visual-design-review/skills/visual-design-review/"
         "references/guide.md").unlink()
        self.assertNotEqual(self.run_script("--check").returncode, 0)

    def test_invalid_marketplace_path_fails(self):
        self.assertEqual(self.run_script("--write").returncode, 0)
        path = self.root / ".agents/plugins/marketplace.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["plugins"][0]["source"]["path"] = "../outside"
        path.write_text(json.dumps(data), encoding="utf-8")
        self.assertNotEqual(self.run_script("--check").returncode, 0)

    def test_linked_canonical_source_dirs_rejected_without_external_changes(self):
        for component in ("root", "references", "nested"):
            with self.subTest(component=component):
                case_tmp = tempfile.TemporaryDirectory()
                root = Path(case_tmp.name)
                link = None
                try:
                    self.create_fixture(root)
                    self.assertEqual(self.run_script("--write", root).returncode, 0)
                    source = root / "visual-design-review"
                    if component == "root":
                        link = source
                        external = root / "outside-source"
                        link.rename(external)
                    else:
                        link = source / "references" / ("nested" if component == "nested" else "")
                        external = root / ("outside-nested" if component == "nested" else "outside-references")
                        if component == "nested":
                            link.mkdir()
                            (link / "extra.md").write_text("external", encoding="utf-8")
                        link.rename(external)
                    external_canary = external / "keep.txt"
                    external_canary.write_text("external canary", encoding="utf-8")
                    self.make_directory_link(link, external)
                    before = external_canary.read_bytes()
                    for mode in ("--check", "--write"):
                        with self.subTest(mode=mode):
                            result = self.run_script(mode, root)
                            self.assertNotEqual(result.returncode, 0)
                            self.assertIn("linked canonical path component", result.stderr)
                            self.assertEqual(before, external_canary.read_bytes())
                finally:
                    if link is not None:
                        self.remove_directory_link(link)
                    case_tmp.cleanup()

    def test_linked_package_ancestor_rejected_without_external_changes(self):
        self.assertEqual(self.run_script("--write").returncode, 0)
        package_parent = self.root / "plugins"
        outside = self.root / "outside-plugins"
        package_parent.rename(outside)
        sentinel = outside / "visual-design-review/skills/visual-design-review/keep.txt"
        sentinel.write_text("external user file", encoding="utf-8")
        before = {p.relative_to(outside): p.read_bytes()
                  for p in outside.rglob("*") if p.is_file()}
        try:
            self.make_directory_link(package_parent, outside)
            for mode in ("--check", "--write"):
                with self.subTest(mode=mode):
                    result = self.run_script(mode)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("linked package path component: plugins", result.stderr)
                    self.assertEqual(before, {p.relative_to(outside): p.read_bytes()
                                             for p in outside.rglob("*") if p.is_file()})
        finally:
            self.remove_directory_link(package_parent)

    def test_linked_package_directory_rejected_before_write(self):
        self.assertEqual(self.run_script("--write").returncode, 0)
        package = self.root / "plugins/visual-design-review/skills/visual-design-review"
        package_references = package / "references"
        external = self.root / "outside-package-references"
        package_references.rename(external)
        canary = external / "keep.txt"
        canary.write_text("external canary", encoding="utf-8")
        try:
            self.make_directory_link(package_references, external)
            result = self.run_script("--write")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("linked package path component", result.stderr)
            self.assertEqual(canary.read_text(encoding="utf-8"), "external canary")
        finally:
            self.remove_directory_link(package_references)

    def test_dangling_package_ancestor_rejected(self):
        parent = self.root / "plugins/visual-design-review/skills"
        missing = self.root / "missing-outside"
        missing.mkdir()
        try:
            self.make_directory_link(parent, missing)
            shutil.rmtree(missing)
            for mode in ("--check", "--write"):
                with self.subTest(mode=mode):
                    result = self.run_script(mode)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("linked package path component", result.stderr)
                    self.assertFalse(missing.exists())
        finally:
            self.remove_directory_link(parent)

    def test_unexpected_package_file_fails(self):
        self.assertEqual(self.run_script("--write").returncode, 0)
        extra = self.root / "plugins/visual-design-review/skills/visual-design-review/extra.md"
        extra.write_text("not in source", encoding="utf-8")
        self.assertNotEqual(self.run_script("--check").returncode, 0)


if __name__ == "__main__":
    unittest.main()
