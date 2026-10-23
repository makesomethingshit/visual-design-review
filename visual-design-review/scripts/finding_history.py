#!/usr/bin/env python3
"""Read-only comparison of stable design finding IDs across reviewed versions."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

TRUSTED_BBOX = {"VERIFIED_SOURCE", "MEASURED_RASTER"}
VALID_COVERAGE = {"PARTIAL", "FULL_COMPARABLE"}
STATES = {"NEW", "PERSISTING", "RESOLVED", "REGRESSED", "INCONCLUSIVE"}


def by_id(entries: list[dict]) -> dict[str, dict]:
    if not isinstance(entries, list):
        raise ValueError("findings must be a list")
    result = {}
    for row in entries:
        if not isinstance(row, dict):
            raise ValueError("Each finding must be an object")
        key = row.get("finding_id")
        if not isinstance(key, str) or not key:
            raise ValueError("Each finding needs a non-empty finding_id")
        if key in result:
            raise ValueError(f"Duplicate finding_id: {key}")
        if row.get("state") is not None and row["state"] not in STATES:
            raise ValueError(f"{key}: unsupported current state")
        object_ids = row.get("object_ids")
        if object_ids is not None:
            if (not isinstance(object_ids, list)
                    or any(not isinstance(object_id, str) or not object_id
                           for object_id in object_ids)
                    or len(object_ids) != len(set(object_ids))):
                raise ValueError(f"{key}: object_ids must be unique non-empty strings")
            if object_ids and row.get("object_id_evidence") != "VERIFIED_SOURCE":
                raise ValueError(f"{key}: object IDs require verified source evidence")
        bbox = row.get("bbox")
        bbox_evidence = row.get("bbox_evidence")
        if bbox_evidence is not None and bbox_evidence not in TRUSTED_BBOX:
            raise ValueError(f"{key}: unsupported bbox evidence")
        if bbox is not None:
            if bbox_evidence not in TRUSTED_BBOX:
                raise ValueError(f"{key}: exact bbox requires measured/source evidence")
            if (not isinstance(bbox, list) or len(bbox) != 4
                    or any(isinstance(value, bool)
                           or not isinstance(value, (int, float))
                           or not math.isfinite(value) for value in bbox)
                    or bbox[2] <= 0 or bbox[3] <= 0):
                raise ValueError(f"{key}: bbox must be four finite values with positive size")
            coordinate_system = row.get("coordinate_system")
            if not isinstance(coordinate_system, str) or not coordinate_system.strip():
                raise ValueError(f"{key}: exact bbox needs a coordinate system")
        result[key] = row
    return result


def compare(before: dict, after: dict) -> list[dict]:
    if not isinstance(before, dict) or not isinstance(after, dict):
        raise ValueError("Snapshots must be objects")
    for snapshot in (before, after):
        coverage = snapshot.get("review_coverage")
        if coverage is not None and coverage not in VALID_COVERAGE:
            raise ValueError("review_coverage must be PARTIAL or FULL_COMPARABLE")
    old = by_id(before.get("findings", []))
    new = by_id(after.get("findings", []))
    complete = after.get("review_coverage") == "FULL_COMPARABLE"
    results = []
    for finding_id in sorted(set(old) | set(new)):
        if finding_id in old and old[finding_id].get("state") == "INCONCLUSIVE":
            # An unresolved prior observation is not evidence of a continuing
            # finding. Neither a new active row nor its absence establishes
            # continuity or resolution, even with FULL_COMPARABLE coverage.
            state = "INCONCLUSIVE"
        elif finding_id in new and new[finding_id].get("state") in {"RESOLVED", "INCONCLUSIVE"}:
            state = new[finding_id]["state"]
        elif finding_id in old and finding_id in new:
            # Compare with the immediately preceding snapshot, not its history.
            state = ("REGRESSED" if old[finding_id].get("state") == "RESOLVED"
                     else "PERSISTING")
        elif finding_id in new:
            state = ("REGRESSED" if new[finding_id].get("previous_state") == "RESOLVED"
                     else "NEW")
        else:
            state = ("RESOLVED" if complete or old[finding_id].get("state") == "RESOLVED"
                     else "INCONCLUSIVE")
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
