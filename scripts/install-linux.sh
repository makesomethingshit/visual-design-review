#!/usr/bin/env bash
# Linux/WSL/macOS. No network access, no package installation.
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
case "$(uname -s)" in
  Linux|Darwin) ;;
  *) echo 'Unsupported OS. Use install-windows.ps1 on native Windows; otherwise Linux/WSL/macOS is required.' >&2; exit 2 ;;
esac
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
source_dir="$(cd -- "$script_dir/../visual-design-review" 2>/dev/null && pwd -P || true)"
codex_home="${CODEX_HOME:-${HOME:?}/.codex}"
[[ "$codex_home" == /* ]] || { echo 'CODEX_HOME must be an absolute Unix path.' >&2; exit 2; }
skills_dir="$codex_home/skills"
target="$skills_dir/visual-design-review"
backups_dir="$codex_home/skill-backups/visual-design-review"

check_layout() {
  local root="$1" path links skill_text frontmatter
  [[ -f "$root/SKILL.md" ]] || { echo "Missing SKILL.md in $root" >&2; return 1; }
  skill_text="$(tr -d '\r' < "$root/SKILL.md")" || return 1
  [[ "$(printf '%s\n' "$skill_text" | head -n 1)" == '---' ]] || return 1
  frontmatter="$(printf '%s\n' "$skill_text" | awk 'NR == 1 && $0 == "---" { inside=1; next } inside && $0 == "---" { found=1; exit } inside { print } END { exit !found }')" || return 1
  [[ -n "$frontmatter" ]] || return 1
  printf '%s\n' "$frontmatter" | grep -qx 'name: visual-design-review' || return 1
  printf '%s\n' "$frontmatter" | grep -Eq '^description:' || return 1
  printf '%s\n' "$frontmatter" | grep -qx 'metadata:' || return 1
  printf '%s\n' "$frontmatter" | grep -Eq '^[[:space:]]+version: "[^"]+"$' || return 1
  [[ ! -L "$root" ]] || { echo "Refusing symlink: $root" >&2; return 1; }
  links="$(find "$root" -type l -print -quit)" || return 1
  [[ -z "$links" ]] || { echo "Refusing symlinks inside $root" >&2; return 1; }
  [[ -f "$root/references/review-protocol.md" && -f "$root/references/critique-rubric.md" ]] || return 1
  while IFS= read -r path; do
    [[ -f "$root/$path" ]] || { echo "Broken reference: $path" >&2; return 1; }
  done < <(printf '%s\n' "$skill_text" | grep -oE '\]\(references/[^)#]+\.md\)' | sed -E 's/^\]\((.*)\)$/\1/' || true)
}

hash_file() {
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$1"
  elif command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "$1"
  else
    echo 'sha256sum or shasum is required.' >&2
    return 1
  fi
}
file_list() {
  (cd -- "$1" && find . -type f -print | sed 's|^./||' | LC_ALL=C sort)
}
same_tree() {
  local rel left_files right_files left_hash right_hash
  [[ -d "$2" && ! -L "$2" ]] || return 1
  check_layout "$2" || return 1
  left_files="$(file_list "$1")" || return 1
  right_files="$(file_list "$2")" || return 1
  [[ -n "$left_files" && "$left_files" == "$right_files" ]] || return 1
  while IFS= read -r rel; do
    left_hash="$(hash_file "$1/$rel")" || return 1
    right_hash="$(hash_file "$2/$rel")" || return 1
    [[ "${left_hash%% *}" == "${right_hash%% *}" ]] || return 1
  done <<< "$left_files"
}
backup_name() {
  printf '%s/%s.%s.%s' "$backups_dir" "$(date -u +%Y%m%dT%H%M%SZ)" "$$" "$RANDOM"
}

if [[ "$action" != remove ]]; then
  [[ -n "$source_dir" ]] || { echo 'Source package is missing.' >&2; exit 1; }
  codex_home_real="$(cd -- "$codex_home" 2>/dev/null && pwd -P || printf '%s' "$codex_home")"
  if [[ "$codex_home_real" == "$source_dir" || "$codex_home_real" == "$source_dir"/* ]]; then
    echo 'CODEX_HOME must not be inside the source directory.' >&2
    exit 2
  fi
  if [[ -d "$skills_dir" ]]; then
    skills_real="$(cd -- "$skills_dir" && pwd -P)" || { echo 'Cannot resolve skills directory.' >&2; exit 2; }
    if [[ "$skills_real" == "$source_dir" || "$skills_real" == "$source_dir"/* ]]; then
      echo 'Skills directory must not be inside the source directory.' >&2
      exit 2
    fi
  fi
  check_layout "$source_dir" || { echo 'Source package structure is invalid.' >&2; exit 1; }
  echo "Source: $source_dir"
fi
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
      if [[ -n "$backup" && -d "$backup" ]]; then
        # A failed cross-device mv can leave a partial target; clear it before restoring.
        if [[ -e "$target" ]]; then rm -rf -- "$target"; fi
        mv -- "$backup" "$target" || { echo "Rollback failed; previous installation is at $backup" >&2; exit 1; }
      fi
      exit 1
    fi
    ;;
esac
