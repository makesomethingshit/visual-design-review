#!/usr/bin/env python3
"""Read-only evidence importer; DOES NOT perform PDF preflight."""
from __future__ import annotations

import argparse
import hashlib
import json
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


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--pdf", required=True, type=Path)
    p.add_argument("--report", required=True, type=Path)
    a = p.parse_args()
    print(json.dumps(normalize(a.pdf.read_bytes(), a.report.read_bytes()),
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
