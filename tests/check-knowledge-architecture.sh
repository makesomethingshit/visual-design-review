#!/usr/bin/env bash
# Static architecture invariants; not a model routing or visual quality evaluation.
set -euo pipefail
root="$(cd -- "$(dirname -- "$0")/.." && pwd -P)"
package="$root/visual-design-review"
fail() { printf 'FAIL: %s\n' "$*" >&2; exit 1; }
for ref in knowledge-routing review-protocol critique-rubric review-output reference-analysis formula-relations typography-relations typography-presets design-handoff; do
  [[ -f "$package/references/$ref.md" ]] || fail "missing reference $ref"
  grep -Fq "references/$ref.md" "$package/SKILL.md" || fail "unreachable reference $ref"
done
for name in T-METRICS T-SPACING T-MEASURE T-LEADING T-CAPACITY T-HIERARCHY; do
  grep -Fq "$name" "$package/references/typography-relations.md" || fail "missing typography model $name"
done
grep -Fq 'UNVERIFIED' "$package/references/typography-relations.md" || fail 'unverified state contract missing'
policy="$package/references/typography-presets.md"
for key in A B C D E F G H; do
  grep -Fq "| $key |" "$policy" || fail "approved policy $key missing"
done
for value in '1.7' '1.5' '2.0' '10pt' '30칸' 'Tracking 0' '왼끝맞춤'; do
  grep -Fq "$value" "$policy" || fail "approved policy value $value missing"
done
grep -Fq 'USER_APPROVED_PROJECT_POLICY' "$policy" || fail 'approval provenance absent'
grep -Fq '명시된 사용자' "$policy" || fail 'user override absent'
grep -Fq '기존 작품 비평' "$policy" || fail 'review exclusion absent'
grep -Fq 'PR #5' "$root/docs/skill-architecture-extension.md" || fail 'source attribution missing'
grep -Fq 'reference-analysis' "$root/docs/skill-architecture-extension.md" || fail 'reference reverse engineering omitted'
# The canonical root ARCHITECTURE.md is supplied by #5; it may exist after that PR merges.
# Compare the PR diff to detect overlapping edits; do not require the file to be absent.
awk 'BEGIN {
  if ((148 - 12 * 2 - 5 * 2) / 3 != 38) exit 1
  if (10 * 1.7 != 17) exit 1
  if (10 * 1.5 != 15) exit 1
  if (10 * 2 != 20) exit 1
  if (10 * 30 != 300) exit 1
  if (1024 / 2048 * 12 != 6) exit 1
}' || fail 'numeric example arithmetic regression'
python3 "$root/tests/check-knowledge-contract.py"
python3 -m unittest discover -s "$root/tests" -p 'test_*.py'
echo 'PASS: architecture references, ownership boundary, formula examples'
