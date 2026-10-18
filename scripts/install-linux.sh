#!/usr/bin/env bash
# Linux/WSL only. No network access, no package installation.
set -euo pipefail

usage() {
  echo 'Usage: bash scripts/install-linux.sh [install|check|remove] [--dry-run]' >&2
}
action=install
dry_run=false
for arg in "$@"; do
  case "$arg" in
    install|check|remove) action="$arg" ;;
    --dry-run) dry_run=true ;;
    -h|--help) usage; exit 0 ;;
    *) usage; exit 2 ;;
  esac
done
[[ "$(uname -s)" == Linux ]] || { echo 'Use install-windows.ps1 on native Windows.' >&2; exit 2; }
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
source_dir="$(cd -- "$script_dir/../visual-design-review" && pwd -P)"
codex_home="${CODEX_HOME:-${HOME:?}/.codex}"
[[ "$codex_home" == /* ]] || { echo 'CODEX_HOME must be an absolute Linux path.' >&2; exit 2; }
skills_dir="$codex_home/skills"
target="$skills_dir/visual-design-review"
backups_dir="$codex_home/skill-backups/visual-design-review"

check_layout() {
  local root="$1" path
  [[ -f "$root/SKILL.md" ]] || { echo "Missing SKILL.md in $root" >&2; return 1; }
  [[ "$(head -n 1 "$root/SKILL.md")" == '---' ]] || return 1
  awk 'NR > 1 && $0 == "---" { found=1; exit } END { exit !found }' "$root/SKILL.md" || return 1
  grep -qx 'name: visual-design-review' "$root/SKILL.md" || return 1
  grep -qx 'metadata:' "$root/SKILL.md" || return 1
  grep -Eq '^[[:space:]]+version: "[^"]+"$' "$root/SKILL.md" || return 1
  [[ ! -L "$root" ]] || { echo "Refusing symlink: $root" >&2; return 1; }
  [[ -z "$(find "$root" -type l -print -quit)" ]] || { echo "Refusing symlinks inside $root" >&2; return 1; }
  [[ -f "$root/references/review-protocol.md" && -f "$root/references/critique-rubric.md" ]] || return 1
  while IFS= read -r path; do
    [[ -f "$root/$path" ]] || { echo "Broken reference: $path" >&2; return 1; }
  done < <(grep -oE '\]\(references/[^)#]+\.md\)' "$root/SKILL.md" | sed -E 's/^\]\((.*)\)$/\1/' || true)
}

file_list() {
  (cd -- "$1" && find . -type f -printf '%P\n' | LC_ALL=C sort)
}
same_tree() {
  local rel
  [[ -d "$2" && ! -L "$2" ]] || return 1
  check_layout "$2" || return 1
  diff -q <(file_list "$1") <(file_list "$2") >/dev/null || return 1
  while IFS= read -r rel; do
    [[ "$(sha256sum "$1/$rel" | cut -d' ' -f1)" == "$(sha256sum "$2/$rel" | cut -d' ' -f1)" ]] || return 1
  done < <(file_list "$1")
}
backup_name() {
  printf '%s/%s.%s.%s' "$backups_dir" "$(date -u +%Y%m%dT%H%M%SZ)" "$$" "$RANDOM"
}

check_layout "$source_dir" || { echo 'Source package structure is invalid.' >&2; exit 1; }
echo "Source: $source_dir"
echo "Target: $target"
if [[ -L "$target" ]]; then echo 'Refusing symlink at install target.' >&2; exit 1; fi
case "$action" in
  check)
    if same_tree "$source_dir" "$target"; then echo 'OK: installed files, SHA-256, frontmatter and links match.'
    else echo 'NOT SYNCED: missing or different installation.' >&2; exit 1; fi
    ;;
  remove)
    if [[ ! -e "$target" ]]; then echo 'Already absent; nothing changed.'; exit 0; fi
    backup="$(backup_name)"
    if $dry_run; then echo "DRY RUN: would move installed skill to $backup"; exit 0; fi
    mkdir -p -- "$backups_dir"
    mv -- "$target" "$backup"
    echo "Removed from active skills; preserved at $backup"
    ;;
  install)
    if same_tree "$source_dir" "$target"; then echo 'Already up to date; nothing changed.'; exit 0; fi
    if [[ -e "$target" && ! -d "$target" ]]; then echo 'Target is not a directory; refusing to replace.' >&2; exit 1; fi
    if $dry_run; then
      if [[ -e "$target" ]]; then echo 'DRY RUN: would back up existing folder and install source.'
      else echo 'DRY RUN: would install source in an empty target.'; fi
      exit 0
    fi
    mkdir -p -- "$skills_dir"
    stage="$(mktemp -d "$skills_dir/.visual-design-review.stage.XXXXXXXX")"
    trap 'if [[ -n "${stage:-}" && -d "$stage" ]]; then rm -rf -- "$stage"; fi' EXIT
    cp -a -- "$source_dir/." "$stage/"
    same_tree "$source_dir" "$stage" || { echo 'Staging verification failed.' >&2; exit 1; }
    backup=''
    if [[ -e "$target" ]]; then
      backup="$(backup_name)"
      mkdir -p -- "$backups_dir"
      mv -- "$target" "$backup"
    fi
    if mv -- "$stage" "$target"; then
      stage=''
      echo 'Installed and SHA-256-verified.'
      [[ -z "$backup" ]] || echo "Previous installation preserved at $backup"
    else
      echo 'Activation failed. Attempting rollback.' >&2
      if [[ -n "$backup" && -d "$backup" && ! -e "$target" ]]; then mv -- "$backup" "$target"; fi
      exit 1
    fi
    ;;
esac
