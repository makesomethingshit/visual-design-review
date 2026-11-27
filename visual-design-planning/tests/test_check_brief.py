"""Tests for scripts/check_brief.py (mechanical brief checks)."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_brief.py"
SPEC = importlib.util.spec_from_file_location("check_brief", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

ITEMS = MODULE.ITEMS


def brief(overrides: dict[str, tuple[str, str]] | None = None, open_row: str | None = None) -> str:
    overrides = overrides or {}
    rows = []
    for name in ITEMS[:-1]:
        content, status = overrides.get(name, (f"사용자 확정: {name} 값", "사용자 확정"))
        rows.append(f"| {name} | {content} | {status} | 사용자 발화 1 |")
    if open_row is None:
        open_row = "예산: 인쇄비 포함 여부 — 사람에게 질문, 필요"
    rows.append(f"| 미확인 | {open_row} | 미확인 | — |")
    return "# 브리프 v1\n\n| 항목 | 내용 | 상태 | 근거 |\n| --- | --- | --- | --- |\n" + "\n".join(rows) + "\n"


MIXED = {"예산": ("사용자 확정: 30만 원 / 미확인: 인쇄비 포함 여부", "미확인")}


class CheckBriefTest(unittest.TestCase):
    def problems(self, text: str) -> list[str]:
        return MODULE.check(text)["problems"]

    def test_clean_brief_passes(self) -> None:
        self.assertEqual(self.problems(brief(MIXED)), [])

    def test_rows_and_columns_are_fixed(self) -> None:
        extra = brief(MIXED).replace("| 미확인 |", "| 비고 | 추가 | [추론] | — |\n| 미확인 |", 1)
        self.assertTrue(any("항목 행" in p for p in self.problems(extra)))
        renamed = brief(MIXED).replace("| 항목 | 내용 | 상태 | 근거 |", "| 항목 | 내용 | 상태 |")
        self.assertTrue(any("열" in p for p in self.problems(renamed)))

    def test_status_must_be_weakest(self) -> None:
        strong = {"예산": ("사용자 확정: 30만 원 / 미확인: 인쇄비 포함 여부", "사용자 확정")}
        self.assertTrue(any("가장 약한" in p for p in self.problems(brief(strong))))
        equal = {"제약": ("사용자 확정: A2 / [측정/기록] 594×420mm EV-01", "사용자 확정")}
        self.assertEqual(self.problems(brief({**MIXED, **equal})), [])
        self.assertTrue(any("상태 값" in p for p in self.problems(brief({"대상": ("x", "확정")}))))

    def test_every_open_part_reaches_row_12(self) -> None:
        scope = {**MIXED, "배경": ("사용자 확정: 단장 예정 / 미확인: 단장 범위(간판·메뉴 포함 여부)", "미확인")}
        self.assertTrue(any("배경:" in p for p in self.problems(brief(scope))))
        listed = brief(scope, "배경: 단장 범위 — 사람에게 질문, 필요; 예산: 인쇄비 포함 여부 — 사람에게 질문, 필요")
        self.assertEqual(self.problems(listed), [])

    def test_open_entry_needs_a_way_to_check(self) -> None:
        bare = brief(MIXED, "예산: 인쇄비 포함 여부")
        self.assertTrue(any("확인 방법" in p for p in self.problems(bare)))

    def test_cli_exit_codes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            good, bad = Path(tmp, "good.md"), Path(tmp, "bad.md")
            good.write_text(brief(MIXED), encoding="utf-8")
            bad.write_text(brief(MIXED, "인쇄비"), encoding="utf-8")
            run = lambda *a: subprocess.run([sys.executable, str(SCRIPT), *a], capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(run(str(good)).returncode, 0)
            result = run(str(bad))
            self.assertEqual(result.returncode, 1)
            self.assertEqual(json.loads(result.stdout)["status"], "FAIL")
            blocked = run(str(Path(tmp, "missing.md")))
            self.assertEqual(blocked.returncode, 2)
            self.assertEqual(json.loads(blocked.stderr)["status"], "BLOCKED")


if __name__ == "__main__":
    unittest.main()
