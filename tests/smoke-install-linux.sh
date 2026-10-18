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
ln -s "$sandbox/not-installed" "$target"
if bash "$installer" install >/dev/null 2>&1; then fail 'symlink install target accepted'; fi
[[ -L "$target" ]] || fail 'symlink was changed'
echo 'PASS: dry-run, custom home, install, hash check, idempotence, backup, remove, symlink refusal'
