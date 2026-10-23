#!/usr/bin/env python3
"""Aggregate caller declarations only; never attest independently verified repairs."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

STATUSES = {"PASS", "FAIL", "BLOCKED", "UNVERIFIED", "INCONCLUSIVE"}


def summarize(samples: list[dict]) -> dict:
    outcomes = []
    seen = set()
    counts = {"RESOLVED_CANDIDATE": 0, "UNCHANGED_CANDIDATE": 0, "REGRESSION_CANDIDATE": 0,
              "INCONCLUSIVE": 0, "BLOCKED": 0}
    for s in samples:
        name = s.get("id")
        if not isinstance(name, str) or not name:
            raise ValueError("Every sample requires a stable id")
        if name in seen:
            raise ValueError(f"Duplicate run id: {name}")
        seen.add(name)
        domain = s.get("domain")
        if domain not in {"deterministic", "perceptual"}:
            raise ValueError("domain must be deterministic or perceptual")
        before, after = s.get("before_status"), s.get("after_status")
        if before not in STATUSES or after not in STATUSES:
            raise ValueError("Before and after must use explicit statuses")
        evidence = s.get("verification_evidence")
        # This reporter accepts references, not imported verifier attestations.
        # A structured UNVERIFIED report must not be promoted by outer statuses.
        reference_only = (isinstance(evidence, list) and bool(evidence)
                          and all(isinstance(ref, str) and ref.strip() for ref in evidence))
        if before == "BLOCKED" or after == "BLOCKED":
            outcome = "BLOCKED"
        elif (not s.get("before_artifact_hash") or not s.get("after_artifact_hash")
              or not reference_only):
            outcome = "INCONCLUSIVE"
        elif (s["before_artifact_hash"] == s["after_artifact_hash"]
              and before != after):
            # A changed result for identical artifact bytes is not repair
            # evidence; the checker/profile or declaration may have changed.
            outcome = "INCONCLUSIVE"
        elif domain == "perceptual":
            # A declared expert rating is evidence to review, not a machine
            # guarantee that a subjective aesthetic comparison improved.
            outcome = "INCONCLUSIVE"
        elif "UNVERIFIED" in {before, after} or "INCONCLUSIVE" in {before, after}:
            outcome = "INCONCLUSIVE"
        elif before == "FAIL" and after == "PASS":
            outcome = "RESOLVED_CANDIDATE"
        elif before == "PASS" and after == "FAIL":
            outcome = "REGRESSION_CANDIDATE"
        else:
            outcome = "UNCHANGED_CANDIDATE"
        counts[outcome] += 1
        outcomes.append({"id": name, "fixture_id": s.get("fixture_id"), "domain": domain,
                         "declared_outcome": outcome, "independent_verification": "UNVERIFIED"})
    return {"schema": "repair-lift-declarations-v1", "declared_counts": counts,
            "verified_counts": None, "independent_verification": "UNVERIFIED",
            "sample_results": outcomes, "aesthetic_score": None,
            "warning": "Caller-reported candidates only; hashes/references are not authenticated; "
                       "not verified repair counts, expert preference, or a global quality score"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("cases", type=Path)
    args = parser.parse_args()
    raw = json.loads(args.cases.read_text(encoding="utf-8"))
    print(json.dumps(summarize(raw["samples"]), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
