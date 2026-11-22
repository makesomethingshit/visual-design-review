#!/usr/bin/env python3
"""Static authoring contract checks for the level 2 drafting skill.

These read the canonical drafting documents and recompute the documented
arithmetic. They do not run a model, render a draft, or judge visual quality.
"""
from __future__ import annotations

import re
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DRAFTING = ROOT / "visual-design-drafting"
WORKFLOW = DRAFTING / "references/workflow/level-2.md"
TRANSLATION = DRAFTING / "references/form-translation.md"
INTAKE = DRAFTING / "references/contracts/draft-intake.md"
EVIDENCE = DRAFTING / "references/contracts/evidence-map.md"
HANDOFF = DRAFTING / "references/contracts/draft-handoff.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def check(condition: bool, reason: str) -> None:
    if not condition:
        raise AssertionError(reason)


def cells(line: str) -> list[str]:
    return [value.strip() for value in line.strip().strip("|").split("|")]


def check_files_and_links() -> None:
    for path in (DRAFTING / "SKILL.md", WORKFLOW, TRANSLATION,
                 INTAKE, EVIDENCE, HANDOFF):
        check(path.is_file(), f"missing drafting document {path.name}")
    skill = read(DRAFTING / "SKILL.md")
    check("name: visual-design-drafting" in skill, "skill frontmatter name changed")
    for relative in ("references/workflow/level-2.md",
                     "references/form-translation.md",
                     "references/contracts/draft-intake.md",
                     "references/contracts/evidence-map.md",
                     "references/contracts/draft-handoff.md"):
        check(f"({relative})" in skill, f"drafting SKILL.md does not open {relative}")

    # Relative links inside the drafting tree must resolve from their own file.
    pattern = re.compile(r"\[[^\]]+\]\(([^)\s]+)(?:\s+[^)]+)?\)")
    for doc in (WORKFLOW, TRANSLATION, INTAKE, EVIDENCE, HANDOFF):
        for raw in pattern.findall(read(doc)):
            target = raw.split("#", 1)[0].split("?", 1)[0]
            if not target or re.match(r"^[a-z]+:", target, flags=re.I):
                continue
            check((doc.parent / target).is_file(),
                  f"broken drafting link {doc.name} -> {raw}")


def check_workflow_contract() -> None:
    text = read(WORKFLOW)
    for step in ("## 1. 인계 자산 로드", "## 2. 조형 번역",
                 "## 3. 복수 시안 생성", "## 4. 선택·확정 및 인계"):
        check(step in text, f"level 2 workflow missing step heading: {step}")
    for artifact in ("10-intake.md", "20-translation.md", "30-evidence-map.md",
                     "40-selection.md", "handoff-v1.md", "drafts/final/",
                     "drafts/INDEX.md"):
        check(artifact in text, f"level 2 workflow does not name {artifact}")
    for status in ("READY", "PARTIAL", "DIRECT", "BLOCKED"):
        check(status in text, f"intake verdict {status} not defined in workflow")
    for relation in ("FOLLOWS", "DEVIATES", "NEW", "CONFLICT"):
        check(relation in text, f"evidence relation {relation} missing from workflow")
    for reached in ("contracts/draft-intake.md", "form-translation.md",
                    "contracts/evidence-map.md", "contracts/draft-handoff.md"):
        check(reached in text, f"workflow does not reach {reached}")
    for boundary in ("레벨 1의 자료 조사", "비평·심각도 판정", "design-handoff"):
        check(boundary in text, f"level 2 boundary missing: {boundary}")
    check("opt-in" in text and "활성화를 선언하지 않는다" in text,
          "workflow must keep the preset activation guard explicit")
    check("review-v1.md" in text, "workflow must open the named level 1 review file")


