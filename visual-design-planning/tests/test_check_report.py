"""Tests for scripts/check_report.py (mechanical report checks)."""
from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_report.py"
SPEC = importlib.util.spec_from_file_location("check_report", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

FOOTNOTE = '<li id="fn1">기관 조사 보고서, 2026, 표 3. EV-01 · 등급 B</li>'
ADOPTION = """<section class="part" id="adoption"><div class="adoption">
<p class="basis">기준 브리프: brief-v2.md</p>
<h3>채택 방향</h3><h3>필요 결과물</h3><h3>근거 ID</h3><h3>제작 제약</h3><h3>남은 쟁점</h3>
</div></section>"""


def page(extra: str = "", adoption: bool = False, footnote: str = FOOTNOTE) -> str:
    sections = "".join(f'<section class="part" id="{name}"><p>{name}</p></section>'
                       for name in ("situation", "methods", "insights", "reframe", "directions", "next"))
    return ("<!doctype html><html><head><style>p{}</style></head><body><main>"
            '<header class="cover" id="cover"><h1>제목</h1></header>' + sections +
            (ADOPTION if adoption else "") +
            '<section class="appendix" id="appendix"><ol class="fn">' + footnote + "</ol></section>"
            '<p>8명 중 4명이 막혔다 <span class="badge b-rec">[측정/기록]</span>'
            '<sup><a href="#fn1">1</a></sup></p>' + extra + "</main></body></html>")


class CheckReportTest(unittest.TestCase):
    def problems(self, text: str, evidence: str | None = "EV-01") -> list[str]:
        return MODULE.check(text, evidence)["problems"]

    def test_clean_report_passes(self) -> None:
        self.assertEqual(self.problems(page()), [])
        self.assertEqual(self.problems(page(adoption=True)), [])

    def test_template_leftovers_fail(self) -> None:
        self.assertTrue(any("템플릿 주석" in p for p in self.problems(page("<!-- 제목 -->"))))
        self.assertTrue(any("{U}" in p for p in self.problems(page("<p>3단계 {U}</p>"))))
        run_path = page("<p>실행 경로: runs/&lt;run-id&gt;/</p>")
        self.assertTrue(any("<run-id>" in p for p in self.problems(run_path)))

    def test_tag_variants_and_badges_fail(self) -> None:
        self.assertTrue(any("(추론)" in p for p in self.problems(page("<p>단계 (추론)</p>"))))
        bad_badge = page('<span class="badge b-int">해석</span>')
        self.assertTrue(any("배지 이름" in p for p in self.problems(bad_badge)))

    def test_footnotes_need_link_ev_and_grade(self) -> None:
        self.assertTrue(any("#fn2" in p for p in self.problems(page('<a href="#fn2">2</a>'))))
        no_grade = page(footnote='<li id="fn1">기사. EV-01</li>')
        self.assertTrue(any("등급" in p for p in self.problems(no_grade)))
        self.assertEqual(self.problems(page(footnote='<li id="fn1">기사. EV-01 · B등급</li>')), [])
        self.assertTrue(any("근거 색인에 없는" in p for p in self.problems(page(), evidence="EV-02")))
        reordered = page(footnote='<li class="source" id="fn1">기사. EV-01 · 등급 B</li>')
        self.assertEqual(self.problems(reordered), [])
        quoted = page(footnote="<li id='fn1'>기사. EV-01 · 등급 B</li>").replace('href="#fn1"', "href='#fn1'")
        self.assertEqual(self.problems(quoted), [])

    def test_measured_tag_needs_source_nearby(self) -> None:
        far = page("<p>" + "가" * 400 + '<span class="badge b-rec">[측정/기록]</span></p>')
        self.assertTrue(any("같은 문단" in p for p in self.problems(far)))
        long_claim = page('<p>12명 중 5명 <span class="badge b-rec">[측정/기록]</span>' + "관찰 설명 " * 80 +
                          '<sup><a href="#fn1">1</a></sup></p>')
        self.assertEqual(self.problems(long_claim), [])
        row = page('<table><tr><td>5/12 <span class="badge b-rec">[측정/기록]</span></td>'
                   '<td>' + "설명 " * 100 + '</td><td>EV-01</td></tr></table>')
        self.assertEqual(self.problems(row), [])
        nested = page('<table><tr><td><p>5/12 <span class="badge b-rec">[측정/기록]</span></p></td>'
                      '<td>EV-01</td></tr></table>')
        self.assertEqual(self.problems(nested), [])

    def test_user_confirmed_calculation_needs_no_evidence_id(self) -> None:
        calc = page("<p>" + "가" * 400 + '마감까지 34일 <span class="badge b-rec">[측정/기록]</span>'
                    "(오늘~마감일, 사용자 확정 일정에서 계산)</p>")
        self.assertEqual(self.problems(calc), [])

    def test_commented_out_markup_is_ignored(self) -> None:
        template_adoption = ADOPTION.replace("brief-v2.md", "brief-vN.md").replace("<h3>근거 ID</h3>", "")
        disabled = page("<!-- 채택 뒤에만 아래 절을 연다.\n" + template_adoption + "\n-->")
        self.assertEqual(self.problems(disabled), [])
        hidden = page('<!-- <span class="badge b-int">해석</span> <a href="#fn9">9</a> -->')
        self.assertEqual(self.problems(hidden), [])

    def test_section_order_and_adoption_fields(self) -> None:
        swapped = page().replace('id="insights"', 'id="tmp"').replace('id="methods"', 'id="insights"')
        self.assertTrue(any("절 순서" in p for p in self.problems(swapped)))
        broken = page(adoption=True).replace("<h3>근거 ID</h3>", "")
        self.assertTrue(any("채택 절 필드" in p for p in self.problems(broken)))
        single_quote = lambda text: re.sub(r'id="([a-z0-9]+)"', r"id='\1'", text)
        single = single_quote(page(adoption=True))
        self.assertEqual(self.problems(single), [])
        hidden_broken = single_quote(broken)
        self.assertTrue(any("채택 절 필드" in p for p in self.problems(hidden_broken)))
        no_basis = single.replace("기준 브리프: brief-v2.md", "")
        self.assertTrue(any("기준 브리프" in p for p in self.problems(no_basis)))
        quoted_badge = page("<p>단계 <span class='badge b-int'>해석</span></p>")
        self.assertTrue(any("배지 이름" in p for p in self.problems(quoted_badge)))

    def test_template_itself_is_flagged(self) -> None:
        template = (ROOT / "assets" / "report-template.html").read_text(encoding="utf-8")
        self.assertEqual(MODULE.check(template)["status"], "FAIL", "빈 템플릿이 통과하면 안 된다")

    def test_cli_exit_codes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            good, bad = Path(tmp, "good.html"), Path(tmp, "bad.html")
            good.write_text(page(), encoding="utf-8")
            bad.write_text(page("<!-- 제목 -->"), encoding="utf-8")
            run = lambda *a: subprocess.run([sys.executable, str(SCRIPT), *a], capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(run(str(good)).returncode, 0)
            result = run(str(bad))
            self.assertEqual(result.returncode, 1)
            self.assertEqual(json.loads(result.stdout)["status"], "FAIL")
            blocked = run(str(Path(tmp, "missing.html")))
            self.assertEqual(blocked.returncode, 2)
            self.assertEqual(json.loads(blocked.stderr)["status"], "BLOCKED")


if __name__ == "__main__":
    unittest.main()
