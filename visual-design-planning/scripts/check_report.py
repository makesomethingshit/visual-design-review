"""Mechanical checks for a level 1 review report (review-vN.html).

Checks section order, leftover template comments and placeholders, claim-tag
names and variant spellings, footnote links with evidence IDs and grades,
evidence IDs against evidence-index.md, and the adoption section's basis line
and five fields. Markup inside HTML comments is ignored, except that leftover
template guidance comments are reported. It does not judge the quality of the analysis.

Prints a JSON result. Exit 0 for PASS, 1 for FAIL, 2 when the input cannot be
read (BLOCKED).
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path

SECTIONS = ("cover", "situation", "methods", "insights", "reframe",
            "directions", "next", "adoption", "appendix")
OPTIONAL = {"adoption"}
TAGS = ("[측정/기록]", "[추론]", "[추측]", "사용자 확정")
VARIANTS = ("(측정/기록)", "(추론)", "(추측)", "[기록]", "[측정]", "[해석]",
            "[가설]", "(기록)", "(해석)", "(가설)")
HANDOFF_FIELDS = ("채택 방향", "필요 결과물", "근거 ID", "제작 제약", "남은 쟁점")
TEMPLATE_COMMENT = re.compile(
    r"<!--\s*(?:제목|근거가 지지하는|첫 1~2문장|값|무엇을 몇|방법 카드 이름|이 분석이|"
    r"고른 이유|인라인 SVG|결론|주장|근거와 각주|단, |재정의가|어떻게 하면|원칙이 어디서|"
    r"방향 이름|개념 한 문장|출처, 날짜|방법 → 이유|수치가 말하는|의뢰 대상이)")
# Matched against decoded text, so the template's &lt;run-id&gt; appears as <run-id>.
PLACEHOLDER = re.compile(r"\{[A-Za-z가-힣_]{1,20}\}|<run-id>|brief-vN\.md|DIR-xx|EV-xx")
EV = re.compile(r"\bEV-\d{2,}\b")
WINDOW = 240
BLOCK = re.compile(r"<(p|li|tr|figcaption|dd|blockquote|h[1-6])\b")


def claim_block(body: str, start: int, end: int) -> str:
    """The paragraph, list item or table row that holds a claim tag.

    Falls back to a fixed window only when the tag sits in no such block.
    """
    opens = [m for m in BLOCK.finditer(body, 0, start)]
    for match in reversed(opens):
        close = body.find(f"</{match.group(1)}>", end)
        if close != -1 and body.find(f"</{match.group(1)}>", match.end(), start) == -1:
            return body[match.start():close]
    return body[max(0, start - WINDOW):end + WINDOW]


def visible_text(fragment: str) -> str:
    fragment = re.sub(r"<!--.*?-->", " ", fragment, flags=re.S)
    fragment = re.sub(r"<(script|style)\b.*?</\1>", " ", fragment, flags=re.S)
    return html.unescape(re.sub(r"<[^>]+>", " ", fragment))


def check(page: str, evidence: str | None = None) -> dict:
    problems: list[str] = []
    raw = page.split("<body", 1)[-1]
    for match in TEMPLATE_COMMENT.finditer(raw):
        problems.append(f"템플릿 주석이 남아 있음: {match.group(0)[:30]}")
    # Commented-out markup (such as the template's disabled adoption section)
    # is not part of the report, so every structural check below ignores it.
    body = re.sub(r"<!--.*?-->", " ", raw, flags=re.S)

    found = [s for s in re.findall(r'<(?:section|header)\b[^>]*\bid="([a-z]+)"', body)
             if s in SECTIONS]
    expected = [s for s in SECTIONS if s in found or s not in OPTIONAL]
    if found != expected:
        problems.append(f"절 순서·누락: 기대 {expected}, 실제 {found}")

    text = visible_text(body)
    for match in sorted(set(PLACEHOLDER.findall(text))):
        problems.append(f"자리표시가 남아 있음: {match}")
    for variant in VARIANTS:
        if variant in text:
            problems.append(f"태그 변형 표기: {variant} (정해진 이름: {', '.join(TAGS)})")
    for badge in re.findall(r'<span class="badge[^"]*">(.*?)</span>', body, flags=re.S):
        label = visible_text(badge).strip()
        if label not in TAGS:
            problems.append(f"배지 이름이 태그와 다름: {label}")
    if re.search(r"<script\b", body) or re.search(r'\bsrc="https?://', page):
        problems.append("스크립트나 외부 자원이 있음")

    refs = sorted(set(re.findall(r'href="#(fn\d+)"', body)), key=lambda x: int(x[2:]))
    notes = dict(re.findall(r'<li id="(fn\d+)"[^>]*>(.*?)</li>', body, flags=re.S))
    for ref in refs:
        if ref not in notes:
            problems.append(f"각주 참조에 대응하는 각주가 없음: #{ref}")
    for note_id, note in notes.items():
        note_text = visible_text(note)
        if not EV.search(note_text):
            problems.append(f"각주에 근거 ID가 없음: {note_id}")
        if not re.search(r"등급\s*:?\s*[ABCD](?![A-Za-z])|(?<![A-Za-z])[ABCD]\s*등급", note_text):
            problems.append(f"각주에 근거 등급이 없음: {note_id}")

    for match in re.finditer(re.escape("[측정/기록]"), body):
        around = claim_block(body, match.start(), match.end())
        # A value computed only from what the user said cites 사용자 확정
        # instead of an evidence entry (report-format.md, computed values).
        if not (re.search(r'href="#fn\d+"', around) or EV.search(around)
                or "사용자 확정" in visible_text(around)):
            line = visible_text(body[max(0, match.start() - 80):match.end()]).strip()
            problems.append(f"[측정/기록]과 같은 문단·항목·행에 각주·근거 ID·사용자 확정 출처가 없음: …{line[-60:]}")

    if evidence is not None:
        known = set(EV.findall(evidence))
        for ev in sorted(set(EV.findall(text)) - known):
            problems.append(f"근거 색인에 없는 근거 ID: {ev}")

    adoption = re.search(r'<section\b[^>]*\bid="adoption".*?</section>', body, flags=re.S)
    if adoption:
        block = adoption.group(0)
        if not re.search(r"기준 브리프:\s*brief-v\d+\.md", visible_text(block)):
            problems.append("채택 절에 기준 브리프 줄이 없음")
        fields = tuple(visible_text(h).strip() for h in re.findall(r"<h3>(.*?)</h3>", block, flags=re.S))
        if fields != HANDOFF_FIELDS:
            problems.append(f"채택 절 필드가 계약과 다름: {list(fields)}")

    return {"status": "FAIL" if problems else "PASS", "problems": problems,
            "counts": {"sections": len(found), "footnotes": len(notes), "footnote_refs": len(refs),
                       "measured_tags": text.count("[측정/기록]")}}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path, help="review-vN.html")
    parser.add_argument("--evidence", type=Path, help="evidence-index.md of the same run")
    args = parser.parse_args(argv)
    try:
        page = args.report.read_text(encoding="utf-8")
        evidence = args.evidence.read_text(encoding="utf-8") if args.evidence else None
        if "<html" not in page.lower():
            raise ValueError("report is not an HTML document")
        result = check(page, evidence)
    except (OSError, ValueError) as exc:
        print(json.dumps({"status": "BLOCKED", "error": str(exc)}, ensure_ascii=False),
              file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
