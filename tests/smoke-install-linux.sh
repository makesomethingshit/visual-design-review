#!/usr/bin/env bash
# Offline filesystem test; does not touch the user's real CODEX_HOME.
set -euo pipefail
root="$(cd -- "$(dirname -- "$0")/.." && pwd -P)"
sandbox="$(mktemp -d)"
trap 'rm -rf -- "$sandbox"' EXIT
installer="$root/scripts/install-linux.sh"
# Catch shell parse regressions before any install/dry-run assertions.
bash -n "$installer" || { echo "FAIL: installer syntax check" >&2; exit 1; }
SKILLS=(visual-design-planning visual-design-drafting visual-design-review)
fail() { echo "FAIL: $*" >&2; exit 1; }
active_skill_dirs() { find "$1/skills" -mindepth 1 -maxdepth 1 -type d | wc -l; }
skill_files() { find "$1/skills" -name SKILL.md | wc -l; }

lifecycle() {
  local name="$1"
  export CODEX_HOME="$sandbox/home-$name"
  local target="$CODEX_HOME/skills/$name"
  local backups_dir="$CODEX_HOME/skill-backups/$name"
  local output backup restored dir

  bash "$installer" install --dry-run >/dev/null
  [[ ! -e "$CODEX_HOME" ]] || fail 'dry-run modified filesystem'
  bash "$installer" install >/dev/null
  bash "$installer" check >/dev/null
  [[ -f "$target/SKILL.md" ]] || fail 'skill missing'
  [[ ! -e "$backups_dir" ]] || fail 'fresh install created backup'
  [[ "$(active_skill_dirs "$CODEX_HOME")" -eq "${#SKILLS[@]}" ]] || fail 'not every skill was installed'
  output="$(bash "$installer" install)"
  [[ "$output" == *'Already up to date'* ]] || fail 'second install was not idempotent'

  printf '\nlocal-change\n' >> "$target/SKILL.md"
  bash "$installer" install --dry-run >/dev/null
  [[ "$(tail -n 1 "$target/SKILL.md")" == 'local-change' ]] || fail 'update dry-run wrote files'
  bash "$installer" install >/dev/null
  bash "$installer" check >/dev/null
  [[ "$(find "$backups_dir" -mindepth 1 -maxdepth 1 -type d | wc -l)" -eq 1 ]] || fail 'missing update backup'
  backup="$(find "$backups_dir" -mindepth 1 -maxdepth 1 -type d | head -n 1)"
  [[ "$(tail -n 1 "$backup/SKILL.md")" == 'local-change' ]] || fail 'old installation not preserved'
  [[ "$(skill_files "$CODEX_HOME")" -eq "${#SKILLS[@]}" ]] || fail 'duplicate skill after update'

  bash "$installer" remove --dry-run >/dev/null
  [[ -d "$target" ]] || fail 'remove dry-run removed files'
  bash "$installer" remove >/dev/null
  [[ ! -e "$target" ]] || fail 'active skill remains after remove'
  [[ "$(find "$backups_dir" -mindepth 1 -maxdepth 1 -type d | wc -l)" -eq 2 ]] || fail 'removal did not preserve installation'
  [[ "$(skill_files "$CODEX_HOME")" -eq 0 ]] || fail 'backup still discoverable after remove'
}

# Both skills reach one CODEX_HOME; remove and restore cover every active skill.
export CODEX_HOME="$sandbox/shared-home"
bash "$installer" install >/dev/null
bash "$installer" check >/dev/null
[[ "$(skill_files "$CODEX_HOME")" -eq "${#SKILLS[@]}" ]] || fail 'shared home did not install each skill once'
for name in "${SKILLS[@]}"; do
  [[ -f "$CODEX_HOME/skills/$name/SKILL.md" ]] || fail "shared home missing $name"
done
bash "$installer" remove >/dev/null
[[ "$(skill_files "$CODEX_HOME")" -eq 0 ]] || fail 'shared home remove left an active skill'
for name in "${SKILLS[@]}"; do
  [[ -d "$CODEX_HOME/skill-backups/$name" ]] || fail "shared home lost $name backup"
  restored="$(find "$CODEX_HOME/skill-backups/$name" -mindepth 1 -maxdepth 1 -type d | head -n 1)"
  mv -- "$restored" "$CODEX_HOME/skills/$name"
