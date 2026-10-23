#!/usr/bin/env python3
"""Limited, read-only mixed-script typography probe. No font/render claims."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

CLOSING = frozenset(")]}〉》」』】、。，．！？!?,.;:)]")
OPENING = frozenset("([{〈《「『【")


def check(payload: dict) -> dict:
    text = payload.get("text")
    profile = payload.get("profile", {})
    if not isinstance(text, str) or not isinstance(profile, dict):
        raise ValueError("text must be a string and profile must be an object")
    lines = payload.get("rendered_lines")
    checks = []
    si = profile.get("si_spacing", False)
    if not isinstance(si, bool):
        raise ValueError("si_spacing must be a boolean")
    if si:
        # Restricted to unambiguous unit tokens; product identifiers require
        # caller-supplied exceptions and are never rewritten automatically.
        exceptions = set(profile.get("except_exact_tokens", []))
        matches = list(re.finditer(r"(?<![\w])\d+(?:\.\d+)?(?:mm|cm|km|kg)(?![\w])", text))
        bad = [m.group() for m in matches if m.group() not in exceptions]
        # No recognized unit token means this narrow probe did not apply a rule.
        # In particular, a token attached to a word is not a verified SI pass.
        status = "NOT_APPLICABLE" if not matches else ("FINDING" if bad else "PASS")
        checks.append({"rule_id": "MIX-005", "status": status,
                       "matches": bad, "severity": "UNDETERMINED",
                       "message": "Review number/SI-unit spacing under the explicit SI editorial profile"})
    else:
        checks.append({"rule_id": "MIX-005", "status": "NOT_APPLICABLE",
                       "reason": "No SI editorial profile"})

    if lines is None:
        checks.append({"rule_id": "MIX-001", "status": "UNVERIFIED",
                       "reason": "Actual rendered lines unavailable"})
    elif not isinstance(lines, list) or not all(isinstance(x, str) for x in lines):
        checks.append({"rule_id": "MIX-001", "status": "BLOCKED",
                       "reason": "rendered_lines must be an array of strings"})
    elif "".join(lines) != text.replace("\n", ""):
        checks.append({"rule_id": "MIX-001", "status": "BLOCKED",
                       "reason": "Provided lines do not match the source text"})
    elif profile.get("korean_horizontal_break_check") is not True:
        checks.append({"rule_id": "MIX-001", "status": "NOT_APPLICABLE",
                       "reason": "No explicit Korean horizontal line-break profile"})
    else:
        # Surface *candidates* only. UAX #14/KLReq full tailoring is not implemented.
        findings = []
        for i, line in enumerate(lines):
            if i and line and line[0] in CLOSING:
                findings.append({"line_index": i, "type": "closing_at_start"})
            if i < len(lines) - 1 and line and line[-1] in OPENING:
                findings.append({"line_index": i, "type": "opening_at_end"})
        checks.append({"rule_id": "MIX-001", "status": "FINDING" if findings else "NO_SIMPLE_ANOMALY",
                       "candidates": findings, "severity": "UNDETERMINED",
                       "limit": "not a Unicode/KLReq-conformant breaking engine"})

    checks.append({"rule_id": "MIX-003", "status": "UNVERIFIED",
                   "reason": "Font coverage and actual fallback need font and renderer evidence"})
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
