import contextlib
import io
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
FILE = ROOT / "visual-design-review" / "scripts" / "check_pdf_preflight.py"
spec = importlib.util.spec_from_file_location("check_pdf_preflight", FILE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

PROFILE = {
    "schema": "vdr-print-contract-v1",
    "profile_id": "test-a4-3mm-grayscale-v1",
    "trim_box_points": [0, 0, 595.28, 841.89],
    "bleed_box_points": [-8.5, -8.5, 603.78, 850.39],
    "box_tolerance_points": 0.02,
    "require_embedded_fonts": True,
    "allowed_rendered_color": "grayscale",
}


def _pdf(objects):
    output = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for number, body in enumerate(objects, start=1):
        offsets.append(len(output))
        output.extend(f"{number} 0 obj\n".encode())
        output.extend(body)
        output.extend(b"\nendobj\n")
    startxref = len(output)
    output.extend(f"xref\n0 {len(objects) + 1}\n".encode())
    output.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.extend(f"{offset:010d} 00000 n \n".encode())
    output.extend((f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
                   f"startxref\n{startxref}\n%%EOF\n").encode())
    return bytes(output)


def write_fixture(path, *, bleed=True, color=False, text=False):
    content = (b"q\n1 0 0 rg\n" if color else b"q\n0 g\n")
    content += b"0 0 595.28 841.89 re f\n"
    if text:
        content += b"BT /F1 18 Tf 40 40 Td (intentional defect) Tj ET\n"
    content += b"Q\n"
    contents = b"<< /Length " + str(len(content)).encode() + b" >>\nstream\n" + content + b"endstream"
    page_boxes = b"/MediaBox [-8.5 -8.5 603.78 850.39] /TrimBox [0 0 595.28 841.89]"
    if bleed:
        page_boxes += b" /BleedBox [-8.5 -8.5 603.78 850.39]"
    else:
        page_boxes += b" /BleedBox [0 0 595.28 841.89]"
    resources = b"/Resources << >>"
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R " + page_boxes + b" " + resources + b" /Contents 4 0 R >>",
        contents,
    ]
    if text:
        objects[2] = objects[2].replace(b"/Resources << >>", b"/Resources << /Font << /F1 5 0 R >> >>")
        objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>")
    path.write_bytes(_pdf(objects))


class PdfPreflightTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.profile = root / "profile.json"
        self.good = root / "normal.pdf"
        self.bad = root / "intentional-defect.pdf"
        self.forged = root / "forged.pdf"
        self.report = root / "report.json"
        self.profile.write_text(json.dumps(PROFILE, indent=2) + "\n", encoding="utf-8")
        write_fixture(self.good)
        write_fixture(self.bad, bleed=False, color=True, text=True)
        self.forged.write_bytes(b"%PDF-1.7\nnot a real PDF")

    def tearDown(self):
        self.temp.cleanup()

    @unittest.skipUnless(
        mod._resolve_tool("pdfinfo", None) and mod._resolve_tool("pdftoppm", None),
        "Poppler pdfinfo and pdftoppm are optional for actual fixture execution",
    )
    def test_normal_fixture_binds_hashes_and_page_evidence(self):
        result = mod.preflight(self.good, self.profile)
        self.assertEqual(result["pdf_sha256"], mod.digest(self.good.read_bytes()))
        self.assertEqual(result["profile"]["sha256"], mod.digest(self.profile.read_bytes()))
        self.assertEqual(result["checker"]["version"], mod.CHECKER_VERSION)
        self.assertEqual(result["input"]["page_count"], 1)
        checks = {item["id"]: item for item in result["checks"]}
        self.assertEqual(checks["trim-bleed"]["status"], "PASS")
        self.assertEqual(checks["allowed-rendered-color"]["status"], "PASS")
        self.assertIn(checks["font-embedding"]["status"], {"NOT_APPLICABLE", "BLOCKED"})
        self.assertEqual(checks["trim-bleed"]["evidence"]["pages"][0]["page"], 1)
        self.assertEqual(checks["allowed-rendered-color"]["evidence"]["pages"][0]["page"], 1)
        self.assertEqual(checks["pdf-x"]["status"], "UNVERIFIED")
        self.assertEqual(checks["physical-print"]["status"], "UNVERIFIED")
        self.assertEqual(result["verification_status"], "UNVERIFIED")

    @unittest.skipUnless(
        mod._resolve_tool("pdfinfo", None) and mod._resolve_tool("pdftoppm", None),
        "Poppler pdfinfo and pdftoppm are optional for actual fixture execution",
    )
    def test_intentional_defect_fixture_fails_actual_checks(self):
        result = mod.preflight(self.bad, self.profile)
        checks = {item["id"]: item for item in result["checks"]}
        self.assertEqual(result["preflight_status"], "FAIL")
        self.assertEqual(checks["trim-bleed"]["status"], "FAIL")
        self.assertEqual(checks["allowed-rendered-color"]["status"], "FAIL")
        self.assertEqual(checks["trim-bleed"]["evidence"]["pages"][0]["bleed_box"], [0.0, 0.0, 595.28, 841.89])
        self.assertIsNotNone(checks["allowed-rendered-color"]["evidence"]["pages"][0]["first_non_grayscale_pixel"])
        self.assertIn(checks["font-embedding"]["status"], {"FAIL", "BLOCKED"})

    def test_unavailable_optional_tool_is_explicitly_blocked(self):
        missing = str(Path(self.temp.name) / "missing-poppler-tool")
        self.assertEqual(mod._tool_record(None)["status"], "BLOCKED")
        self.assertEqual(mod._check_fonts(self.good, missing, PROFILE, 1)["status"], "BLOCKED")
        result = mod.preflight(self.good, self.profile, {"pdfinfo": missing})
        self.assertEqual(result["input"]["status"], "BLOCKED")
        self.assertEqual(result["tools"]["pdfinfo"]["status"], "BLOCKED")
        checks = {item["id"]: item for item in result["checks"]}
        self.assertEqual(checks["font-embedding"]["status"], "BLOCKED")
        self.assertEqual(result["preflight_status"], "BLOCKED")

    def test_cli_font_opt_out_does_not_require_pdffonts(self):
        pdfinfo = (b"Pages: 1\nTrimBox: 0.00 0.00 595.28 841.89\n"
                   b"BleedBox: -8.50 -8.50 603.78 850.39\n")

        def run_pdfinfo(tool, args, timeout=30):
            self.assertEqual(tool, "pdfinfo")
            return subprocess.CompletedProcess([], 0, pdfinfo, b"")

        for required, expected_status, expected_exit in (
            (False, "NOT_APPLICABLE", 0), (True, "BLOCKED", 2),
        ):
            with self.subTest(require_embedded_fonts=required):
                profile = {**PROFILE, "require_embedded_fonts": required,
                           "allowed_rendered_color": "any"}
                self.profile.write_text(json.dumps(profile), encoding="utf-8")
                with patch.object(mod, "_resolve_tool", side_effect=lambda name, override:
                                  "pdfinfo" if name == "pdfinfo" else None), \
                     patch.object(mod, "_run", side_effect=run_pdfinfo), \
                     contextlib.redirect_stdout(io.StringIO()):
                    code = mod.main(["--pdf", str(self.good), "--profile", str(self.profile),
                                     "--output", str(self.report)])
                report = json.loads(self.report.read_text(encoding="utf-8"))
                checks = {item["id"]: item for item in report["checks"]}
                self.assertEqual(code, expected_exit)
                self.assertEqual(checks["font-embedding"]["status"], expected_status)
                self.assertEqual(checks["trim-bleed"]["status"], "PASS")
                self.assertEqual(report["preflight_status"], "PASS" if not required else "BLOCKED")

    def test_cli_accepts_spaced_pdffonts_separator(self):
        table = (b"name                                 type              encoding         emb sub uni object ID\n"
                 b"------------------------------------ ----------------- ---------------- --- --- --- ---------\n")
        pdfinfo = (b"Pages: 1\nTrimBox: 0.00 0.00 595.28 841.89\n"
                   b"BleedBox: -8.50 -8.50 603.78 850.39\n")
        self.profile.write_text(json.dumps({**PROFILE, "allowed_rendered_color": "any"}),
                                encoding="utf-8")
        for row, expected_status, expected_exit in (
            (b"EmbeddedFont                         TrueType          WinAnsi          yes yes yes      5  0\n", "PASS", 0),
            (b"Helvetica                            Type 1            WinAnsi          no  no  no       5  0\n", "FAIL", 1),
            (b"", "NOT_APPLICABLE", 0),
            (b"malformed row\n", "BLOCKED", 2),
        ):
            with self.subTest(font_status=expected_status):
                def run_tool(tool, args, timeout=30):
                    output = b"version 1.0\n" if args == ["-v"] else (
                        pdfinfo if tool == "pdfinfo" else table + row)
                    return subprocess.CompletedProcess([], 0, output, b"")

                with patch.object(mod, "_resolve_tool", side_effect=lambda name, override:
                                  name if name in {"pdfinfo", "pdffonts"} else None), \
                     patch.object(mod, "_run", side_effect=run_tool), \
                     contextlib.redirect_stdout(io.StringIO()):
                    code = mod.main(["--pdf", str(self.good), "--profile", str(self.profile),
                                     "--output", str(self.report)])
                report = json.loads(self.report.read_text(encoding="utf-8"))
                checks = {item["id"]: item for item in report["checks"]}
                self.assertEqual(checks["font-embedding"]["status"], expected_status)
                self.assertEqual(code, expected_exit)
                self.assertEqual(report["preflight_status"],
                                 "PASS" if expected_status == "NOT_APPLICABLE" else expected_status)

    def test_tools_inspect_private_snapshot_matching_report_hash(self):
        original_run = mod._run
        original_resolve = mod._resolve_tool
        inspected_paths = []

        def fake_resolve(name, override):
            return name

        def fake_run(tool, args, timeout=30):
            if args == ["-v"]:
                return subprocess.CompletedProcess([], 0, f"{tool} version 1.0\n".encode(), b"")
            pdf_args = [Path(arg) for arg in args if str(arg).lower().endswith(".pdf")]
            inspected_paths.extend(path.resolve() for path in pdf_args)
            if tool == "pdfinfo":
                if "-f" in args:
                    output = (b"Page    1 TrimBox: 0.00 0.00 595.28 841.89\n"
                              b"Page    1 BleedBox: -8.50 -8.50 603.78 850.39\n")
                else:
                    output = b"Pages:           1\n"
                return subprocess.CompletedProcess([], 0, output, b"")
            if tool == "pdffonts":
                output = b"name type emb sub uni object ID\n-----------------------------\n"
                return subprocess.CompletedProcess([], 0, output, b"")
            if tool == "pdftoppm":
                Path(args[-1]).with_suffix(".ppm").write_bytes(b"P6\n1 1\n255\n" + bytes([10, 10, 10]))
                return subprocess.CompletedProcess([], 0, b"", b"")
            raise AssertionError(tool)

        mod._resolve_tool = fake_resolve
        mod._run = fake_run
        try:
            result = mod.preflight(self.good, self.profile)
        finally:
            mod._run = original_run
            mod._resolve_tool = original_resolve
        self.assertTrue(inspected_paths)
        self.assertTrue(all(path != self.good.resolve() for path in inspected_paths))
        self.assertEqual(result["pdf_sha256"], result["inspected_pdf_sha256"])
        self.assertEqual(result["inspected_pdf_sha256"], mod.digest(self.good.read_bytes()))
        self.assertTrue(result["inspection"]["private_snapshot"])

    def test_cli_output_rejects_pdf_profile_and_hardlink_targets(self):
        before_pdf = self.good.read_bytes()
        before_profile = self.profile.read_bytes()
        for output, before in ((self.good, before_pdf), (self.profile, before_profile)):
            completed = subprocess.run([
                sys.executable, str(FILE), "--pdf", str(self.good), "--profile", str(self.profile),
                "--output", str(output),
            ], check=False, capture_output=True, text=True)
            self.assertEqual(completed.returncode, 2)
            self.assertEqual(output.read_bytes(), before)
        hardlink = Path(self.temp.name) / "hardlink.pdf"
        os.link(self.good, hardlink)
        completed = subprocess.run([
            sys.executable, str(FILE), "--pdf", str(self.good), "--profile", str(self.profile),
            "--output", str(hardlink),
        ], check=False, capture_output=True, text=True)
        self.assertEqual(completed.returncode, 2)
        self.assertEqual(self.good.read_bytes(), before_pdf)

    def test_forged_pdf_header_is_blocked_by_engine(self):
        result = mod.preflight(self.forged, self.profile)
        self.assertEqual(result["input"]["status"], "BLOCKED")
        self.assertEqual(result["preflight_status"], "BLOCKED")
        self.assertTrue(all(item["status"] == "BLOCKED" for item in result["checks"][:3]))

    def test_missing_profile_and_strict_profile_forgery_are_rejected(self):
        with self.assertRaises(FileNotFoundError):
            mod.preflight(self.good, Path(self.temp.name) / "missing-profile.json")
        forged = dict(PROFILE)
        forged["unexpected"] = "PASS"
        forged_path = Path(self.temp.name) / "forged-profile.json"
        forged_path.write_text(json.dumps(forged), encoding="utf-8")
        with self.assertRaises(ValueError):
            mod.preflight(self.good, forged_path)

    def test_ppm_parser_preserves_first_pixel_after_one_delimiter(self):
        pixels = bytes([10, 10, 10, 255, 0, 0])
        width, height, parsed = mod._parse_ppm(b"P6\n2 1\n255\n" + pixels)
        self.assertEqual((width, height), (2, 1))
        self.assertEqual(parsed, pixels)

    def test_malformed_font_table_blocks_instead_of_becoming_empty(self):
        fonts, error = mod._parse_fonts("name type emb sub uni object ID\n" +
                                        "----------------------------------\nmalformed row\n")
        self.assertEqual(fonts, [])
        self.assertEqual(error, "malformed pdffonts row")

    def test_boolean_profile_numbers_are_rejected(self):
        forged = dict(PROFILE)
        forged["box_tolerance_points"] = True
        with self.assertRaises(ValueError):
            mod.validate_profile(json.dumps(forged).encode())

    @unittest.skipUnless(
        mod._resolve_tool("pdfinfo", None) and mod._resolve_tool("pdftoppm", None),
        "Poppler pdfinfo and pdftoppm are optional for actual fixture execution",
    )
    def test_cli_writes_actual_report_and_returns_failure(self):
        completed = subprocess.run([
            sys.executable, str(FILE), "--pdf", str(self.bad), "--profile", str(self.profile),
            "--output", str(self.report),
        ], check=False, capture_output=True, text=True)
        self.assertEqual(completed.returncode, 1)
        report = json.loads(self.report.read_text(encoding="utf-8"))
        self.assertEqual(report["pdf_sha256"], mod.digest(self.bad.read_bytes()))
        self.assertEqual(report["profile"]["sha256"], mod.digest(self.profile.read_bytes()))
        self.assertEqual(report["preflight_status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
