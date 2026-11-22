#!/usr/bin/env bash
# Static architecture invariants; not a model routing or visual quality evaluation.
set -euo pipefail
root="$(cd -- "$(dirname -- "$0")/.." && pwd -P)"
planning="$root/visual-design-planning"
drafting="$root/visual-design-drafting"
review="$root/visual-design-review"
fail() { printf 'FAIL: %s\n' "$*" >&2; exit 1; }

# Level 1 planning: workflow plus one method card per index entry.
[[ -f "$planning/SKILL.md" ]] || fail 'planning SKILL.md missing'
grep -Fq '(references/workflow/level-1.md)' "$planning/SKILL.md" || fail 'level 1 workflow not linked from planning SKILL.md'
[[ -f "$planning/references/workflow/level-1.md" ]] || fail 'level 1 workflow missing'
[[ -f "$planning/references/methods/01.methods-index.md" ]] || fail 'methods index missing'
[[ ! -e "$review/references/methods" && ! -e "$review/references/workflow" ]] ||
  fail 'level 1 knowledge left inside the review skill'

# Level 2 drafting: workflow skeleton and the level 3 handoff boundary.
[[ -f "$drafting/SKILL.md" ]] || fail 'drafting SKILL.md missing'
grep -Fq '(references/workflow/level-2.md)' "$drafting/SKILL.md" || fail 'level 2 workflow not linked from drafting SKILL.md'
[[ -f "$drafting/references/workflow/level-2.md" ]] || fail 'level 2 workflow missing'
for step in '## 1. 인계 자산 로드' '## 2. 조형 번역' '## 3. 복수 시안 생성' '## 4. 선택·확정 및 인계'; do
  grep -Fq "$step" "$drafting/references/workflow/level-2.md" || fail "level 2 step missing: $step"
done
grep -Fq 'visual-design-review' "$drafting/SKILL.md" || fail 'drafting must name the level 3 skill'
grep -Fq 'design-handoff' "$drafting/references/workflow/level-2.md" || fail 'level 3 handoff contract not named'

# Level 3 review: knowledge reachable from its own SKILL.md.
for ref in knowledge-routing review-protocol critique-rubric review-output reference-analysis formula-relations typography-relations typography-presets design-handoff; do
  [[ -f "$review/references/$ref.md" ]] || fail "missing reference $ref"
  grep -Fq "(references/$ref.md)" "$review/SKILL.md" || fail "unreachable reference $ref"
done
for name in T-METRICS T-SPACING T-MEASURE T-LEADING T-CAPACITY T-HIERARCHY; do
  grep -Fq "$name" "$review/references/typography-relations.md" || fail "missing typography model $name"
done
grep -Fq 'UNVERIFIED' "$review/references/typography-relations.md" || fail 'unverified state contract missing'
policy="$review/references/typography-presets.md"
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
# Product-correct is an explicit-write opt-in; static reachability only, not GitHub agent E2E.
[[ -f "$review/references/product-correct.md" ]] || fail 'product-correct reference missing'
grep -Fq '(references/product-correct.md)' "$review/SKILL.md" || fail 'product-correct not routed from SKILL'
grep -Fq 'product-correct' "$review/references/knowledge-routing.md" || fail 'product-correct route missing'
[[ -f "$review/tests/product-correct-cases.md" ]] || fail 'product-correct manual cases missing'
grep -Fq '| PC-01 |' "$review/tests/product-correct-cases.md" || fail 'product-correct no-write negative case missing'
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
echo 'PASS: level 1-2-3 boundaries, architecture references, formula examples'
