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

    def test_no_supported_unit_token_is_not_a_pass(self):
        for text in ("본문만 있음", "폭 35 mm 끝", "모델35mmA"):
            result = probe.check({"text": text, "profile": {"si_spacing": True}})
            self.assertEqual(result["checks"][0]["status"], "NOT_APPLICABLE")

    def test_non_boolean_opt_in_rejected(self):
        for flag in ("false", "true", 1, None):
            with self.assertRaises(ValueError):
                probe.check({"text": "폭 35mm 끝", "profile": {"si_spacing": flag}})

    def test_except_exact_tokens_rejects_non_list_or_non_string_items(self):
        for invalid in ("35mm", None, 35, {"value": "35mm"},
                        ["35mm", None], ["35mm", 35], [True], [None]):
            with self.subTest(invalid=invalid):
                for si in (False, True):
                    with self.assertRaisesRegex(ValueError, "except_exact_tokens"):
                        probe.check({"text": "폭 35mm 끝", "profile": {
                            "si_spacing": si, "except_exact_tokens": invalid}})

    def test_except_exact_tokens_accepts_only_string_lists(self):
        for valid in ([], ["35mm"], ["35mm", "20cm"]):
            payload = {"text": "폭 35mm 끝", "profile": {
                "si_spacing": True, "except_exact_tokens": valid}}
            expected = "FINDING" if not valid else "PASS"
            self.assertEqual(probe.check(payload)["checks"][0]["status"], expected)

    def test_si_disabled_does_not_report_a_finding(self):
        result = probe.check({"text": "폭 35mm 끝", "profile": {"si_spacing": False}})
        self.assertEqual(result["checks"][0]["status"], "NOT_APPLICABLE")

    def test_payload_is_not_rewritten(self):
        import copy
        payload = {"text": "폭 35mm 끝", "profile": {"si_spacing": True,
                   "except_exact_tokens": ["35mm"]}}
        original = copy.deepcopy(payload)
        self.assertEqual(probe.check(payload)["checks"][0]["status"], "PASS")
        self.assertEqual(payload, original)


if __name__ == "__main__":
    unittest.main()
