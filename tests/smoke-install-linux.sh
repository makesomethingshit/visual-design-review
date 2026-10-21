#!/usr/bin/env bash
# Offline filesystem test; does not touch the user's real CODEX_HOME.
set -euo pipefail
root="$(cd -- "$(dirname -- "$0")/.." && pwd -P)"
sandbox="$(mktemp -d)"
trap 'rm -rf -- "$sandbox"' EXIT
export CODEX_HOME="$sandbox/custom-codex-home"
installer="$root/scripts/install-linux.sh"
target="$CODEX_HOME/skills/visual-design-review"
backups_dir="$CODEX_HOME/skill-backups/visual-design-review"
fail() { echo "FAIL: $*" >&2; exit 1; }

bash "$installer" install --dry-run >/dev/null
[[ ! -e "$CODEX_HOME" ]] || fail 'dry-run modified filesystem'
bash "$installer" install >/dev/null
bash "$installer" check >/dev/null
[[ -f "$target/SKILL.md" ]] || fail 'skill missing'
[[ ! -e "$backups_dir" ]] || fail 'fresh install created backup'
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
[[ "$(find "$CODEX_HOME/skills" -name SKILL.md | wc -l)" -eq 1 ]] || fail 'duplicate skill after update'

bash "$installer" remove --dry-run >/dev/null
[[ -d "$target" ]] || fail 'remove dry-run removed files'
bash "$installer" remove >/dev/null
[[ ! -e "$target" ]] || fail 'active skill remains after remove'
[[ "$(find "$backups_dir" -mindepth 1 -maxdepth 1 -type d | wc -l)" -eq 2 ]] || fail 'removal did not preserve installation'
[[ "$(find "$CODEX_HOME/skills" -name SKILL.md | wc -l)" -eq 0 ]] || fail 'backup still discoverable after remove'
restored="$(find "$backups_dir" -mindepth 1 -maxdepth 1 -type d ! -path "$backup" | head -n 1)"
mv -- "$restored" "$target"
bash "$installer" check >/dev/null
[[ "$(find "$CODEX_HOME/skills" -name SKILL.md | wc -l)" -eq 1 ]] || fail 'restored skill not uniquely discoverable'
bash "$installer" remove >/dev/null
if bash "$installer" check >/dev/null 2>&1; then fail 'check passed without installation'; fi
if CODEX_HOME='relative/path' bash "$installer" install --dry-run >/dev/null 2>&1; then fail 'relative CODEX_HOME accepted'; fi
bash "$installer" install >/dev/null
printf '\ncorrupted\n' >> "$target/SKILL.md"
mkdir "$sandbox/bin"
real_find="$(command -v find)"
printf '#!/usr/bin/env bash\nfor arg in "$@"; do [[ "$arg" != f ]] || exit 1; done\nexec %q "$@"\n' "$real_find" > "$sandbox/bin/find"
chmod +x "$sandbox/bin/find"
if PATH="$sandbox/bin:$PATH" bash "$installer" check >/dev/null 2>&1; then fail 'listing failure reported synced'; fi
if PATH="$sandbox/bin:$PATH" bash "$installer" install >/dev/null 2>&1; then fail 'listing failure allowed activation'; fi
[[ "$(tail -n 1 "$target/SKILL.md")" == corrupted ]] || fail 'listing failure changed target'
rm "$sandbox/bin/find"
printf '#!/usr/bin/env bash\nexit 1\n' > "$sandbox/bin/sha256sum"
chmod +x "$sandbox/bin/sha256sum"
if PATH="$sandbox/bin:$PATH" bash "$installer" check >/dev/null 2>&1; then fail 'hash failure reported synced'; fi
bash "$installer" remove >/dev/null

# F-01: fields outside the first frontmatter block must be rejected.
fake_repo="$sandbox/fake-repo"
mkdir -p "$fake_repo/scripts"
cp "$root/scripts/install-linux.sh" "$fake_repo/scripts/"
cp -a "$root/visual-design-review" "$fake_repo/"