def check_contract_documents() -> None:
    intake = read(INTAKE)
    for field in ("handoff_status", "adopted", "constraints", "evidence",
                  "unresolved", "gaps", "assumptions", "checks"):
        check(field in intake, f"intake contract missing field {field}")
    for verdict in ("`OK`", "`ASKED`", "`ASSUMED`", "`CONFLICT`"):
        check(verdict in intake, f"intake check result {verdict} missing")
    check("direct" in intake.lower() and "DIRECT" in intake,
          "intake contract must define the direct-brief route")
    check("합성" in intake, "intake example must be marked synthetic")

    evidence = read(EVIDENCE)
    for relation in ("`FOLLOWS`", "`DEVIATES`", "`NEW`", "`CONFLICT`"):
        check(relation in evidence, f"evidence contract missing relation {relation}")
    for status in ("DETERMINED", "PROJECT_INITIAL_PRESET", "CANDIDATE",
                   "UNRESOLVED", "FORMULA_CHECKED", "OUTPUT_INSPECTED", "UNVERIFIED"):
        check(status in evidence, f"evidence contract missing status {status}")
    check("NO-EVIDENCE" in evidence and "ALIAS" in evidence,
          "evidence contract must separate missing and alias evidence refs")
    check("양방향" in evidence, "evidence contract must keep the bidirectional check")
    check("점수" in evidence, "evidence contract must refuse score-based ranking")

    handoff = read(HANDOFF)
    for field in ("Brief & constraints", "Design values", "Provenance",
                  "Decision status", "Verification status", "Unresolved",
                  "Verification request"):
        check(field in handoff, f"handoff contract missing design-handoff field {field}")
    check("design-handoff" in handoff, "handoff contract must name its source contract")
    check("draft-a-v2" in handoff and "handoff-v2.md" in handoff,
          "handoff contract must keep versioned drafts and handoff")
    check("합성" in handoff, "handoff example must be marked synthetic")


def check_translation_math() -> None:
    text = read(TRANSLATION)
    grid_rows: dict[str, Decimal] = {}
    for line in text.splitlines():
        if not line.startswith("| DG-"):
            continue
        code, page, margin, gutter, columns, width = cells(line)
        check(code not in grid_rows, f"duplicate grid example {code}")
        page, margin = Decimal(page), Decimal(margin)
        gutter, columns = Decimal(gutter), Decimal(columns)
        computed = (page - margin * 2 - gutter * (columns - 1)) / columns
        check(computed == Decimal(width),
              f"documented column width wrong for {code}: {computed}")
        grid_rows[code] = computed
    check(grid_rows == {"DG-1": Decimal(38)},
          f"missing or changed grid examples: {grid_rows}")

    leading_rows: dict[str, Decimal] = {}
    for line in text.splitlines():
        if not line.startswith("| DL-"):
            continue
        code, size, ratio, baseline = cells(line)
        check(code not in leading_rows, f"duplicate leading example {code}")
        computed = Decimal(size) * Decimal(ratio)
        check(computed == Decimal(baseline),
              f"documented baseline wrong for {code}: {computed}")
        leading_rows[code] = computed
    check(leading_rows == {"DL-1": Decimal(17)},
          f"missing or changed leading examples: {leading_rows}")

    for guard in ("opt-in", "활성 프로파일", "UNRESOLVED", "UNVERIFIED", "합성"):
        check(guard in text, f"translation guide missing guard {guard}")


def check_example_consistency() -> None:
    # The same synthetic item must carry the same value in translation, mapping
    # table and handoff spec; otherwise the documents contradict each other.
    translation = read(TRANSLATION)
    grid = re.search(r"\| DG-1 \|(?:[^|\n]*\|){4}\s*(\d+)\s*\|", translation)
    leading = re.search(r"\| DL-1 \|(?:[^|\n]*\|){2}\s*(\d+)\s*\|", translation)
    check(grid is not None and leading is not None,
          "translation examples DG-1/DL-1 not parseable")
    column_width, baseline = grid.group(1), leading.group(1)

    mapping = read(EVIDENCE)
    row = next((line for line in mapping.splitlines()
                if line.startswith("| E-GRID-01 |")), None)
    check(row is not None, "evidence map example row E-GRID-01 missing")
    value = cells(row)[3]
    check(value.split()[0] == column_width,
          f"evidence map column width {value} differs from DG-1 {column_width}")

    handoff = read(HANDOFF)
    for identifier, expected in (("G-COL-1", column_width), ("T-BODY-1", baseline)):
        match = re.search(r"id: " + identifier + r"[^\n]*value: (\d+)", handoff)
        check(match is not None, f"handoff example value {identifier} missing")
        check(match.group(1) == expected,
              f"handoff example {identifier}={match.group(1)} differs from {expected}")
    check("T-LEADING" in handoff, "handoff example must name its leading rule")


if __name__ == "__main__":
    check_files_and_links()
    check_workflow_contract()
    check_contract_documents()
    check_translation_math()
    check_example_consistency()
    print("PASS: level 2 intake, translation, evidence mapping and handoff contracts")
