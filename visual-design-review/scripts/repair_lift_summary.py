#!/usr/bin/env python3
"""Evidence-aware, non-aesthetic aggregation of before/after design repairs."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

STATUSES = {"PASS", "FAIL", "BLOCKED", "UNVERIFIED", "INCONCLUSIVE"}


def summarize(samples: list[dict]) -> dict:
    outcomes = []
    counts = {"RESOLVED": 0, "UNCHANGED": 0, "REGRESSION": 0,
              "INCONCLUSIVE": 0, "BLOCKED": 0}
    for s in samples:
        name = s.get("id")
        if not isinstance(name, str) or not name:
            raise ValueError("Every sample requires a stable id")
        domain = s.get("domain")
        if domain not in {"deterministic", "perceptual"}:
            raise ValueError("domain must be deterministic or perceptual")
        before, after = s.get("before_status"), s.get("after_status")
        if before not in STATUSES or after not in STATUSES:
            raise ValueError("Before and after must use explicit statuses")
        if before == "BLOCKED" or after == "BLOCKED":
            outcome = "BLOCKED"
        elif (not s.get("before_artifact_hash") or not s.get("after_artifact_hash")
              or not s.get("verification_evidence")):
            outcome = "INCONCLUSIVE"
        elif domain == "perceptual":
            # A declared expert rating is evidence to review, not a machine
            # guarantee that a subjective aesthetic comparison improved.
            outcome = "INCONCLUSIVE"
        elif "UNVERIFIED" in {before, after} or "INCONCLUSIVE" in {before, after}:
            outcome = "INCONCLUSIVE"
        elif before == "FAIL" and after == "PASS":
            outcome = "RESOLVED"
        elif before == "PASS" and after == "FAIL":
            outcome = "REGRESSION"
        else:
            outcome = "UNCHANGED"
        counts[outcome] += 1
        outcomes.append({"id": name, "domain": domain, "outcome": outcome})
    return {"schema": "repair-lift-v0", "counts": counts,
            "sample_results": outcomes, "aesthetic_score": None,
            "warning": "Not an expert preference or global design quality score"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("cases", type=Path)
    args = parser.parse_args()
    raw = json.loads(args.cases.read_text(encoding="utf-8"))
    print(json.dumps(summarize(raw["samples"]), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