# Regression: long but valid SKILL.md must not fail validation under pipefail.
# On macOS, printf | head (or early-exiting awk) can fail with SIGPIPE.
awk 'BEGIN {
  for (i = 0; i < 4096; i++) {
    print "long-skill-body-padding-to-detect-premature-consumer-close-on-BSD"
  }
}' >> "$fake_repo/visual-design-review/SKILL.md"
large_home="$sandbox/large-skill-home"
CODEX_HOME="$large_home" bash "$fake_repo/scripts/install-linux.sh" install --dry-run >/dev/null ||
  fail 'large valid SKILL.md failed validation (possible SIGPIPE)'
[[ ! -e "$large_home" ]] || fail 'large-skill dry-run modified filesystem'

awk '
  $0 == "name: visual-design-review" { next }
  { print }
  !closed && NR > 1 && $0 == "---" { print "name: visual-design-review"; closed=1 }
' "$root/visual-design-review/SKILL.md" > "$fake_repo/visual-design-review/SKILL.md"
if output="$(CODEX_HOME="$sandbox/bad-frontmatter-home" bash "$fake_repo/scripts/install-linux.sh" install --dry-run 2>&1)"; then
  fail 'frontmatter fields outside block accepted'
fi
[[ "$output" == *'Source package structure is invalid.'* ]] || fail 'wrong frontmatter failure'
[[ ! -e "$sandbox/bad-frontmatter-home" ]] || fail 'invalid frontmatter dry-run created files'

# A version belonging to another mapping is not metadata.version.
awk '{ print; if ($0 == "metadata:") print "other:" }' "$root/visual-design-review/SKILL.md" > "$fake_repo/visual-design-review/SKILL.md"
if CODEX_HOME="$sandbox/bad-frontmatter-home" bash "$fake_repo/scripts/install-linux.sh" install --dry-run >/dev/null 2>&1; then
  fail 'version outside metadata accepted'
fi
[[ ! -e "$sandbox/bad-frontmatter-home" ]] || fail 'invalid metadata created files'

# F-02: remove must not depend on a valid source package.
rm -rf "$fake_repo/visual-design-review"
remove_home="$sandbox/remove-home"
CODEX_HOME="$remove_home" bash "$root/scripts/install-linux.sh" install >/dev/null
CODEX_HOME="$remove_home" bash "$fake_repo/scripts/install-linux.sh" remove >/dev/null
[[ ! -e "$remove_home/skills/visual-design-review" ]] || fail 'remove failed without source'
[[ -d "$remove_home/skill-backups/visual-design-review" ]] || fail 'remove without source lost backup'


# CODEX_HOME nested under the source tree must be rejected before creation.
nested_home="$root/visual-design-review/.nested-codex-home"
if CODEX_HOME="$nested_home" bash "$root/scripts/install-linux.sh" install --dry-run >/dev/null 2>&1; then
  fail 'CODEX_HOME inside source accepted'
fi
[[ ! -e "$nested_home" ]] || fail 'nested CODEX_HOME was created'
# Parent links must not redirect install/remove into the source or backups elsewhere.
link_home="$sandbox/link-home"
mkdir -p "$link_home"
for linked in skills skill-backups skill-backups/visual-design-review; do
  mkdir -p "$(dirname "$link_home/$linked")"
  ln -s "$root" "$link_home/$linked"
  for action in install remove; do
    if CODEX_HOME="$link_home" bash "$installer" "$action" >/dev/null 2>&1; then
      fail "linked root accepted: $linked ($action)"
    fi
  done
  [[ -f "$root/visual-design-review/SKILL.md" ]] || fail 'linked remove moved source'
  rm "$link_home/$linked"
done
ln -s "$sandbox/not-installed" "$target"
if bash "$installer" install >/dev/null 2>&1; then fail 'symlink install target accepted'; fi
[[ -L "$target" ]] || fail 'symlink was changed'
echo 'PASS: dry-run, custom home, install, hash check, idempotence, backup, remove, symlink refusal, frontmatter, source-less remove, nested source'
