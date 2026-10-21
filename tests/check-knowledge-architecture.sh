#!/usr/bin/env bash
# Static architecture invariants; not a model routing or visual quality evaluation.
set -euo pipefail
root="$(cd -- "$(dirname -- "$0")/.." && pwd -P)"
package="$root/visual-design-review"
fail() { printf 'FAIL: %s\n' "$*" >&2; exit 1; }
for ref in knowledge-routing review-protocol critique-rubric review-output reference-analysis formula-relations typography-relations design-handoff; do
  [[ -f "$package/references/$ref.md" ]] || fail "missing reference $ref"
  grep -Fq "references/$ref.md" "$package/SKILL.md" || fail "unreachable reference $ref"
done
for name in T-METRICS T-SPACING T-MEASURE T-LEADING T-CAPACITY T-HIERARCHY; do
  grep -Fq "$name" "$package/references/typography-relations.md" || fail "missing typography model $name"
done
grep -Fq 'UNVERIFIED' "$package/references/typography-relations.md" || fail 'unverified state contract missing'
grep -Fq 'PR #5' "$root/docs/skill-architecture-extension.md" || fail 'source attribution missing'
grep -Fq 'reference-analysis' "$root/docs/skill-architecture-extension.md" || fail 'reference reverse engineering omitted'
# The canonical root ARCHITECTURE.md is supplied by #5; it may exist after that PR merges.
# Compare the PR diff to detect overlapping edits; do not require the file to be absent.
awk 'BEGIN {
  if ((148 - 12 * 2 - 5 * 2) / 3 != 38) exit 1
  if (10 * 1.7 != 17) exit 1
  if (1024 / 2048 * 12 != 6) exit 1
}' || fail 'numeric example arithmetic regression'
echo 'PASS: architecture references, ownership boundary, formula examples'
