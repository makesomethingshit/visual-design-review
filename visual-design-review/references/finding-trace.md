# Finding trace — draft evidence/iteration schema (#11)

This module is **optional** and does not replace the existing Quick/Deep prose format. It is for versioned repeat reviews where real page/frame/object evidence exists. No adapter or automatic editing is implemented here.

```yaml
artifact_version: "user-supplied-version"
review_coverage: PARTIAL  # or FULL_COMPARABLE
findings:
  - finding_id: F1
    page_id: "1"
    object_ids: []        # only source-verified IDs
    region_note: "left text block"
    bbox: null            # only if actually measured
    bbox_evidence: null   # VERIFIED_SOURCE | MEASURED_RASTER
    observation_evidence: "user-provided screenshot region"
    observed_impact: "depends on actual brief"
    uncertainty: "PROBABLE"
    previous_state: null
    state: NEW           # current snapshot state; RESOLVED can retain a history tombstone
    verification_request: "inspect at actual output size"
```

A visual region label is **not** an object ID. A pixel bbox needs documented coordinate system, source frame bounds, resize/crop transform and actual measurement. Print millimeters require reliable physical scale. Unverified source positions must not be fabricated.

**History states:** `NEW / PERSISTING / RESOLVED / REGRESSED / INCONCLUSIVE`. Exact IDs in two snapshots are treated as *user-provided* continuity, not visual confirmation. The accompanying `finding_history.py` comparator is a narrow deterministic draft and cannot infer visually equivalent renamed objects.

**Resolution guard:** absence of a finding after a partial review is **INCONCLUSIVE**, not RESOLVED. Even under `FULL_COMPARABLE`, the comparator records a status **candidate**; physical improvement still needs actual artifact review. A prior RESOLVED finding reappearing is REGRESSED only when stable identity and history are supplied.

`state` records the current snapshot; `previous_state` is historical metadata.
When the same ID is active in both snapshots, the result is PERSISTING even if an older
`previous_state` says RESOLVED. A RESOLVED tombstone in the immediately previous snapshot
followed by an active finding is REGRESSED. The legacy current-row `previous_state` fallback
is used only when the ID is absent from the before snapshot; it is a caller-provided assertion.
An explicitly resolved or inconclusive current row retains that declared candidate state.
An immediately previous **INCONCLUSIVE** finding is *not* a confirmed active
observation: a new row with that ID (including one labelled NEW/PERSISTING) cannot
be silently counted as PERSISTING. If the ID disappears, even from a nominally
FULL_COMPARABLE snapshot, the prior uncertainty alone does not prove RESOLVED.
Both cases remain INCONCLUSIVE until continuity or actual resolution is established
outside this ID-only helper. The chain RESOLVED → REGRESSED → PERSISTING is unchanged.

**Severity:** no numeric area score automatically upgrades Critical/Major. Existing finding contract (location, observation, impact, counter-interpretation, action, verification) remains authoritative.

Run the draft test from repository root:
```sh
python -m unittest discover -s tests -p 'test_finding_history.py'
```

**Limitations:** no bbox extractor, no object matching, no PDF/Figma connector, no rendered before/after validation. This is a storage contract + exact-ID status helper.
