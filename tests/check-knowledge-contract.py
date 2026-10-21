#!/usr/bin/env python3
"""Static authoring contract checks. These do NOT validate actual Codex skill routing."""
from __future__ import annotations

import re
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "visual-design-review"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def check(condition: bool, reason: str) -> None:
    if not condition:
        raise AssertionError(reason)


def check_preset_mapping() -> None:
    text = read(PKG / "references/typography-presets.md")
    rows: dict[str, list[str]] = {}
    for line in text.splitlines():
        if line.startswith("| "):
            cells = [v.strip() for v in line.strip().strip("|").split("|")]
            if cells and cells[0] in "ABCDEFGH" and len(cells[0]) == 1:
                check(cells[0] not in rows, f"Duplicate policy {cells[0]}")
                rows[cells[0]] = cells
    check(set(rows) == set("ABCDEFGH"), f"Missing or extra preset rows: {set(rows)}")

    # Check the ID-to-value association, not merely presence of 1.7/1.5/2.0.
    expected_ratios = {"A": Decimal("1.7"), "B": Decimal("1.5"),
                       "C": Decimal("2.0"), "D": Decimal("2.0")}
    for code, expected in expected_ratios.items():
        check(len(rows[code]) == 4, f"Malformed ratio row {code}")
        match = re.search(r"\*\*(\d+(?:\.\d+)?)\*\*", rows[code][2])
        check(match is not None and Decimal(match.group(1)) == expected,
              f"Wrong language leading: {code} should be {expected}")
        pt = re.search(r"(\d+)pt", rows[code][3])
        check(pt is not None and Decimal(pt.group(1)) == Decimal(10) * expected,
              f"Wrong leading example: {code}")

    expected_strings = {"E": "10pt", "F": "30칸",
                        "G": "Tracking 0", "H": "왼끝맞춤"}
    for code, required in expected_strings.items():
        check(len(rows[code]) == 3 and required in rows[code][1],
              f"Wrong print-first preset mapping {code}")
    for guard in ("USER_APPROVED_PROJECT_POLICY", "명시된 사용자",
                  "기존 작품 비평", "세로쓰기", "PROJECT_INITIAL_PRESET"):
        check(guard in text, f"Missing preset condition/guard {guard}")


def check_links() -> None:
    # Verify relative links as GitHub resolves them, relative to each Markdown file.
    docs = [
        ROOT / "README.md",
        ROOT / "docs/skill-architecture-extension.md",
        PKG / "SKILL.md",
        *sorted((PKG / "references").glob("*.md")),
        PKG / "tests/architecture-scenarios.md",
    ]
    pattern = re.compile(r"\[[^\]]+\]\(([^)\s]+)(?:\s+[^)]+)?\)")
    for doc in docs:
        text = read(doc)
        for raw in pattern.findall(text):
            target = raw.split("#", 1)[0].split("?", 1)[0]
            if not target or re.match(r"^(?:[a-z]+:|/)", target, flags=re.I):
                continue
            # Do not allow paths that accidentally resolve to a non-existent docs/ subtree.
            resolved = (doc.parent / target).resolve()
            check(resolved.is_relative_to(ROOT.resolve()),
                  f"Out-of-tree local link {doc.relative_to(ROOT)} -> {raw}")
            check(resolved.is_file(),
                  f"Broken local Markdown link {doc.relative_to(ROOT)} -> {raw}")


def check_review_invocation() -> None:
    skill = read(PKG / "SKILL.md")
    header = skill.split("---", 2)[1]
    for trigger in ("print preflight", "typography critique",
                    "composition analysis", "포스터 피드백", "편집디자인 검토"):
        check(trigger in header, f"Legacy automatic invocation phrase missing: {trigger}")
    for reference in ("review-protocol.md", "critique-rubric.md",
                      "review-output.md", "reference-analysis.md",
                      "typography-presets.md", "design-handoff.md"):
        check(reference in skill, f"Skill link not surfaced: {reference}")
    review_output = read(PKG / "references/review-output.md")
    for contract in ("Quick Review", "Deep / Aggressive Review",
                     "Critical / Major / Minor / Exploratory", "Keep / Fix / Push"):
        check(contract in review_output, f"Missing legacy review contract {contract}")


def check_reference_math() -> None:
    doc = read(PKG / "references/reference-analysis.md")
    for must_have in ("Frame", "Object", "Relation", "Hypothesis",
                      "evidence_status", "UNVERIFIED", "e_x=", "median(",
                      "경쟁 모델", "단일", "재구성"):
        check(must_have in doc, f"Missing inverse-analysis contract {must_have}")
    width = Decimal(1200)
    xs = [Decimal(120), Decimal(420), Decimal(720)]
    check([x / width for x in xs] ==
          [Decimal(".10"), Decimal(".35"), Decimal(".60")],
          "Synthetic normalized x observations mismatch")
    gaps = [b - a for a, b in zip(xs, xs[1:])]
    check(gaps == [Decimal(300), Decimal(300)], "Synthetic pitch mismatch")
    check([abs(Decimal(120) + Decimal(300)*i - x) / width
           for i, x in enumerate(xs)] == [0, 0, 0],
          "Synthetic geometric residual mismatch")


if __name__ == "__main__":
    check_preset_mapping()
    check_links()
    check_review_invocation()
    check_reference_math()
    print("PASS: policy mappings, local docs links, legacy triggers, reference-math examples")
