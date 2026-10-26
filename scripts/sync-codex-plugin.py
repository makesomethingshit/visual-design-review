#!/usr/bin/env python3
"""Build or check the Codex plugin mirror of the canonical visual-design-review skill."""
import argparse
import json
from pathlib import Path
import re
import shutil
import sys

PARTS = ("references", "scripts", "assets")
PLUGIN = "visual-design-review"
MARKETPLACE = "makesomethingshit-design"


def reject_linked_package_path(root, target):
    """Do not read or replace a package reached through a linked parent."""
    current = root
    for part in target.relative_to(root).parts:
        current = current / part
        is_junction = getattr(current, "is_junction", lambda: False)
        if current.is_symlink() or is_junction():
            raise ValueError("linked package path component: " + str(current.relative_to(root)))


def inventory(root):
    source = root / PLUGIN
    if source.is_symlink() or not (source / "SKILL.md").is_file():
        raise ValueError("canonical SKILL.md missing or symlinked")
    paths = [Path("SKILL.md")]
    for part in PARTS:
        directory = source / part
        if directory.is_symlink():
            raise ValueError("symlinked source directory: " + part)
        if directory.exists():
            if not directory.is_dir():
                raise ValueError("source component is not a directory: " + part)
            paths.extend(sorted(p.relative_to(source) for p in directory.rglob("*") if p.is_file()))
    for rel in paths:
        if (source / rel).is_symlink():
            raise ValueError("symlinked source file: " + str(rel))
    return paths


def validate(root, target, paths):
    errors = []
    manifest_path = root / "plugins" / PLUGIN / ".codex-plugin" / "plugin.json"
    marketplace_path = root / ".agents" / "plugins" / "marketplace.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if (manifest.get("name") != PLUGIN or manifest.get("skills") != "./skills/"
                or not manifest.get("version")):
            errors.append("plugin name/version/skills manifest mismatch")
        entry_root = (manifest_path.parent.parent / manifest.get("skills", "")).resolve()
        if entry_root != target.parent.resolve():
            errors.append("plugin skills path escapes or differs from packaged skills/")
    except (OSError, ValueError, TypeError) as exc:
        errors.append("invalid plugin manifest: " + str(exc))
    try:
        catalog = json.loads(marketplace_path.read_text(encoding="utf-8"))
        entries = [p for p in catalog.get("plugins", []) if p.get("name") == PLUGIN]
        if catalog.get("name") != MARKETPLACE or len(entries) != 1:
            errors.append("marketplace identifier or plugin entry mismatch")
        elif (entries[0].get("source") != {"source": "local", "path": "./plugins/visual-design-review"}
              or entries[0].get("policy", {}).get("installation") != "AVAILABLE"):
            errors.append("marketplace path or installation policy mismatch")
    except (OSError, ValueError, TypeError) as exc:
        errors.append("invalid marketplace: " + str(exc))

    if target.is_symlink():
        errors.append("package skill root is a symlink")
    actual = {p.relative_to(target) for p in target.rglob("*") if p.is_file()} if target.is_dir() else set()
    expected = set(paths)
    for rel in sorted(expected - actual):
        errors.append("missing packaged file: " + str(rel))
    for rel in sorted(actual - expected):
        errors.append("unexpected packaged file: " + str(rel))
    for rel in sorted(expected & actual):
        if (target / rel).is_symlink():
            errors.append("symlinked packaged file: " + str(rel))
        elif (root / PLUGIN / rel).read_bytes() != (target / rel).read_bytes():
            errors.append("source/package content differs: " + str(rel))
    try:
        skill = (target / "SKILL.md").read_text(encoding="utf-8")
        if not re.search(r"(?m)^name:\s*visual-design-review\s*$", skill):
            errors.append("skill frontmatter name missing")
        for ref in re.findall(r"\]\((references/[^)\s#]+)", skill):
            if not (target / ref).is_file():
                errors.append("missing referenced skill file: " + ref)
    except OSError as exc:
        errors.append("packaged SKILL.md unreadable: " + str(exc))
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true", help="regenerate generated skill")
    mode.add_argument("--check", action="store_true", help="verify unchanged package (default)")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1],
                        help="repository root (also used for isolated fixture tests)")
    args = parser.parse_args()
    root = args.root.resolve()
    source = root / PLUGIN
    target = root / "plugins" / PLUGIN / "skills" / PLUGIN
    try:
        reject_linked_package_path(root, target)
        paths = inventory(root)
        if args.write:
            if target.is_symlink():
                raise ValueError("will not replace symlinked package")
            if target.exists():
                shutil.rmtree(target)
            for rel in paths:
                dest = target / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source / rel, dest)
        errors = validate(root, target, paths)
    except (OSError, ValueError) as exc:
        errors = [str(exc)]
    if errors:
        for issue in errors:
            print("FAIL:", issue, file=sys.stderr)
        print("Run: python3 scripts/sync-codex-plugin.py --write", file=sys.stderr)
        return 1
    print("PASS: plugin manifest, marketplace and", len(paths),
          "canonical skill files are in sync")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