done
bash "$installer" check >/dev/null
[[ "$(skill_files "$CODEX_HOME")" -eq "${#SKILLS[@]}" ]] || fail 'restored skills not uniquely discoverable'
bash "$installer" remove >/dev/null
if bash "$installer" check >/dev/null 2>&1; then fail 'check passed without installation'; fi

for name in "${SKILLS[@]}"; do
  lifecycle "$name"
done

export CODEX_HOME="$sandbox/interaction-home"
bash "$installer" install >/dev/null
if CODEX_HOME='relative/path' bash "$installer" install --dry-run >/dev/null 2>&1; then fail 'relative CODEX_HOME accepted'; fi
printf '\ncorrupted\n' >> "$CODEX_HOME/skills/visual-design-review/SKILL.md"
mkdir "$sandbox/bin"
real_find="$(command -v find)"
printf '#!/usr/bin/env bash\nfor arg in "$@"; do [[ "$arg" != f ]] || exit 1; done\nexec %q "$@"\n' "$real_find" > "$sandbox/bin/find"
chmod +x "$sandbox/bin/find"
if PATH="$sandbox/bin:$PATH" bash "$installer" check >/dev/null 2>&1; then fail 'listing failure reported synced'; fi
if PATH="$sandbox/bin:$PATH" bash "$installer" install >/dev/null 2>&1; then fail 'listing failure allowed activation'; fi
[[ "$(tail -n 1 "$CODEX_HOME/skills/visual-design-review/SKILL.md")" == corrupted ]] || fail 'listing failure changed target'
rm "$sandbox/bin/find"
printf '#!/usr/bin/env bash\nexit 1\n' > "$sandbox/bin/sha256sum"
chmod +x "$sandbox/bin/sha256sum"
if PATH="$sandbox/bin:$PATH" bash "$installer" check >/dev/null 2>&1; then fail 'hash failure reported synced'; fi
bash "$installer" remove >/dev/null

# F-01: fields outside the first frontmatter block must be rejected.
fake_repo="$sandbox/fake-repo"
mkdir -p "$fake_repo/scripts"
cp "$root/scripts/install-linux.sh" "$fake_repo/scripts/"
for name in "${SKILLS[@]}"; do
  cp -a "$root/$name" "$fake_repo/"
done
review_skill="$fake_repo/visual-design-review/SKILL.md"

# Regression: long but valid SKILL.md must not fail validation under pipefail.
# On macOS, printf | head (or early-exiting awk) can fail with SIGPIPE.
awk 'BEGIN {
  for (i = 0; i < 4096; i++) {
    print "long-skill-body-padding-to-detect-premature-consumer-close-on-BSD"
  }
}' >> "$review_skill"
large_home="$sandbox/large-skill-home"
CODEX_HOME="$large_home" bash "$fake_repo/scripts/install-linux.sh" install --dry-run >/dev/null ||
  fail 'large valid SKILL.md failed validation (possible SIGPIPE)'
[[ ! -e "$large_home" ]] || fail 'large-skill dry-run modified filesystem'

awk '
  $0 == "name: visual-design-review" { next }
  { print }
  !closed && NR > 1 && $0 == "---" { print "name: visual-design-review"; closed=1 }
' "$root/visual-design-review/SKILL.md" > "$review_skill"
if output="$(CODEX_HOME="$sandbox/bad-frontmatter-home" bash "$fake_repo/scripts/install-linux.sh" install --dry-run 2>&1)"; then
  fail 'frontmatter fields outside block accepted'
fi
[[ "$output" == *'Source package structure is invalid'* ]] || fail 'wrong frontmatter failure'
[[ ! -e "$sandbox/bad-frontmatter-home" ]] || fail 'invalid frontmatter dry-run created files'

# A version belonging to another mapping is not metadata.version.
awk '{ print; if ($0 == "metadata:") print "other:" }' "$root/visual-design-review/SKILL.md" > "$review_skill"
if CODEX_HOME="$sandbox/bad-frontmatter-home" bash "$fake_repo/scripts/install-linux.sh" install --dry-run >/dev/null 2>&1; then
  fail 'version outside metadata accepted'
fi
[[ ! -e "$sandbox/bad-frontmatter-home" ]] || fail 'invalid metadata created files'

