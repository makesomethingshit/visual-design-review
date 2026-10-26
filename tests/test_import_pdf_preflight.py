import importlib.util
import json
import unittest
from pathlib import Path

FILE = (Path(__file__).resolve().parents[1] / "visual-design-review" /
        "scripts" / "import_pdf_preflight.py")
spec = importlib.util.spec_from_file_location("import_pdf_preflight", FILE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class ImporterTests(unittest.TestCase):
    def test_import_not_auto_verified(self):
        raw = json.dumps({"tool_name": "example", "checks": [
            {"id": "font-embed", "status": "PASS"}]}).encode()
        r = mod.normalize(b"%PDF-1.7\nfoo", raw)
        self.assertEqual(r["checks"][0]["external_report_status"], "PASS")
        self.assertEqual(r["checks"][0]["status"], "UNVERIFIED")
        self.assertEqual(r["verification_status"], "UNVERIFIED")

    def test_invalid_pdf_rejected(self):
        with self.assertRaises(ValueError):
            mod.normalize(b"not a PDF", b'{"checks": []}')

    def test_unknown_status_rejected(self):
        with self.assertRaises(ValueError):
            mod.normalize(b"%PDF-1.4", b'{"checks": [{"id":"x","status":"MAGIC_SUCCESS"}]}')


if __name__ == "__main__":
    unittest.main()
