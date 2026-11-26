"""Shared CLI contract for the read-only review scripts.

Every script must report unreadable or malformed input as a BLOCKED JSON
object on stderr with exit code 2, and never as a Python traceback. This is a
static interface check, not a verification of the scripts' design judgements.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "visual-design-review" / "scripts"


def run(script: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(SCRIPTS / script), *args],
                          capture_output=True, text=True, encoding="utf-8")


class ScriptCliContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self._directory = tempfile.TemporaryDirectory()
        self.root = Path(self._directory.name)
        self.missing = str(self.root / "missing.json")
        self.not_json = self.root / "not-json.json"
        self.not_json.write_text("{not json", encoding="utf-8")
        self.wrong_shape = self.root / "wrong-shape.json"
        self.wrong_shape.write_text("[]", encoding="utf-8")
        self.pdf = self.root / "input.pdf"
        self.pdf.write_bytes(b"%PDF-1.7\n%%EOF\n")

    def tearDown(self) -> None:
        self._directory.cleanup()

    def assertBlocked(self, result: subprocess.CompletedProcess[str]) -> None:
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(result.stdout, "")
        report = json.loads(result.stderr.strip().splitlines()[-1])
        self.assertEqual(report["status"], "BLOCKED")
        self.assertTrue(report["error"])

    def cases(self) -> dict[str, list[list[str]]]:
        bad = [self.missing, str(self.not_json), str(self.wrong_shape)]
        return {
            "finding_history.py": [[path, path] for path in bad],
            "mixed_text_probe.py": [[path] for path in bad],
            "repair_lift_summary.py": [[path] for path in bad],
            "import_pdf_preflight.py": [["--pdf", str(self.pdf), "--report", path]
                                        for path in bad]
                                       + [["--pdf", self.missing,
                                           "--report", str(self.wrong_shape)]],
            "font_pairing_render.py": [["--fixture", path, "--validate-only"]
                                       for path in bad],
        }

    def test_malformed_input_is_blocked_without_traceback(self) -> None:
        for script, argument_sets in self.cases().items():
            for arguments in argument_sets:
                with self.subTest(script=script, arguments=arguments):
                    self.assertBlocked(run(script, *arguments))

    def test_every_script_exposes_main_with_argv(self) -> None:
        for path in sorted(SCRIPTS.glob("*.py")):
            with self.subTest(script=path.name):
                text = path.read_text(encoding="utf-8")
                self.assertIn("def main(argv: list[str] | None = None) -> int:", text)
                self.assertIn("raise SystemExit(main())", text)
                self.assertIn('"status": "BLOCKED"', text)

    def test_help_uses_module_docstring(self) -> None:
        for path in sorted(SCRIPTS.glob("*.py")):
            with self.subTest(script=path.name):
                result = run(path.name, "--help")
                self.assertEqual(result.returncode, 0, result.stderr)
                first_line = path.read_text(encoding="utf-8").split('"""')[1].strip()
                summary = " ".join(first_line.split(";")[0].split(".")[0].split())
                self.assertIn(summary, " ".join(result.stdout.split()))


if __name__ == "__main__":
    unittest.main()
