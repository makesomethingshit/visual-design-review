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
                      "경쟁 모델", "임의 가중치", "재구성"):
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


def check_print_routing() -> None:
    routing = read(PKG / "references/knowledge-routing.md")
    for guard in ("매체가 디지털 전용으로 확정되고 인쇄 요청·제약이 없는 경우만",
                  "텍스트 없는 인쇄용 로고 PDF", "UNVERIFIED"):
        check(guard in routing, f"Missing print routing guard: {guard}")
    check("심볼만 있으면 인쇄 프리플라이트 생략" not in routing,
          "Symbol-only output must not bypass print checks")
    scenarios = read(PKG / "tests/architecture-scenarios.md")
    for scenario in ("| R-4 |", "| R-23 |", "| R-24 |"):
        check(scenario in scenarios, f"Missing digital/print routing case {scenario}")


def check_typography_widths() -> None:
    doc = read(PKG / "references/typography-relations.md")
    for formula in ("W_raw = Σ(a_raw_i + Δadvance_i) / S × F + T_remaining",
                    "W_shaped = Σa_shaped_i / S × F + T_remaining"):
        check(formula in doc, f"Missing width input contract: {formula}")
    widths: dict[str, Decimal] = {}
    for line in doc.splitlines():
        if not line.startswith("| W-"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        check(len(cells) == 9, f"Malformed width example: {line}")
        code, kind, advances, scale, size, delta, offset, tracking, expected = cells
        check(code not in widths, f"Duplicate width example {code}")
        check(kind in ("raw", "shaped"), f"Unknown width representation: {kind}")
        check(Decimal(scale) > 0 and Decimal(size) > 0, f"Invalid scale/size: {code}")
        check(kind == "raw" or Decimal(delta) == 0,
              f"Shaped advances must not receive kerning again: {code}")
        # Placement is parsed but excluded: it changes ink position, not pen movement.
        Decimal(offset)
        width = ((sum(Decimal(value) for value in advances.split(",")) + Decimal(delta))
                 / Decimal(scale) * Decimal(size) + Decimal(tracking))
        check(width == Decimal(expected), f"Wrong documented width: {code}: {width}")
        widths[code] = width
    check(widths == {"W-1": Decimal(12), "W-2": Decimal("11.5"),
                     "W-3": Decimal("11.5"), "W-4": Decimal(12),
                     "W-5": Decimal(12), "W-6": Decimal(6), "W-7": Decimal(6)},
          f"Missing or changed width acceptance examples: {widths}")
    check(widths["W-6"] + widths["W-7"] == Decimal(12),
          "Mixed-font runs must be scaled separately before summing")




def check_rule_contract() -> None:
    contract = read(PKG / "references/rule-contract.md")
    for required in ("knowledge_kind", "rule_strength", "source_version",
                     "document_status", "scope", "conditions", "exceptions",
                     "verification_method", "PROJECT_POLICY", "UNVERIFIED"):
        check(required in contract, f"Missing rule contract field {required}")
    for path in ("SKILL.md", "references/knowledge-routing.md",
                 "references/design-handoff.md", "references/typography-relations.md"):
        check("rule-contract.md" in read(PKG / path),
              f"Rule contract not linked from {path}")
    scenarios = read(PKG / "tests/architecture-scenarios.md")
    for code in range(29, 34):
        check(f"| R-{code} |" in scenarios,
              f"Missing knowledge-boundary scenario R-{code}")
    presets = read(PKG / "references/typography-presets.md")
    check("PROJECT_POLICY" in presets and "opt-in" in presets,
          "User-approved project policy must be scoped and opt-in")

if __name__ == "__main__":
    check_preset_mapping()
    check_links()
    check_review_invocation()
    check_reference_math()
    check_print_routing()
    check_typography_widths()
    check_rule_contract()
    print("PASS: policy mappings, local docs links, legacy triggers, reference-math examples, "
          "print routing guards, documented typography widths")
