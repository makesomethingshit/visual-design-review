#!/usr/bin/env bash
# All source copies and CODEX_HOME values are isolated under one temporary root.
set -euo pipefail
root="$(cd -- "$(dirname -- "$0")/.." && pwd -P)"
sandbox="$(mktemp -d)"
trap 'rm -rf -- "$sandbox"' EXIT
fail() { echo "FAIL: $*" >&2; exit 1; }
mkdir -p "$sandbox/repo/scripts"
cp "$root/scripts/install-linux.sh" "$sandbox/repo/scripts/"
cp -a "$root/visual-design-review" "$sandbox/repo/"
installer="$sandbox/repo/scripts/install-linux.sh"
source_copy="$sandbox/repo/visual-design-review"
ln -s "$source_copy" "$sandbox/source-alias"
nested_home="$sandbox/source-alias/new-home/deeper"

# Check dry-run before the real operation: a regression must never mutate source.
for action in install check; do
  for dry in --dry-run ''; do
    if output="$(CODEX_HOME="$nested_home" /bin/bash "$installer" "$action" $dry 2>&1)"; then
      fail "source ancestor link accepted: $action $dry"
    else status=$?; fi
    [[ "$status" -eq 2 && "$output" == *'must not be inside the source'* ]] ||
      fail "wrong source ancestor rejection: $output"
    [[ ! -e "$source_copy/new-home" ]] || fail 'source was mutated before rejection'
  done
done

# A safe alias with missing descendants remains a valid install destination.
mkdir "$sandbox/outside"
ln -s "$sandbox/outside" "$sandbox/safe-alias"
export CODEX_HOME="$sandbox/safe-alias/new-home/deeper"
/bin/bash "$installer" install --dry-run >/dev/null
[[ ! -e "$sandbox/outside/new-home" ]] || fail 'safe dry-run created directories'
/bin/bash "$installer" install >/dev/null
/bin/bash "$installer" check >/dev/null
/bin/bash "$installer" remove >/dev/null
[[ ! -e "$CODEX_HOME/skills/visual-design-review" ]] || fail 'safe remove left active skill'

# Long valid SKILL.md must not trip pipefail when a reader stops after frontmatter.
printf '\n' >> "$source_copy/SKILL.md"
awk 'BEGIN { for (i=0; i<10000; i++) print "Long valid body text for frontmatter pipe regression." }' >> "$source_copy/SKILL.md"
export CODEX_HOME="$sandbox/long-document-home"
/bin/bash "$installer" install --dry-run >/dev/null
/bin/bash "$installer" install >/dev/null
/bin/bash "$installer" check >/dev/null
/bin/bash "$installer" remove >/dev/null

# A dangling ancestor is not silently treated as a resolvable directory.
ln -s "$sandbox/missing" "$sandbox/dangling"
if CODEX_HOME="$sandbox/dangling/new-home" /bin/bash "$installer" install --dry-run >/dev/null 2>&1; then
  fail 'dangling ancestor accepted'
fi
[[ ! -e "$sandbox/missing" ]] || fail 'dangling ancestor caused directory creation'
echo 'PASS: linked source ancestor, missing descendants, safe alias, dangling ancestor'
