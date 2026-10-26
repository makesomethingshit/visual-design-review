"""Isolated positive/negative cases for the source-of-truth plugin mirror."""
import json
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
        src = self.root / "visual-design-review"
        (src / "references").mkdir(parents=True)
        (src / "SKILL.md").write_text(
            "---\nname: visual-design-review\ndescription: Design review.\n---\n"
            "\n[ref](references/guide.md)\n", encoding="utf-8"
        )
        (src / "references" / "guide.md").write_text("canonical", encoding="utf-8")
        for rel in [".agents/plugins/marketplace.json",
                    "plugins/visual-design-review/.codex-plugin/plugin.json"]:
            path = self.root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / rel, path)

    def run_script(self, flag):
        return subprocess.run([sys.executable, str(SCRIPT), flag,
                               "--root", str(self.root)],
                              capture_output=True, text=True)

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
            package_parent.symlink_to(outside, target_is_directory=True)
        except OSError as exc:
            self.skipTest("directory symlinks unavailable: " + str(exc))
        for mode in ("--check", "--write"):
            with self.subTest(mode=mode):
                result = self.run_script(mode)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("linked package path component: plugins", result.stderr)
                self.assertEqual(before, {p.relative_to(outside): p.read_bytes()
                                         for p in outside.rglob("*") if p.is_file()})

    def test_dangling_package_ancestor_rejected(self):
        parent = self.root / "plugins/visual-design-review/skills"
        try:
            parent.symlink_to(self.root / "missing-outside", target_is_directory=True)
        except OSError as exc:
            self.skipTest("directory symlinks unavailable: " + str(exc))
        for mode in ("--check", "--write"):
            with self.subTest(mode=mode):
                result = self.run_script(mode)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("linked package path component", result.stderr)
                self.assertFalse((self.root / "missing-outside").exists())

    def test_unexpected_package_file_fails(self):
        self.assertEqual(self.run_script("--write").returncode, 0)
        extra = self.root / "plugins/visual-design-review/skills/visual-design-review/extra.md"
        extra.write_text("not in source", encoding="utf-8")
        self.assertNotEqual(self.run_script("--check").returncode, 0)


if __name__ == "__main__":
    unittest.main()