# The planning skill is validated the same way, not only the review skill.
mkdir -p "$sandbox/planning-repo/scripts"
cp "$root/scripts/install-linux.sh" "$sandbox/planning-repo/scripts/"
for name in "${SKILLS[@]}"; do
  cp -a "$root/$name" "$sandbox/planning-repo/"
done
awk '$0 == "name: visual-design-planning" { print "name: visual-design-review"; next } { print }' \
  "$root/visual-design-planning/SKILL.md" > "$sandbox/planning-repo/visual-design-planning/SKILL.md"
if CODEX_HOME="$sandbox/bad-planning-home" bash "$sandbox/planning-repo/scripts/install-linux.sh" install --dry-run >/dev/null 2>&1; then
  fail 'mismatched planning frontmatter name accepted'
fi

# F-02: remove must not depend on a valid source package.
rm -rf "$fake_repo/visual-design-review" "$fake_repo/visual-design-planning"
remove_home="$sandbox/remove-home"
CODEX_HOME="$remove_home" bash "$installer" install >/dev/null
CODEX_HOME="$remove_home" bash "$fake_repo/scripts/install-linux.sh" remove >/dev/null
for name in "${SKILLS[@]}"; do
  [[ ! -e "$remove_home/skills/$name" ]] || fail 'remove failed without source'
  [[ -d "$remove_home/skill-backups/$name" ]] || fail 'remove without source lost backup'
done

# CODEX_HOME nested under either source tree must be rejected before creation.
for name in "${SKILLS[@]}"; do
  nested_home="$root/$name/.nested-codex-home"
  if CODEX_HOME="$nested_home" bash "$installer" install --dry-run >/dev/null 2>&1; then
    fail 'CODEX_HOME inside source accepted'
  fi
  [[ ! -e "$nested_home" ]] || fail 'nested CODEX_HOME was created'
done

# Remove must also reject an existing installation whose home is inside source.
nested_remove_repo="$sandbox/nested-remove-repo"
mkdir -p "$nested_remove_repo/scripts"
cp "$root/scripts/install-linux.sh" "$nested_remove_repo/scripts/"
cp -a "$root/visual-design-review" "$nested_remove_repo/"
nested_remove_installer="$nested_remove_repo/scripts/install-linux.sh"
nested_remove_home="$nested_remove_repo/visual-design-review/.nested-remove-home"
mkdir -p "$nested_remove_home/skills/visual-design-review"
printf 'sentinel\n' > "$nested_remove_home/skills/visual-design-review/SKILL.md"
if output="$(CODEX_HOME="$nested_remove_home" bash "$nested_remove_installer" remove 2>&1)"; then
  fail 'remove accepted CODEX_HOME inside source'
else status=$?; fi
[[ "$status" -eq 2 && "$output" == *'must not be inside the source'* ]] ||
  fail "wrong nested remove rejection: $output"
[[ -f "$nested_remove_home/skills/visual-design-review/SKILL.md" ]] ||
  fail 'nested remove moved the existing installation'
[[ ! -e "$nested_remove_home/skill-backups" ]] ||
  fail 'nested remove created a backup inside source'

# Parent links must not redirect install/remove into the source or backups elsewhere.
link_home="$sandbox/link-home"
mkdir -p "$link_home"
for linked in skills skill-backups skill-backups/visual-design-planning skill-backups/visual-design-drafting skill-backups/visual-design-review; do
  mkdir -p "$(dirname "$link_home/$linked")"
  ln -s "$root" "$link_home/$linked"
  for action in install remove; do
    if CODEX_HOME="$link_home" bash "$installer" "$action" >/dev/null 2>&1; then
      fail "linked root accepted: $linked ($action)"
    fi
  done
  for name in "${SKILLS[@]}"; do
    [[ -f "$root/$name/SKILL.md" ]] || fail 'linked remove moved source'
  done
  rm "$link_home/$linked"
done
mkdir -p "$link_home/skills"
ln -s "$sandbox/not-installed" "$link_home/skills/visual-design-review"
if CODEX_HOME="$link_home" bash "$installer" install >/dev/null 2>&1; then fail 'symlink install target accepted'; fi
[[ -L "$link_home/skills/visual-design-review" ]] || fail 'symlink was changed'
bash "$root/tests/smoke-install-paths.sh"
echo 'PASS: dry-run, custom home, install, hash check, idempotence, backup, remove, symlink refusal, frontmatter, source-less remove, nested source'
