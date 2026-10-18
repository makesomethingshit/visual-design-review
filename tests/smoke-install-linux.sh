#!/usr/bin/env bash
# Offline filesystem test; does not touch the user's real CODEX_HOME.
set -euo pipefail
root="$(cd -- "$(dirname -- "$0")/.." && pwd -P)"
sandbox="$(mktemp -d)"
trap 'rm -rf -- "$sandbox"' EXIT
export CODEX_HOME="$sandbox/custom-codex-home"
installer="$root/scripts/install-linux.sh"
target="$CODEX_HOME/skills/visual-design-review"
fail() { echo "FAIL: $*" >&2; exit 1; }

bash "$installer" install --dry-run >/dev/null
[[ ! -e "$CODEX_HOME" ]] || fail 'dry-run modified filesystem'
bash "$installer" install >/dev/null
bash "$installer" check >/dev/null
[[ -f "$target/SKILL.md" ]] || fail 'skill missing'
[[ "$(find "$CODEX_HOME/skills" -maxdepth 1 -name 'visual-design-review.backup.*' | wc -l)" -eq 0 ]] || fail 'fresh install created backup'
output="$(bash "$installer" install)"
[[ "$output" == *'Already up to date'* ]] || fail 'second install was not idempotent'

printf '\nlocal-change\n' >> "$target/SKILL.md"
bash "$installer" install --dry-run >/dev/null
[[ "$(tail -n 1 "$target/SKILL.md")" == 'local-change' ]] || fail 'update dry-run wrote files'
bash "$installer" install >/dev/null
bash "$installer" check >/dev/null
[[ "$(find "$CODEX_HOME/skills" -maxdepth 1 -type d -name 'visual-design-review.backup.*' | wc -l)" -eq 1 ]] || fail 'missing update backup'
backup="$(find "$CODEX_HOME/skills" -maxdepth 1 -type d -name 'visual-design-review.backup.*' | head -n 1)"
[[ "$(tail -n 1 "$backup/SKILL.md")" == 'local-change' ]] || fail 'old installation not preserved'

bash "$installer" remove --dry-run >/dev/null
[[ -d "$target" ]] || fail 'remove dry-run removed files'
bash "$installer" remove >/dev/null
[[ ! -e "$target" ]] || fail 'active skill remains after remove'
[[ "$(find "$CODEX_HOME/skills" -maxdepth 1 -type d -name 'visual-design-review.backup.*' | wc -l)" -eq 2 ]] || fail 'removal did not preserve installation'
if bash "$installer" check >/dev/null 2>&1; then fail 'check passed without installation'; fi
if CODEX_HOME='relative/path' bash "$installer" install --dry-run >/dev/null 2>&1; then fail 'relative CODEX_HOME accepted'; fi
ln -s "$sandbox/not-installed" "$target"
if bash "$installer" install >/dev/null 2>&1; then fail 'symlink install target accepted'; fi
[[ -L "$target" ]] || fail 'symlink was changed'
echo 'PASS: dry-run, custom home, install, hash check, idempotence, backup, remove, symlink refusal'
