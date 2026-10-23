#!/usr/bin/env python3
"""Read-only, profile-bound PDF checks backed by Poppler command-line tools."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

CHECKER_NAME = "poppler-read-only-pdf-preflight"
CHECKER_VERSION = "1.0.0"
PROFILE_SCHEMA = "vdr-print-contract-v1"
TOOL_NAMES = ("pdfinfo", "pdffonts", "pdftoppm")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _json_object(raw: bytes, label: str) -> dict[str, Any]:
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"{label} must be UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    return value


def validate_profile(raw: bytes) -> dict[str, Any]:
    profile = _json_object(raw, "Profile")
    required = {
        "schema", "profile_id", "trim_box_points", "bleed_box_points",
        "box_tolerance_points", "require_embedded_fonts",
        "allowed_rendered_color",
    }
    if set(profile) != required:
        missing = sorted(required - set(profile))
        extra = sorted(set(profile) - required)
        raise ValueError(f"Profile fields must match exactly; missing={missing}, extra={extra}")
    if profile["schema"] != PROFILE_SCHEMA:
        raise ValueError(f"Unsupported profile schema: {profile['schema']}")
    if not isinstance(profile["profile_id"], str) or not profile["profile_id"]:
        raise ValueError("profile_id must be a non-empty string")
    for name in ("trim_box_points", "bleed_box_points"):
        value = profile[name]
        if (not isinstance(value, list) or len(value) != 4 or
                not all(isinstance(item, (int, float)) and not isinstance(item, bool) and math.isfinite(item)
                        for item in value) or value[2] <= value[0] or value[3] <= value[1]):
            raise ValueError(f"{name} must be four increasing finite points")
    tolerance = profile["box_tolerance_points"]
    if (not isinstance(tolerance, (int, float)) or isinstance(tolerance, bool) or
            not math.isfinite(tolerance) or tolerance < 0):
        raise ValueError("box_tolerance_points must be a non-negative number")
    if not isinstance(profile["require_embedded_fonts"], bool):
        raise ValueError("require_embedded_fonts must be boolean")
    if profile["allowed_rendered_color"] not in {"grayscale", "any"}:
        raise ValueError("allowed_rendered_color must be grayscale or any")
    return profile


def _resolve_tool(name: str, override: str | None) -> str | None:
    candidate = override or name
    if Path(candidate).is_file():
        return str(Path(candidate).resolve())
    return shutil.which(candidate)


def _same_file(left: Path, right: Path) -> bool:
    if left.resolve() == right.resolve():
        return True
    try:
        return left.exists() and right.exists() and left.samefile(right)
    except OSError:
        return False


def validate_output_target(pdf: Path, profile: Path, output: Path | None) -> None:
    if output is not None and (_same_file(output, pdf) or _same_file(output, profile)):
        raise ValueError("--output must not overwrite the PDF or print profile")


def _run(tool: str, args: list[str], timeout: int = 30) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run([tool, *args], check=False, capture_output=True, timeout=timeout)


def _tool_version(tool: str) -> str:
    try:
        result = _run(tool, ["-v"], timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        return "UNKNOWN"
    text = (result.stdout + result.stderr).decode("utf-8", errors="replace")
    match = re.search(r"version\s+([^\s]+)", text, re.IGNORECASE)
    return match.group(1) if match else "UNKNOWN"


def _tool_record(path: str | None) -> dict[str, Any]:
    if path is None:
        return {"status": "BLOCKED", "path": None, "version": "UNKNOWN",
                "reason": "executable unavailable"}
    return {"status": "PASS", "path": path, "version": _tool_version(path)}


def _blocked(check_id: str, reason: str, tool: str | None = None) -> dict[str, Any]:
    evidence: dict[str, Any] = {"reason": reason}
    if tool:
        evidence["tool"] = tool
    return {"id": check_id, "status": "BLOCKED", "page": None, "evidence": evidence}


def _unverified(check_id: str, reason: str) -> dict[str, Any]:
    return {"id": check_id, "status": "UNVERIFIED", "page": None,
            "evidence": {"reason": reason}}


def _parse_pages(text: str) -> int | None:
    match = re.search(r"^Pages:\s*(\d+)\s*$", text, re.MULTILINE)
    return int(match.group(1)) if match else None


def _parse_boxes(text: str) -> dict[str, list[float]]:
    boxes: dict[str, list[float]] = {}
    for line in text.splitlines():
        name, separator, values = line.partition(":")
        name = re.sub(r"^Page\s+\d+\s+", "", name.strip())
        if not separator or name not in {"TrimBox", "BleedBox"}:
            continue
        numbers = values.split()
        if len(numbers) == 4:
            try:
                boxes[name.strip()] = [float(item) for item in numbers]
            except ValueError:
                pass
    return boxes


def _matches(actual: list[float] | None, expected: list[float], tolerance: float) -> bool:
    return actual is not None and all(abs(a - e) <= tolerance for a, e in zip(actual, expected))


def _check_boxes(pdf: Path, tool: str | None, profile: dict[str, Any], page_count: int | None) -> dict[str, Any]:
    if tool is None:
        return _blocked("trim-bleed", "pdfinfo executable unavailable", "pdfinfo")
    if page_count is None:
        return _blocked("trim-bleed", "PDF page count was not readable", "pdfinfo")
    pages: list[dict[str, Any]] = []
    for page in range(1, page_count + 1):
        try:
            result = _run(tool, ["-f", str(page), "-l", str(page), "-box", str(pdf)])
        except (OSError, subprocess.TimeoutExpired) as exc:
            return _blocked("trim-bleed", f"pdfinfo execution failed: {exc}", "pdfinfo")
        if result.returncode != 0:
            return _blocked("trim-bleed", f"pdfinfo rejected page {page}", "pdfinfo")
        actual = _parse_boxes(result.stdout.decode("utf-8", errors="replace"))
        trim = actual.get("TrimBox")
        bleed = actual.get("BleedBox")
        pages.append({
            "page": page,
            "trim_box": trim,
            "expected_trim_box": profile["trim_box_points"],
            "trim_match": _matches(trim, profile["trim_box_points"], profile["box_tolerance_points"]),
            "bleed_box": bleed,
            "expected_bleed_box": profile["bleed_box_points"],
            "bleed_match": _matches(bleed, profile["bleed_box_points"], profile["box_tolerance_points"]),
            "tolerance_points": profile["box_tolerance_points"],
        })
    status = "PASS" if all(item["trim_match"] and item["bleed_match"] for item in pages) else "FAIL"
    return {"id": "trim-bleed", "status": status, "page": None,
            "evidence": {"source": "pdfinfo -box", "pages": pages}}


def _parse_fonts(text: str) -> tuple[list[dict[str, Any]], str | None]:
    rows: list[dict[str, Any]] = []
    in_table = False
    for line in text.splitlines():
        if line.startswith("name") and "emb" in line.split():
            in_table = True
            continue
        if not in_table or not line.strip() or set(line.strip()) == {"-"}:
            continue
        parts = line.split()
        if (len(parts) < 7 or parts[-5].lower() not in {"yes", "no"} or
                parts[-4].lower() not in {"yes", "no"} or parts[-3].lower() not in {"yes", "no"} or
                not parts[-2].isdigit() or not parts[-1].isdigit()):
            return [], "malformed pdffonts row"
        rows.append({
            "name": parts[0],
            "type": " ".join(parts[1:-5]),
            "embedded": parts[-5].lower() == "yes",
            "subset": parts[-4].lower() == "yes",
            "unicode": parts[-3].lower() == "yes",
            "object": parts[-2],
            "generation": parts[-1],
        })
    if not in_table:
        return [], "pdffonts font table header missing"
    return rows, None


def _check_fonts(pdf: Path, tool: str | None, profile: dict[str, Any], page_count: int | None) -> dict[str, Any]:
    if tool is None:
        return _blocked("font-embedding", "pdffonts executable unavailable", "pdffonts")
    if page_count is None:
        return _blocked("font-embedding", "PDF page count was not readable", "pdffonts")
    pages: list[dict[str, Any]] = []
    all_fonts: list[dict[str, Any]] = []
    for page in range(1, page_count + 1):
        try:
            result = _run(tool, ["-f", str(page), "-l", str(page), str(pdf)])
        except (OSError, subprocess.TimeoutExpired) as exc:
            return _blocked("font-embedding", f"pdffonts execution failed: {exc}", "pdffonts")
        if result.returncode != 0:
            return _blocked("font-embedding", f"pdffonts rejected page {page}", "pdffonts")
        fonts, parse_error = _parse_fonts(result.stdout.decode("utf-8", errors="replace"))
        if parse_error:
            return _blocked("font-embedding", parse_error, "pdffonts")
        for font in fonts:
            all_fonts.append({"page": page, **font})
        pages.append({"page": page, "fonts": fonts})
    if not all_fonts:
        return {"id": "font-embedding", "status": "NOT_APPLICABLE", "page": None,
                "evidence": {"source": "pdffonts", "pages": pages,
                             "reason": "PDF contains no text fonts"}}
    if not profile["require_embedded_fonts"]:
        return {"id": "font-embedding", "status": "NOT_APPLICABLE", "page": None,
                "evidence": {"source": "pdffonts", "pages": pages,
                             "reason": "profile does not require embedding"}}
    status = "PASS" if all(font["embedded"] for font in all_fonts) else "FAIL"
    return {"id": "font-embedding", "status": status, "page": None,
            "evidence": {"source": "pdffonts", "pages": pages}}


def _ppm_token(data: bytes, offset: int) -> tuple[bytes, int]:
    while offset < len(data):
        if data[offset] in b" \t\r\n":
            offset += 1
        elif data[offset] == ord("#"):
            newline = data.find(b"\n", offset)
            offset = len(data) if newline < 0 else newline + 1
        else:
            break
    start = offset
    while offset < len(data) and data[offset] not in b" \t\r\n":
        offset += 1
    return data[start:offset], offset


def _parse_ppm(data: bytes) -> tuple[int, int, bytes]:
    offset = 0
    tokens: list[bytes] = []
    for _ in range(4):
        token, offset = _ppm_token(data, offset)
        tokens.append(token)
    if tokens[0] != b"P6" or tokens[1] == b"" or tokens[2] == b"" or tokens[3] != b"255":
        raise ValueError("pdftoppm did not return an 8-bit P6 image")
    if offset >= len(data) or data[offset] not in b" \t\r\n":
        raise ValueError("PPM maxval delimiter missing")
    offset += 2 if data[offset:offset + 2] == b"\r\n" else 1
    width, height = int(tokens[1]), int(tokens[2])
    size = width * height * 3
    pixels = data[offset:offset + size]
    if len(pixels) != size:
        raise ValueError("truncated PPM output")
    return width, height, pixels


def _check_color(pdf: Path, tool: str | None, profile: dict[str, Any], page_count: int | None) -> dict[str, Any]:
    if profile["allowed_rendered_color"] == "any":
        return {"id": "allowed-rendered-color", "status": "NOT_APPLICABLE", "page": None,
                "evidence": {"reason": "profile places no rendered-colour restriction"}}
    if tool is None:
        return _blocked("allowed-rendered-color", "pdftoppm executable unavailable", "pdftoppm")
    if page_count is None:
        return _blocked("allowed-rendered-color", "PDF page count was not readable", "pdftoppm")
    pages: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="vdr-pdf-render-") as temp_dir:
        for page in range(1, page_count + 1):
            output_prefix = Path(temp_dir) / f"page-{page}"
            try:
                result = _run(tool, ["-f", str(page), "-l", str(page), "-singlefile",
                                     "-r", "72", str(pdf), str(output_prefix)], timeout=60)
            except (OSError, subprocess.TimeoutExpired) as exc:
                return _blocked("allowed-rendered-color", f"pdftoppm execution failed: {exc}", "pdftoppm")
            if result.returncode != 0:
                return _blocked("allowed-rendered-color", f"pdftoppm rejected page {page}", "pdftoppm")
            output = output_prefix.with_suffix(".ppm")
            if not output.is_file():
                return _blocked("allowed-rendered-color", "pdftoppm produced no PPM output", "pdftoppm")
            try:
                ppm = output.read_bytes()
                width, height, pixels = _parse_ppm(ppm)
            except (OSError, ValueError, OverflowError) as exc:
                return _blocked("allowed-rendered-color", str(exc), "pdftoppm")
            first_non_gray = None
            for index in range(0, len(pixels), 3):
                rgb = pixels[index:index + 3]
                if rgb[0] != rgb[1] or rgb[1] != rgb[2]:
                    first_non_gray = {"x": (index // 3) % width, "y": (index // 3) // width,
                                      "rgb": list(rgb)}
                    break
            pages.append({
                "page": page,
                "width": width,
                "height": height,
                "render_sha256": digest(ppm),
                "pixel_count": width * height,
                "first_non_grayscale_pixel": first_non_gray,
            })
    status = "PASS" if all(item["first_non_grayscale_pixel"] is None for item in pages) else "FAIL"
    return {"id": "allowed-rendered-color", "status": status, "page": None,
            "evidence": {"source": "pdftoppm -ppm at 72 dpi", "mode": "grayscale", "pages": pages}}


def _rollup(checks: list[dict[str, Any]]) -> str:
    statuses = {item["status"] for item in checks}
    if "FAIL" in statuses:
        return "FAIL"
    if "BLOCKED" in statuses:
        return "BLOCKED"
    return "PASS"


def preflight(pdf_path: Path, profile_path: Path, tool_paths: dict[str, str | None] | None = None) -> dict[str, Any]:
    pdf = Path(pdf_path)
    profile_file = Path(profile_path)
    pdf_bytes = pdf.read_bytes()
    source_pdf_sha256 = digest(pdf_bytes)
    profile_bytes = profile_file.read_bytes()
    if not pdf_bytes.startswith(b"%PDF-"):
        raise ValueError("Input does not begin with a PDF header")
    profile = validate_profile(profile_bytes)
    overrides = tool_paths or {}
    resolved = {name: _resolve_tool(name, overrides.get(name)) for name in TOOL_NAMES}
    with tempfile.TemporaryDirectory(prefix="vdr-pdf-input-") as temp_dir:
        inspection_pdf = Path(temp_dir) / "input.pdf"
        inspection_pdf.write_bytes(pdf_bytes)
        inspected_pdf_sha256 = digest(inspection_pdf.read_bytes())
        if inspected_pdf_sha256 != source_pdf_sha256:
            raise RuntimeError("PDF snapshot hash changed before inspection")
        report: dict[str, Any] = {
            "schema": "pdf-preflight-v1",
            "checker": {"name": CHECKER_NAME, "version": CHECKER_VERSION},
            "pdf_sha256": source_pdf_sha256,
            "inspected_pdf_sha256": inspected_pdf_sha256,
            "profile": {"schema": profile["schema"], "profile_id": profile["profile_id"],
                        "sha256": digest(profile_bytes)},
            "tools": {name: _tool_record(resolved[name]) for name in TOOL_NAMES},
            "read_only": True,
            "inspection": {"private_snapshot": True},
            "physical_print_status": "UNVERIFIED",
        }
        page_count: int | None = None
        input_blocked: str | None = None
        if resolved["pdfinfo"] is None:
            input_blocked = "pdfinfo executable unavailable"
        else:
            try:
                info = _run(resolved["pdfinfo"], ["-box", str(inspection_pdf)])
            except (OSError, subprocess.TimeoutExpired) as exc:
                input_blocked = f"pdfinfo execution failed: {exc}"
            else:
                if info.returncode != 0:
                    input_blocked = "pdfinfo rejected the PDF bytes"
                else:
                    page_count = _parse_pages(info.stdout.decode("utf-8", errors="replace"))
                    if page_count is None or page_count < 1:
                        input_blocked = "pdfinfo did not provide a positive page count"
        report["input"] = {"status": "BLOCKED" if input_blocked else "PASS",
                           "page_count": page_count, "reason": input_blocked}
        if input_blocked:
            checks = [
                _blocked("trim-bleed", input_blocked, "pdfinfo"),
                _blocked("font-embedding", input_blocked, "pdffonts"),
                _blocked("allowed-rendered-color", input_blocked, "pdftoppm"),
            ]
        else:
            checks = [
                _check_boxes(inspection_pdf, resolved["pdfinfo"], profile, page_count),
                _check_fonts(inspection_pdf, resolved["pdffonts"], profile, page_count),
                _check_color(inspection_pdf, resolved["pdftoppm"], profile, page_count),
            ]
        checks.extend([
            _unverified("pdf-x", "PDF/X conformance is outside this checker"),
            _unverified("physical-print", "paper, ink, press, and viewing conditions are outside this checker"),
        ])
        report["checks"] = checks
        report["preflight_status"] = _rollup(checks[:3])
        report["verification_status"] = "UNVERIFIED"
        report["evidence_level"] = "ACTUAL_PDF_BYTES_PARTIAL_PRECHECK"
        report["warning"] = "PASS covers only the implemented profile checks; PDF/X and physical print remain UNVERIFIED"
        return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", required=True, type=Path)
    parser.add_argument("--profile", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--pdfinfo")
    parser.add_argument("--pdffonts")
    parser.add_argument("--pdftoppm")
    args = parser.parse_args(argv)
    try:
        validate_output_target(args.pdf, args.profile, args.output)
        report = preflight(args.pdf, args.profile, {
            "pdfinfo": args.pdfinfo, "pdffonts": args.pdffonts, "pdftoppm": args.pdftoppm,
        })
    except (OSError, ValueError) as exc:
        print(json.dumps({"status": "BLOCKED", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    text = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8", newline="\n")
    print(text)
    return {"PASS": 0, "FAIL": 1, "BLOCKED": 2}[report["preflight_status"]]


if __name__ == "__main__":
    raise SystemExit(main())
