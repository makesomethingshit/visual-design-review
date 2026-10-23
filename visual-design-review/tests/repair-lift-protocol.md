# Design critique repair-lift evaluation — draft (#13)

**Question:** does a design review lead to a measured improvement when an independent editor/reviser acts on it? This is **not** Issue #7's test of routing, reference reads, or rule-contract compliance. Both must be measured independently.

## Candidate design

- Each fixture has a design brief and actual versioned artifacts `original → critique → revision → verification`, with hashes, medium, constraints and documented intended expression.
- **Deterministic cases** (e.g., clipped required text, print output failure, incorrect source numbers) need an authenticated checker outcome and same production profile before/after.
- **Perceptual/contextual cases** (e.g., Korean–Latin font pairing, hierarchy, poster composition) require independent expert pairwise evaluation. A machine can record ratings and disagreements but must not infer a single aesthetic truth.
- Keep both `baseline feedback` and `skill feedback` arms only when same editor, time budget, model/tool, brief and source can reasonably be controlled. Do not equate a before/after observation with a causal A/B difference.
- Swap presentation order for human/AI judges; record ties, counter interpretations, added regressions and the cost of correction.

## Example schema (NOT actual experimental results)

```json
{
  "samples": [{
    "id": "demo-01",
    "domain": "deterministic",
    "before_status": "UNVERIFIED",
    "after_status": "UNVERIFIED",
    "before_artifact_hash": null,
    "after_artifact_hash": null,
    "verification_evidence": [],
    "editor": null,
    "time_budget": null
  }]
}
```

`repair_lift_summary.py` is a **caller-declaration reporter** for explicitly supplied deterministic statuses. It never runs a repair, editor, PDF preflight, or perceptual evaluation. It will keep all unverified/subjective samples INCONCLUSIVE. Text-only descriptions are not evidence of finished designs.

### Declaration-only output and aggregation unit

The draft output contract is `repair-lift-declarations-v1` (replaces the unreleased v0
`counts`/`outcome` fields). `declared_counts` and per-row `declared_outcome` contain only
RESOLVED_CANDIDATE / UNCHANGED_CANDIDATE / REGRESSION_CANDIDATE, INCONCLUSIVE, or BLOCKED.
`independent_verification` is always UNVERIFIED and `verified_counts` is null, not zero.
Opaque artifact references and evidence-reference strings are not authenticated by this code.

`id` is the unique run-record ID within an aggregation; duplicates are rejected.
Optional `fixture_id` groups distinct repeated runs of the same design. Counting two
explicit runs is not a claim that two different designs improved.

`verification_evidence` accepts non-empty reference strings only. Imported structured
PASS or UNVERIFIED reports are unsupported and remain INCONCLUSIVE, even if outer
statuses claim FAIL → PASS. There is no automatic #19 → #20 pipeline or attestation parser.

Before describing any candidate as a verified improvement, an independent caller/evaluator
must bind before/after evidence to the exact artifact versions, the same checker/version
and production profile, verify evidence/status consistency, and retain the actual results.
That verifier is not implemented by this reporter. This draft preserves references and
declarations for later review without inventing verified evidence.

## Acceptance needed before leaving Draft

- [ ] At least three actual versioned design tasks: poster, Korean–English print text, print-ready output
- [ ] For each: visible source artifact, critique, fixed result, explicit design intent, independent verification
- [ ] Baseline skill vs changed skill kept separate from before/after comparison; consider revisor/action budget
- [ ] Negative repair: suggested change made but target was not fixed or a new defect was introduced
- [ ] Blind human comparison for non-deterministic targets, with order swap and dissent logged
- [ ] Provenance and `BLOCKED/INCONCLUSIVE` never counted as success

## Run

```sh
python -m unittest discover -s tests -p 'test_repair_lift_summary.py'
python visual-design-review/scripts/repair_lift_summary.py path/to/real-cases.json
```

References: [UICrit](https://arxiv.org/abs/2407.08850) and work on [actionable UX critiques](https://arxiv.org/) as methodology background only. UI findings are not automatically evidence about printed graphic design.
