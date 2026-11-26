#!/usr/bin/env python3
"""Read-only evidence importer; DOES NOT perform PDF preflight."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ALLOWED = {"PASS", "FAIL", "BLOCKED", "UNVERIFIED", "NOT_APPLICABLE"}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalize(pdf: bytes, report: bytes) -> dict:
    if not pdf.startswith(b"%PDF-"):
        raise ValueError("Input does not begin with a PDF header")
    source = json.loads(report.decode("utf-8"))
    if not isinstance(source, dict) or not isinstance(source.get("checks"), list):
        raise ValueError("Report must have a checks array")
    checks = []
    for item in source["checks"]:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            raise ValueError("Each check must have an id")
        status = item.get("status", "UNVERIFIED")
        if status not in ALLOWED:
            raise ValueError(f"Unsupported report status: {status}")
        checks.append({"id": item["id"], "external_report_status": status,
                       "page": item.get("page"), "evidence": item.get("evidence"),
                       "status": "UNVERIFIED"})
    return {
        "schema": "pdf-preflight-import-v0",
        "source_pdf_sha256": digest(pdf),
        "external_report_sha256": digest(report),
        "tool_name": source.get("tool_name", "UNKNOWN"),
        "tool_version": source.get("tool_version", "UNKNOWN"),
        "profile_id": source.get("profile_id", "UNKNOWN"),
        "evidence_level": "EXTERNAL_REPORT_IMPORTED_UNVERIFIED",
        "verification_status": "UNVERIFIED",
        "checks": checks,
        "warning": "External report is not authenticated; imported PASS is not independently verified",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        result = normalize(args.pdf.read_bytes(), args.report.read_bytes())
    except (OSError, ValueError) as exc:
        print(json.dumps({"status": "BLOCKED", "error": str(exc)}, ensure_ascii=False),
              file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
