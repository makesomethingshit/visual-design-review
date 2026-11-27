"""Mechanical checks for a level 1 design brief (brief-vN.md).

Checks the fixed 12-row table (item names, order, columns), the status values,
that each row's status is the weakest status written in its content, that every
row with an unconfirmed part is listed in row 12 by its item name, and that each
row 12 entry follows `<항목>: <무엇> — <확인 방법>, <필요 여부>`. Row 12 is
`없음` when nothing is unconfirmed. It does not judge the content.

Prints a JSON result. Exit 0 for PASS, 1 for FAIL, 2 when the input cannot be
read (BLOCKED).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ITEMS = ("목표", "배경", "대상", "메시지", "결과물", "환경", "필수조건", "제약",
         "일정", "예산", "판단기준", "미확인")
COLUMNS = ("항목", "내용", "상태", "근거")
STATUSES = ("미확인", "[추측]", "[추론]", "[측정/기록]", "사용자 확정")
# Weakest first; a record and a user statement are equally strong.
RANK = {"미확인": 0, "[추측]": 1, "[추론]": 2, "[측정/기록]": 3, "사용자 확정": 3}
CHECK_WAYS = ("질문", "조사", "자료", "요청", "레벨 2", "레벨 3")
NONE_VALUES = ("없음", "해당 없음")


def cells(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def table(text: str) -> tuple[list[str], list[list[str]]]:
    lines = [l for l in text.splitlines() if l.lstrip().startswith("|")]
    if len(lines) < 2:
        return [], []
    header = cells(lines[0])
    rows = [cells(l) for l in lines[1:] if not re.fullmatch(r"[\s|:-]+", l)]
    return header, rows


def statuses_in(content: str) -> list[str]:
    return [s for s in STATUSES if s in content]


def check(text: str) -> dict:
    problems: list[str] = []
    header, rows = table(text)
    if tuple(header) != COLUMNS:
        problems.append(f"표의 열이 계약과 다름: 기대 {list(COLUMNS)}, 실제 {header}")
    names = [r[0] for r in rows]
    if tuple(names) != ITEMS:
        problems.append(f"항목 행이 계약과 다름: 기대 {list(ITEMS)}, 실제 {names}")
    by_name = {r[0]: r for r in rows if len(r) >= 3}
    open_row = by_name.get("미확인", ["", "", ""])[1]
    entries = [e.strip() for e in re.split(r"[①-⑳]|<br>|;", open_row) if e.strip()]

    for name in ITEMS[:-1]:
        row = by_name.get(name)
        if not row:
            continue
        content, status = row[1], row[2]
        if status not in STATUSES:
            problems.append(f"{name}: 상태 값이 정해진 이름이 아님: {status}")
            continue
        present = statuses_in(content)
        if present:
            weakest = min(present, key=RANK.get)
            if RANK[status] > RANK[weakest]:
                problems.append(f"{name}: 상태 칸 {status}가 내용의 가장 약한 상태 {weakest}보다 강함")
        if status == "미확인" or "미확인" in content:
            if not re.search(rf"(?<![가-힣]){re.escape(name)}\s*:", open_row):
                problems.append(f"{name}: 미확인 부분이 12번 미확인 행에 `{name}:`로 올라가 있지 않음")

    any_open = any(r[2] == "미확인" or "미확인" in r[1] for n, r in by_name.items() if n != "미확인")
    if open_row in NONE_VALUES or not open_row:
        if any_open:
            problems.append("다른 행에 미확인이 있는데 12번 미확인 행이 비었거나 '없음'임")
        elif not open_row:
            problems.append("12번 미확인 행이 비어 있음: 남은 미확인이 없으면 '없음'으로 적는다")
        entries = []
    for entry in entries:
        head, sep, tail = entry.partition("—")
        item = head.split(":", 1)[0].strip() if ":" in head else ""
        if item not in ITEMS[:-1]:
            problems.append(f"미확인 항목이 `<항목>:`으로 시작하지 않음: {entry[:40]}")
        if not sep:
            problems.append(f"미확인 항목에 `—` 뒤 확인 방법이 없음: {entry[:40]}")
            continue
        method, _, need = tail.rpartition(",")
        if not any(way in method for way in CHECK_WAYS):
            problems.append(f"미확인 항목의 확인 방법이 질문·조사가 아님: {entry[:40]}")
        if not re.search(r"필요|불필요", need):
            problems.append(f"미확인 항목에 다음 판단에 필요한지가 없음: {entry[:40]}")
    return {"status": "FAIL" if problems else "PASS", "problems": problems,
            "counts": {"rows": len(rows), "open_entries": len(entries)}}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("brief", type=Path, help="brief-vN.md")
    args = parser.parse_args(argv)
    try:
        result = check(args.brief.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(json.dumps({"status": "BLOCKED", "error": str(exc)}, ensure_ascii=False),
              file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
