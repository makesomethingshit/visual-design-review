"""Standalone unittest for the limited mixed-text probe."""
import importlib.util
import unittest
from pathlib import Path

FILE = (Path(__file__).resolve().parents[1] / "visual-design-review"
        / "scripts" / "mixed_text_probe.py")
spec = importlib.util.spec_from_file_location("mixed_text_probe", FILE)
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


class ProbeTests(unittest.TestCase):
    def test_unverified_without_actual_line_geometry(self):
        result = probe.check({"text": "한글 ABC"})
        self.assertEqual(result["checks"][1]["status"], "UNVERIFIED")
        self.assertEqual(result["checks"][2]["status"], "UNVERIFIED")

    def test_si_is_opt_in_and_never_rewrites(self):
        payload = {"text": "폭은 35mm입니다", "profile": {"si_spacing": True}}
        self.assertEqual(probe.check(payload)["checks"][0]["status"], "NOT_APPLICABLE")
        payload = {"text": "폭 35mm 끝", "profile": {"si_spacing": True}}
        self.assertEqual(probe.check(payload)["checks"][0]["status"], "FINDING")
        payload["profile"]["except_exact_tokens"] = ["35mm"]
        self.assertEqual(probe.check(payload)["checks"][0]["status"], "PASS")

    def test_korean_line_break_candidates_only(self):
        result = probe.check({"text": "가나다)","rendered_lines": ["가나다", ")"],
                              "profile": {"korean_horizontal_break_check": True}})
        self.assertEqual(result["checks"][1]["status"], "FINDING")
        self.assertEqual(result["checks"][1]["severity"], "UNDETERMINED")

    def test_mismatched_lines_blocked(self):
        result = probe.check({"text": "가나다", "rendered_lines": ["가나"]})
        self.assertEqual(result["checks"][1]["status"], "BLOCKED")


if __name__ == "__main__":
    unittest.main()
