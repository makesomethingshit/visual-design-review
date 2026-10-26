"""Standalone unittest for the limited mixed-text probe."""
import importlib.util
import json
import unittest
from pathlib import Path

FILE = (Path(__file__).resolve().parents[1] / "visual-design-review"
        / "scripts" / "mixed_text_probe.py")
spec = importlib.util.spec_from_file_location("mixed_text_probe", FILE)
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)

PIL_AVAILABLE = importlib.util.find_spec("PIL") is not None
WINDOWS_KOREAN_FONT = Path(r"C:\Windows\Fonts\malgun.ttf")


class ProbeTests(unittest.TestCase):
    def test_unverified_without_actual_line_geometry(self):
        result = probe.check({"text": "한글 ABC"})
        self.assertEqual(result["checks"][1]["status"], "UNVERIFIED")
        self.assertEqual(result["checks"][2]["status"], "UNVERIFIED")

    def test_rule_sources_are_explicit(self):
        result = probe.check({"text": "한글 ABC"})
        for item in result["checks"]:
            for field in ("source", "source_version", "document_status",
                          "scope", "verification_method"):
                self.assertIn(field, item)

    @unittest.skipUnless(PIL_AVAILABLE and WINDOWS_KOREAN_FONT.is_file(),
                         "Pillow and the Windows Korean font are optional")
    def test_optional_font_render_reproducer_records_engine_and_identity(self):
        import hashlib
        import io
        import PIL
        from PIL import Image, ImageDraw, ImageFont

        font_path = WINDOWS_KOREAN_FONT
        font = ImageFont.truetype(str(font_path), size=32)
        image = Image.new("L", (400, 64), 0)
        ImageDraw.Draw(image).text((4, 4), "한글 ABC", font=font, fill=255)
        encoded = io.BytesIO()
        image.save(encoded, format="PNG", optimize=False)
        self.assertIsNotNone(image.getbbox())
        self.assertEqual(len(hashlib.sha256(font_path.read_bytes()).hexdigest()), 64)
        self.assertEqual(len(hashlib.sha256(encoded.getvalue()).hexdigest()), 64)
        self.assertTrue(font.getname()[0])
        self.assertTrue(str(getattr(font, "layout_engine", "BASIC")))
        self.assertTrue(PIL.__version__)

    def test_source_fixtures_cover_simple_good_and_bad_paths(self):
        root = Path(__file__).resolve().parents[1] / "examples"
        good = probe.check(json.loads((root / "mixed-script-good.json").read_text(encoding="utf-8")))
        bad = probe.check(json.loads((root / "mixed-script-bad.json").read_text(encoding="utf-8")))
        self.assertEqual(good["checks"][1]["status"], "NO_SIMPLE_ANOMALY")
        self.assertEqual(bad["checks"][1]["status"], "FINDING")
        self.assertEqual(bad["checks"][0]["status"], "FINDING")

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

    def test_source_line_endings_preserve_boundary_findings(self):
        for newline in ("\n", "\r\n", "\r"):
            with self.subTest(newline=repr(newline)):
                result = probe.check({
                    "text": "가나" + newline + "다라)",
                    "rendered_lines": ["가나", "다라", ")"],
                    "profile": {"korean_horizontal_break_check": True},
                })
                self.assertEqual(result["checks"][1]["status"], "FINDING")

    def test_no_supported_unit_token_is_not_a_pass(self):
        for text in ("본문만 있음", "폭 35 mm 끝", "모델35mmA"):
            result = probe.check({"text": text, "profile": {"si_spacing": True}})
            self.assertEqual(result["checks"][0]["status"], "NOT_APPLICABLE")

    def test_si_numeric_boundaries_do_not_restart_inside_unsupported_numbers(self):
        cases = (("모델35.5mm", []), ("1,035mm", []),
                 ("exception035mm", ["035mm"]), ("1e+35mm", []),
                 ("1e-35mm", []), ("1.2.35mm", []))
        for text, exceptions in cases:
            with self.subTest(text=text):
                result = probe.check({"text": text, "profile": {
                    "si_spacing": True, "except_exact_tokens": exceptions}})
                self.assertEqual(result["checks"][0]["status"], "NOT_APPLICABLE")
                self.assertEqual(result["checks"][0]["matches"], [])

        result = probe.check({"text": "35.5mm", "profile": {"si_spacing": True}})
        self.assertEqual(result["checks"][0]["status"], "FINDING")
        self.assertEqual(result["checks"][0]["matches"], ["35.5mm"])

        result = probe.check({"text": "35.5mm", "profile": {
            "si_spacing": True, "except_exact_tokens": ["35.5mm"]}})
        self.assertEqual(result["checks"][0]["status"], "PASS")

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
