#!/usr/bin/env python3
"""Build or check the Codex plugin mirror of the canonical visual-design skills."""
import argparse
import json
from pathlib import Path
import re
import shutil
import stat
import sys

PARTS = ("references", "scripts", "assets")
PLUGIN = "visual-design"
SKILLS = ("visual-design-planning", "visual-design-drafting",
          "visual-design-review")
MARKETPLACE = "makesomethingshit-design"


def is_linked(path):
    try:
        info = path.lstat()
    except FileNotFoundError:
        return False
    return stat.S_ISLNK(info.st_mode) or bool(
        getattr(info, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT)


def reject_linked_path(root, target, label):
    """Do not read or replace a path reached through a linked component."""
    current = root
    for part in target.relative_to(root).parts:
        current = current / part
        if is_linked(current):
            raise ValueError("linked " + label + " path component: "
                             + str(current.relative_to(root)))


def reject_linked_tree(root, target, label):
    reject_linked_path(root, target, label)
    if target.is_dir():
        for path in target.rglob("*"):
            reject_linked_path(root, path, label)


def inventory(root, skill):
    source = root / skill
    reject_linked_path(root, source, "canonical")
    reject_linked_path(root, source / "SKILL.md", "canonical")
    if not (source / "SKILL.md").is_file():
        raise ValueError("canonical SKILL.md missing or symlinked: " + skill)
    paths = [Path("SKILL.md")]
    for part in PARTS:
        directory = source / part
        reject_linked_path(root, directory, "canonical")
        if directory.exists():
            if not directory.is_dir():
                raise ValueError("source component is not a directory: "
                                 + skill + "/" + part)
            for path in sorted(directory.rglob("*")):
                if "__pycache__" in path.relative_to(source).parts:
                    continue
                reject_linked_path(root, path, "canonical")
                if path.is_file():
                    paths.append(path.relative_to(source))
    for rel in paths:
        reject_linked_path(root, source / rel, "canonical")
    return paths


def validate_manifests(root, skills_root):
    errors = []
    manifest_path = root / "plugins" / PLUGIN / ".codex-plugin" / "plugin.json"
    marketplace_path = root / ".agents" / "plugins" / "marketplace.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if (manifest.get("name") != PLUGIN or manifest.get("skills") != "./skills/"
                or not manifest.get("version")):
            errors.append("plugin name/version/skills manifest mismatch")
        entry_root = (manifest_path.parent.parent / manifest.get("skills", "")).resolve()
        if entry_root != skills_root.resolve():
            errors.append("plugin skills path escapes or differs from packaged skills/")
    except (OSError, ValueError, TypeError) as exc:
        errors.append("invalid plugin manifest: " + str(exc))
    try:
        catalog = json.loads(marketplace_path.read_text(encoding="utf-8"))
        entries = [p for p in catalog.get("plugins", []) if p.get("name") == PLUGIN]
        if catalog.get("name") != MARKETPLACE or len(entries) != 1:
            errors.append("marketplace identifier or plugin entry mismatch")
        elif (entries[0].get("source") != {"source": "local",
                                           "path": "./plugins/" + PLUGIN}
              or entries[0].get("policy", {}).get("installation") != "AVAILABLE"):
            errors.append("marketplace path or installation policy mismatch")
    except (OSError, ValueError, TypeError) as exc:
        errors.append("invalid marketplace: " + str(exc))
    return errors


def validate_skill(root, target, skill, paths):
    errors = []
    try:
        reject_linked_tree(root, target, "package")
        actual = set()
        if target.is_dir():
            for path in target.rglob("*"):
                if path.is_file():
                    actual.add(path.relative_to(target))
    except (OSError, ValueError) as exc:
        errors.append(str(exc))
        return errors
    expected = set(paths)
    for rel in sorted(expected - actual):
        errors.append("missing packaged file: " + skill + "/" + str(rel))
    for rel in sorted(actual - expected):
        errors.append("unexpected packaged file: " + skill + "/" + str(rel))
    for rel in sorted(expected & actual):
        if (target / rel).is_symlink():
            errors.append("symlinked packaged file: " + skill + "/" + str(rel))
        elif (root / skill / rel).read_bytes() != (target / rel).read_bytes():
            errors.append("source/package content differs: " + skill + "/" + str(rel))
    try:
        skill_file = (target / "SKILL.md").read_text(encoding="utf-8")
        if not re.search(r"(?m)^name:\s*" + re.escape(skill) + r"\s*$", skill_file):
            errors.append("skill frontmatter name missing: " + skill)
        for ref in re.findall(r"\]\((references/[^)\s#]+)", skill_file):
            if not (target / ref).is_file():
                errors.append("missing referenced skill file: " + skill + "/" + ref)
    except OSError as exc:
        errors.append("packaged SKILL.md unreadable: " + skill + ": " + str(exc))
    return errors


def validate(root, skills_root, inventories):
    errors = validate_manifests(root, skills_root)
    try:
        if skills_root.is_dir():
            packaged = sorted(path.name for path in skills_root.iterdir())
            if packaged != sorted(SKILLS):
                errors.append("packaged skills/ entries differ from expected: "
                              + repr(packaged))
    except OSError as exc:
        errors.append("unreadable packaged skills directory: " + str(exc))
    for skill in SKILLS:
        errors.extend(validate_skill(root, skills_root / skill, skill,
                                     inventories[skill]))
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true", help="regenerate generated skills")
    mode.add_argument("--check", action="store_true", help="verify unchanged package (default)")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1],
                        help="repository root (also used for isolated fixture tests)")
    args = parser.parse_args()
    root = args.root.resolve()
    skills_root = root / "plugins" / PLUGIN / "skills"
    inventories = {}
    errors = []
    try:
        reject_linked_tree(root, skills_root, "package")
        for skill in SKILLS:
            inventories[skill] = inventory(root, skill)
        if args.write:
            for skill in SKILLS:
                target = skills_root / skill
                if target.exists():
                    # shortcut: concurrent path changes are unprotected; use directory handles if needed.
                    shutil.rmtree(target)
                for rel in inventories[skill]:
                    dest = target / rel
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(root / skill / rel, dest)
        errors = validate(root, skills_root, inventories)
    except (OSError, ValueError) as exc:
        errors = [str(exc)]
    if errors:
        for issue in errors:
            print("FAIL:", issue, file=sys.stderr)
        print("Run: python3 scripts/sync-codex-plugin.py --write", file=sys.stderr)
        return 1
    total = sum(len(paths) for paths in inventories.values())
    print("PASS: plugin manifest, marketplace and", total,
          "canonical skill files of", ", ".join(SKILLS), "are in sync")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
