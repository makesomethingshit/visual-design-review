#!/usr/bin/env bash
# Native macOS only; all installations use isolated temporary homes.
set -euo pipefail
[[ "$(uname -s)" == Darwin ]] || { echo 'Run this test on macOS.' >&2; exit 2; }
root="$(cd -- "$(dirname -- "$0")/.." && pwd -P)"
sandbox="$(mktemp -d)"
trap 'rm -rf -- "$sandbox"' EXIT
fail() { echo "FAIL: $*" >&2; exit 1; }

# Exercise the shared install/check/update/backup/remove/restore regressions.
bash "$root/tests/smoke-install-linux.sh"

# Force the shasum fallback using native commands only, even if sha256sum is installed.
native_bin="$sandbox/native-bin"
mkdir "$native_bin"
for name in awk bash cat chmod cp date dirname find grep head ln mkdir mktemp mv rm sed shasum sort tail uname wc; do
  command_path=''
  for dir in /usr/bin /bin /usr/sbin /sbin; do
    if [[ -x "$dir/$name" ]]; then command_path="$dir/$name"; break; fi
  done
  [[ -n "$command_path" ]] || fail "Missing native command: $name"
  ln -s "$command_path" "$native_bin/$name"
done
PATH="$native_bin" /bin/bash "$root/tests/smoke-install-linux.sh"

export CODEX_HOME="$sandbox/한글 경로 with spaces/codex-home"
installer="$root/scripts/install-linux.sh"
target="$CODEX_HOME/skills/visual-design-review"
PATH="$native_bin" /bin/bash "$installer" install --dry-run >/dev/null
[[ ! -e "$CODEX_HOME" ]] || fail 'dry-run created custom home'
PATH="$native_bin" /bin/bash "$installer" install >/dev/null
PATH="$native_bin" /bin/bash "$installer" check >/dev/null
printf '\nrollback-local-edit\n' >> "$target/SKILL.md"
cp "$target/SKILL.md" "$sandbox/expected-skill.md"

# Fail only staging activation; allow backup creation and the rollback move.
mkdir "$sandbox/fault-bin"
cat > "$sandbox/fault-bin/mv" <<'SH'
#!/bin/bash
for arg in "$@"; do
  case "$arg" in
    *.visual-design-review.stage.*) echo 'injected activation failure' >&2; exit 73 ;;
  esac
done
exec /bin/mv "$@"
SH
chmod +x "$sandbox/fault-bin/mv"
if PATH="$sandbox/fault-bin:$native_bin" /bin/bash "$installer" install >"$sandbox/rollback.log" 2>&1; then
  fail 'injected activation failure reported success'
fi
grep -q 'Attempting rollback' "$sandbox/rollback.log" || fail 'rollback branch did not execute'
/usr/bin/cmp "$sandbox/expected-skill.md" "$target/SKILL.md" || fail 'rollback lost local edit'
[[ -z "$(find "$CODEX_HOME/skills" -name '.visual-design-review.stage.*' -print)" ]] || fail 'staging directory remains'
# Both hash tools absent must be a clear dependency failure, not a false "not synced".
rm "$native_bin/shasum"
if PATH="$native_bin" /bin/bash "$installer" check >/dev/null 2>"$sandbox/no-hash.log"; then
  fail 'check passed without a hash tool'
fi
grep -q 'sha256sum or shasum is required' "$sandbox/no-hash.log" || fail 'missing hash tool not reported'
echo 'PASS: macOS native commands, shasum fallback, Unicode/spaces, forced rollback, missing hash tool'
