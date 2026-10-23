#!/usr/bin/env python3
"""Read-only comparison of stable design finding IDs across reviewed versions."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

TRUSTED_BBOX = {"VERIFIED_SOURCE", "MEASURED_RASTER"}


def by_id(entries: list[dict]) -> dict[str, dict]:
    result = {}
    for row in entries:
        key = row.get("finding_id")
        if not isinstance(key, str) or not key:
            raise ValueError("Each finding needs a non-empty finding_id")
        if key in result:
            raise ValueError(f"Duplicate finding_id: {key}")
        if row.get("bbox") is not None and row.get("bbox_evidence") not in TRUSTED_BBOX:
            raise ValueError(f"{key}: exact bbox requires measured/source evidence")
        result[key] = row
    return result


def compare(before: dict, after: dict) -> list[dict]:
    old = by_id(before.get("findings", []))
    new = by_id(after.get("findings", []))
    complete = after.get("review_coverage") == "FULL_COMPARABLE"
    results = []
    for finding_id in sorted(set(old) | set(new)):
        if finding_id in old and finding_id in new:
            state = ("REGRESSED" if old[finding_id].get("previous_state") == "RESOLVED"
                     else "PERSISTING")
        elif finding_id in new:
            state = ("REGRESSED" if new[finding_id].get("previous_state") == "RESOLVED"
                     else "NEW")
        else:
            state = "RESOLVED" if complete else "INCONCLUSIVE"
        results.append({"finding_id": finding_id, "state": state,
                        "evidence": "stable_id_only",
                        "warning": "ID continuity is supplied, not visually verified"})
    return results


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("before", type=Path)
    p.add_argument("after", type=Path)
    a = p.parse_args()
    old = json.loads(a.before.read_text(encoding="utf-8"))
    new = json.loads(a.after.read_text(encoding="utf-8"))
    print(json.dumps(compare(old, new), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
