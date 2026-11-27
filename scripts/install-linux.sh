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
SKILLS=(visual-design-planning visual-design-drafting visual-design-review)
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
repo_root="$(cd -- "$script_dir/.." && pwd -P)"
codex_home="${CODEX_HOME:-${HOME:?}/.codex}"
[[ "$codex_home" == /* ]] || { echo 'CODEX_HOME must be an absolute Unix path.' >&2; exit 2; }
skills_dir="$codex_home/skills"

check_layout() {
  local name="$1" root="$2" path links skill_text frontmatter first_line required
  [[ -f "$root/SKILL.md" ]] || { echo "Missing SKILL.md in $root" >&2; return 1; }
  skill_text="$(tr -d '\r' < "$root/SKILL.md")" || return 1
  IFS= read -r first_line <<< "$skill_text" || return 1
  [[ "$first_line" == '---' ]] || return 1
  # Avoid early-reader SIGPIPE (BSD/macOS) with pipefail enabled.
  frontmatter="$(awk 'NR == 1 && $0 == "---" { inside=1; next } inside && $0 == "---" { found=1; inside=0; next } inside { print } END { exit !found }' <<< "$skill_text")" || return 1
  [[ -n "$frontmatter" ]] || return 1
  grep -qx "name: $name" <<< "$frontmatter" || return 1
  grep -Eq '^description:' <<< "$frontmatter" || return 1
  grep -qx 'metadata:' <<< "$frontmatter" || return 1
  awk '
    /^[^[:space:]]/ { metadata = ($0 == "metadata:") }
    metadata && /^  version: "[^"]+"$/ { found=1 }
    END { exit !found }
  ' <<< "$frontmatter" || return 1
  [[ ! -L "$root" ]] || { echo "Refusing symlink: $root" >&2; return 1; }
  links="$(find "$root" -type l -print -quit)" || return 1
  [[ -z "$links" ]] || { echo "Refusing symlinks inside $root" >&2; return 1; }
  case "$name" in
    visual-design-planning)
      required=('references/workflow/level-1.md' 'references/methods/01.methods-index.md') ;;
    visual-design-drafting)
      required=('references/workflow/level-2.md') ;;
    visual-design-review)
      required=('references/knowledge-routing.md' 'references/review-protocol.md') ;;
    *) echo "Unknown skill: $name" >&2; return 1 ;;
  esac
  for path in "${required[@]}"; do
    [[ -f "$root/$path" ]] || return 1
  done
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
  local name="$1" rel left_files right_files left_hash right_hash
  [[ -d "$3" && ! -L "$3" ]] || return 1
  check_layout "$name" "$3" || return 1
  left_files="$(file_list "$2")" || return 1
  right_files="$(file_list "$3")" || return 1
  [[ -n "$left_files" && "$left_files" == "$right_files" ]] || return 1
  while IFS= read -r rel; do
    left_hash="$(hash_file "$2/$rel")" || return 1
    right_hash="$(hash_file "$3/$rel")" || return 1
    [[ "${left_hash%% *}" == "${right_hash%% *}" ]] || return 1
  done <<< "$left_files"
}
backup_name() {
  printf '%s/%s.%s.%s' "$1" "$(date -u +%Y%m%dT%H%M%SZ)" "$$" "$RANDOM"
}

# Resolve the existing ancestor even when the final home has not been created.
# Falling back to the original path string would hide links into the source.
resolve_future_directory() {
  local probe="$1" suffix='' component parent physical
  while [[ "$probe" != / && "$probe" == */ ]]; do probe="${probe%/}"; done
  while [[ ! -d "$probe" ]]; do
    [[ ! -e "$probe" && ! -L "$probe" ]] || return 1
    component="${probe##*/}"
    # Do not preserve unresolved dot segments: mkdir could enter the source
    # through a missing directory before .. changes the final destination.
    case "$component" in .|..) return 1 ;; esac
    parent="${probe%/*}"
    [[ -n "$parent" ]] || parent=/
    [[ "$parent" != "$probe" ]] || return 1
    suffix="/$component$suffix"
    probe="$parent"
  done
  physical="$(cd -- "$probe" && pwd -P)" || return 1
  if [[ -n "$suffix" ]]; then printf '%s%s\n' "${physical%/}" "$suffix"
  else printf '%s\n' "$physical"; fi
}

source_dir_for() {
  local candidate="$repo_root/$1"
  [[ -d "$candidate" ]] || return 1
  (cd -- "$candidate" && pwd -P)
}

# Managed roots must not redirect moves into another tree.
for managed_root in "$skills_dir" "$codex_home/skill-backups"; do
  if [[ -L "$managed_root" ]]; then
    echo "Refusing linked install or backup directory: $managed_root" >&2
    exit 2
  fi
done
for name in "${SKILLS[@]}"; do
  name_backups="$codex_home/skill-backups/$name"
  if [[ -L "$name_backups" ]]; then
    echo "Refusing linked install or backup directory: $name_backups" >&2
    exit 2
  fi
