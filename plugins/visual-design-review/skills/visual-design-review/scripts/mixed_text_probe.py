#!/usr/bin/env python3
"""Limited, read-only mixed-script typography probe. No font/render claims."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

CLOSING = frozenset(")]}〉》」』】、。，．！？!?,.;:)]")
OPENING = frozenset("([{〈《「『【")

RULE_METADATA = {
    "MIX-001": {
        "knowledge_kind": "NORMATIVE",
        "rule_strength": "CONDITIONAL",
        "source": "Unicode UAX #14; W3C KLReq",
        "source_url": [
            "https://www.unicode.org/reports/tr14/",
            "https://www.w3.org/TR/2026/DNOTE-klreq-20260321/",
        ],
        "source_version": "KLReq 2026-03-21; UAX #14 version not pinned by this PoC",
        "document_status": "Unicode Standard Annex + Group Note Draft",
        "scope": "Caller-supplied line strings for Korean horizontal text",
        "verification_method": "source_line_boundary_candidate_check",
        "evidence_status": "UNVERIFIED: lines are not shaping evidence",
    },
    "MIX-003": {
        "knowledge_kind": "NORMATIVE",
        "rule_strength": "CONDITIONAL",
        "source": "OpenType font specifications; HarfBuzz glyph positions",
        "source_url": [
            "https://learn.microsoft.com/en-us/typography/opentype/spec/",
            "https://harfbuzz.github.io/harfbuzz-hb-buffer.html#hb-glyph-position-t",
        ],
        "source_version": "Not inspected by this runtime",
        "document_status": "Technical specification/API documentation",
        "scope": "No font or renderer input is accepted by this runtime",
        "verification_method": "not_available_in_runtime",
        "evidence_status": "UNVERIFIED: font coverage and fallback are outside this runtime",
    },
    "MIX-005": {
        "knowledge_kind": "NORMATIVE",
        "rule_strength": "PROJECT_POLICY",
        "source": "Caller-supplied editorial profile",
        "source_url": None,
        "source_version": "Input profile",
        "document_status": "Project policy; not SI conformance",
        "scope": "Standalone numeric tokens selected by profile.si_spacing",
        "verification_method": "source_text_token_inspection",
    },
}

def _check(rule_id: str, status: str, **fields: object) -> dict:
    result = {"rule_id": rule_id, "status": status}
    result.update(RULE_METADATA[rule_id])
    result.update(fields)
    return result


def check(payload: dict) -> dict:
    if not isinstance(payload, dict):
        raise ValueError("payload must be an object")
    text = payload.get("text")
    profile = payload.get("profile", {})
    if not isinstance(text, str) or not isinstance(profile, dict):
        raise ValueError("text must be a string and profile must be an object")
    lines = payload.get("rendered_lines")
    checks = []
    si = profile.get("si_spacing", False)
    if not isinstance(si, bool):
        raise ValueError("si_spacing must be a boolean")
    except_tokens = profile.get("except_exact_tokens", [])
    if not isinstance(except_tokens, list) or not all(isinstance(v, str) for v in except_tokens):
        raise ValueError("except_exact_tokens must be a list of strings")
    if si:
        # Restricted to unambiguous unit tokens; product identifiers require
        # caller-supplied exceptions and are never rewritten automatically.
        exceptions = set(except_tokens)
        matches = list(re.finditer(r"(?<![\w.,+\-])\d+(?:\.\d+)?(?:mm|cm|km|kg)(?![\w])", text))
        bad = [m.group() for m in matches if m.group() not in exceptions]
        # No recognized unit token means this narrow probe did not apply a rule.
        # In particular, a token attached to a word is not a verified SI pass.
        status = "NOT_APPLICABLE" if not matches else ("FINDING" if bad else "PASS")
        checks.append(_check("MIX-005", status, matches=bad,
                             severity="UNDETERMINED",
                             message="Review number/SI-unit spacing under the explicit SI editorial profile"))
    else:
        checks.append(_check("MIX-005", "NOT_APPLICABLE",
                             reason="No SI editorial profile"))

    if lines is None:
        checks.append(_check("MIX-001", "UNVERIFIED",
                             reason="Actual rendered lines unavailable"))
    elif not isinstance(lines, list) or not all(isinstance(x, str) for x in lines):
        checks.append(_check("MIX-001", "BLOCKED",
                             reason="rendered_lines must be an array of strings"))
    elif "".join(lines) != text.replace("\r", "").replace("\n", ""):
        checks.append(_check("MIX-001", "BLOCKED",
                             reason="Provided lines do not match the source text"))
    elif profile.get("korean_horizontal_break_check") is not True:
        checks.append(_check("MIX-001", "NOT_APPLICABLE",
                             reason="No explicit Korean horizontal line-break profile"))
    else:
        # Surface *candidates* only. UAX #14/KLReq full tailoring is not implemented.
        findings = []
        for i, line in enumerate(lines):
            if i and line and line[0] in CLOSING:
                findings.append({"line_index": i, "type": "closing_at_start"})
            if i < len(lines) - 1 and line and line[-1] in OPENING:
                findings.append({"line_index": i, "type": "opening_at_end"})
        checks.append(_check("MIX-001", "FINDING" if findings else "NO_SIMPLE_ANOMALY",
                             candidates=findings, severity="UNDETERMINED",
                             limit="not a Unicode/KLReq-conformant breaking engine"))

    checks.append(_check("MIX-003", "UNVERIFIED",
                         reason="Font coverage and actual fallback need font and renderer evidence"))
    return {"schema": "mixed-text-probe-v0", "read_only": True,
            "scope": "limited text-level inspection", "checks": checks}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path, help="JSON with text, profile, optional rendered_lines")
    args = parser.parse_args()
    print(json.dumps(check(json.loads(args.input.read_text(encoding="utf-8"))),
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