done

codex_home_real="$(resolve_future_directory "$codex_home")" || {
  echo 'Cannot resolve CODEX_HOME or its existing ancestor.' >&2; exit 2;
}

if [[ "$action" != remove ]]; then
  if [[ -d "$skills_dir" ]]; then
    skills_real="$(cd -- "$skills_dir" && pwd -P)" || { echo 'Cannot resolve skills directory.' >&2; exit 2; }
  else
    skills_real=''
  fi
  for name in "${SKILLS[@]}"; do
    source_dir="$(source_dir_for "$name")" || { echo "Source package is missing: $name" >&2; exit 1; }
    if [[ "$codex_home_real" == "$source_dir" || "$codex_home_real" == "$source_dir"/* ]]; then
      echo 'CODEX_HOME must not be inside the source directory.' >&2
      exit 2
    fi
    if [[ -n "$skills_real" ]]; then
      if [[ "$skills_real" == "$source_dir" || "$skills_real" == "$source_dir"/* ]]; then
        echo 'Skills directory must not be inside the source directory.' >&2
        exit 2
      fi
    fi
    check_layout "$name" "$source_dir" || { echo "Source package structure is invalid: $name" >&2; exit 1; }
    echo "Source: $source_dir"
  done
else
  # Remove normally works without the source package, but it must still
  # reject a home that resolves inside any source tree before moving files.
  for name in "${SKILLS[@]}"; do
    if source_dir="$(source_dir_for "$name")"; then
      if [[ "$codex_home_real" == "$source_dir" || "$codex_home_real" == "$source_dir"/* ]]; then
        echo 'CODEX_HOME must not be inside the source directory.' >&2
        exit 2
      fi
    fi
  done
fi

process_skill() {
  local name="$1"
  local source_dir=''
  local target="$skills_dir/$name"
  local backups_dir="$codex_home/skill-backups/$name"
  local backup
  # Global so the EXIT trap can remove a staging directory left by a failure.
  stage=''
  echo "Target: $target"
  if [[ "$action" != remove ]]; then
    source_dir="$(source_dir_for "$name")" || { echo 'Source package is missing.' >&2; return 1; }
  fi
  if [[ -L "$target" ]]; then echo 'Refusing symlink at install target.' >&2; return 1; fi
  case "$action" in
    check)
      if same_tree "$name" "$source_dir" "$target"; then echo "[$name] OK: installed files, SHA-256, frontmatter and links match."
      else echo "[$name] NOT SYNCED: missing or different installation." >&2; return 1; fi
      ;;
    remove)
      if [[ ! -e "$target" ]]; then echo "[$name] Already absent; nothing changed."; return 0; fi
      backup="$(backup_name "$backups_dir")"
      if $dry_run; then echo "[$name] DRY RUN: would move installed skill to $backup"; return 0; fi
      mkdir -p -- "$backups_dir"
      mv -- "$target" "$backup"
      echo "[$name] Removed from active skills; preserved at $backup"
      ;;
    install)
      if same_tree "$name" "$source_dir" "$target"; then echo "[$name] Already up to date; nothing changed."; return 0; fi
      if [[ -e "$target" && ! -d "$target" ]]; then echo 'Target is not a directory; refusing to replace.' >&2; return 1; fi
      if $dry_run; then
        if [[ -e "$target" ]]; then echo "[$name] DRY RUN: would back up existing folder and install source."
        else echo "[$name] DRY RUN: would install source in an empty target."; fi
        return 0
      fi
      mkdir -p -- "$skills_dir"
      stage="$(mktemp -d "$skills_dir/.$name.stage.XXXXXXXX")"
      trap 'if [[ -n "${stage:-}" && -d "$stage" ]]; then rm -rf -- "$stage"; fi' EXIT
      cp -a -- "$source_dir/." "$stage/"
      same_tree "$name" "$source_dir" "$stage" || { echo 'Staging verification failed.' >&2; return 1; }
      backup=''
      if [[ -e "$target" ]]; then
        backup="$(backup_name "$backups_dir")"
        mkdir -p -- "$backups_dir"
        mv -- "$target" "$backup"
      fi
      if mv -- "$stage" "$target"; then
        stage=''
        echo "[$name] Installed and SHA-256-verified."
        [[ -z "$backup" ]] || echo "[$name] Previous installation preserved at $backup"
      else
        echo 'Activation failed. Attempting rollback.' >&2
        if [[ -n "$backup" && -d "$backup" ]]; then
          # A failed cross-device mv can leave a partial target; clear it before restoring.
          if [[ -e "$target" ]]; then rm -rf -- "$target"; fi
          mv -- "$backup" "$target" || { echo "Rollback failed; previous installation is at $backup" >&2; return 1; }
        fi
        return 1
      fi
      ;;
  esac
}

for name in "${SKILLS[@]}"; do
  process_skill "$name"
done
