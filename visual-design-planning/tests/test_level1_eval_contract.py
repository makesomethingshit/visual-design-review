#!/usr/bin/env python3
"""레벨 1 기획 스킬 실전 평가 케이스의 구조·정합 검사.

이 테스트는 문서·픽스처·평가 가이드가 같은 계약을 말하는지만 검사한다.
실제 Codex 세션에서 스킬이 그 계약대로 동작했는지는 검사하지 않는다.
"""
from __future__ import annotations

import hashlib
import json
import re
import unittest
from datetime import datetime
from pathlib import Path

TESTS = Path(__file__).resolve().parent
PLANNING = TESTS.parent
ROOT = PLANNING.parent
WORKFLOW = PLANNING / "references" / "workflow"
METHODS = PLANNING / "references" / "methods"
INDEX = METHODS / "01.methods-index.md"
EVAL = TESTS / "evaluation" / "level1"
GUIDE = TESTS / "eval-cases.md"

# 레벨 1 워크플로 7단계가 각 단계에서 반드시 언급해야 하는 말.
STEP_KEYWORDS = {
    1: ("실행 기록 관리", "새 의뢰"),
    2: ("맥락 확인", "과제 분할"),
    3: ("카드", "미수행 사유"),
    4: ("리서치", "배정"),
    5: ("분석", "병렬"),
    6: ("취합", "미수행"),
    7: ("review-v1.md",),
}

# 인계 5필드의 기준 표기. lead-state-lifecycle.md의 '인계 기록' 절이 유일한 기준이다.
HANDOFF_FIELDS = ("채택 방향", "필요 결과물", "근거 ID", "제작 제약", "남은 쟁점")
# 인계 필드별 ID 접두어와 한 문서 안의 번호 표기.
HANDOFF_ID_PREFIXES = {"채택 방향": "DIR-01", "필요 결과물": "DEL-01",
                       "근거 ID": "EV-01", "제작 제약": "C-01",
                       "남은 쟁점": "U-01"}
# 통일 전 표기. 필드 이름으로 다시 쓰지 않는다.
OLD_FIELD_LABELS = ("채택한 방향", "채택된 방향", "미결 쟁점")
# cases.json의 status 허용값. 실행 후 상태를 갱신해도 계약 검사가 깨지지 않아야 한다.
ALLOWED_CASE_STATUSES = {"authored-not-executed", "partially-executed", "executed"}

# level-1 금지 행위를 문서에서 뒷받침하는 문구.
FORBIDDEN_SOURCES = {
    "새 인터뷰": ("SKILL.md", "새 인터뷰"),
    "새 설문·모집·시행": ("SKILL.md", "설문"),
    "시제품·실험": ("SKILL.md", "시제품·실험"),
    "시각적 평가": ("SKILL.md", "시각적 평가"),
    "제작·시안 생성": ("SKILL.md", "제작"),
    "레벨 2 시안 워크플로 실행": ("visual-design-drafting/references/workflow/level-2.md",
                                  "## 3. 복수 시안 생성"),
    "레벨 3 비평·타이포 프리셋 적용": ("SKILL.md", "visual-design-review"),
}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_cases() -> dict:
    return json.loads(read(EVAL / "cases.json"))


def load_template() -> dict:
    return json.loads(read(EVAL / "prompt-template.json"))


def assemble_prompt(template: dict, case: dict, turn_index: int) -> str:
    turn = case["turns"][turn_index]
    if turn_index == 0:
        return (template["common"] + template["skill_prefix"]
                + template["input_prefix"] + turn["text"])
    return template["followup_prefix"] + turn["text"]


def method_card_path(method_id: str) -> Path:
    return METHODS / method_id


def doc_path(relative: str) -> Path:
    """SKILL.md는 기획 스킬 폴더, 나머지는 저장소 루트 기준."""
    return PLANNING / relative if relative == "SKILL.md" else ROOT / relative


def index_entries() -> list[tuple[str, str]]:
    """(카드 상대 경로, 인덱스 표시 이름) 목록."""
    entries = []
    for label, target in re.findall(
            r"\[([^\]]+)\]\((\d{2}-[^)/]+/[^)/]+\.md)\)", read(INDEX)):
        entries.append((target, label.strip()))
    return entries


def guide_prompt_blocks() -> dict[str, str]:
    text = read(GUIDE)
    pattern = re.compile(
        r"<!-- level1-eval:prompt:([A-Z0-9-]+) -->\n```text\n(.*?)\n```", re.S)
    return {key: body.strip("\n") for key, body in pattern.findall(text)}


class WorkflowContractTest(unittest.TestCase):
    """레벨 1 워크플로 7단계와 상태·인계 계약."""

    def setUp(self) -> None:
        self.level1 = read(WORKFLOW / "level-1.md")
        self.skill = read(PLANNING / "SKILL.md")

    def test_seven_numbered_steps(self) -> None:
        steps = re.findall(r"(?m)^(\d)\. ", self.level1)
        self.assertEqual([int(s) for s in steps], [1, 2, 3, 4, 5, 6, 7],
                         "level-1.md의 단계 번호가 1~7 순서가 아니다")
        items = dict(re.findall(r"(?m)^(\d)\. (.+?)(?=\n\d\. |\Z)", self.level1,
                                flags=re.S))
        for number, keywords in STEP_KEYWORDS.items():
            body = items[str(number)]
            for keyword in keywords:
                self.assertIn(keyword, body,
                              f"level-1.md {number}단계에 '{keyword}'가 없다")

    def test_workflow_documents_are_reachable(self) -> None:
        self.assertIn("(references/workflow/level-1.md)", self.skill)
        for name in ("context-align", "lead-state-lifecycle",
                     "task-decomposition", "task-exchange"):
            self.assertIn(f"({name}.md)", self.level1,
                          f"level-1.md가 {name}.md를 열지 않는다")
            self.assertTrue((WORKFLOW / f"{name}.md").is_file())
        self.assertIn("(../methods/01.methods-index.md)", self.level1)

    def test_task_state_contract(self) -> None:
        text = read(WORKFLOW / "lead-state-lifecycle.md")
        match = re.search(r"과제 상태는 (.+?)를 사용한다", text)
        self.assertIsNotNone(match, "상태 목록 문장을 찾지 못했다")
        states = [state.strip() for state in match.group(1).split("·")]
        scope = load_cases()["scope"]["task_states"]
        self.assertEqual(states, scope,
                         "lead-state-lifecycle.md의 상태와 평가 픽스처의 상태가 다르다")
        self.assertEqual(len(states), 6)
        # 취합은 대기·진행이 남지 않았을 때 한 번.
        self.assertIn("대기", self.level1)
        self.assertIn("진행", self.level1)
        self.assertIn("부분 완료", self.level1)

    def test_run_folder_and_versioning(self) -> None:
        text = read(WORKFLOW / "lead-state-lifecycle.md")
        for token in ("runs/exhibition-01", "lead-state.md", "evidence-index.md",
                      "review-v1.md", "review-v2.md", "확인"):
            self.assertIn(token, text, f"실행 기록 규칙에 '{token}'가 없다")
        self.assertIn("근거 ID", read(WORKFLOW / "task-exchange.md"))
        self.assertIn("evidence-index.md", read(ROOT / "docs/architecture.html"))

    def test_handoff_fields(self) -> None:
        scope = load_cases()["scope"]
        self.assertEqual(scope["handoff_fields"], list(HANDOFF_FIELDS))
        lifecycle = read(WORKFLOW / "lead-state-lifecycle.md")
        level2 = read(ROOT / "visual-design-drafting/references/workflow/level-2.md")
        intake = read(ROOT / "visual-design-drafting/references/contracts/draft-intake.md")
        for field in HANDOFF_FIELDS:
            self.assertIn(field, self.level1, f"level-1.md 7단계에 인계 필드 '{field}'가 없다")
            self.assertIn(field, lifecycle, f"인계 기록 절에 '{field}'가 없다")
            self.assertIn(field, level2, f"레벨 2 인계 계약에 '{field}'가 없다")
            self.assertIn(field, intake, f"draft-intake.md에 '{field}'가 없다")
        # 기준 표는 하나만 두고 순서를 고정한다.
        table_fields = re.findall(r"(?m)^\| \d \| \*\*(.+?)\*\* \|", lifecycle)
        self.assertEqual(tuple(table_fields), HANDOFF_FIELDS,
                         "lead-state-lifecycle.md의 인계 필드 표 순서가 기준과 다르다")
        for label in OLD_FIELD_LABELS:
            for name, text in (("level-2.md", level2), ("draft-intake.md", intake)):
                self.assertNotIn(label, text, f"{name}에 통일 전 표기 '{label}'가 남아 있다")

    def test_handoff_ids_are_defined_once(self) -> None:
        lifecycle = read(WORKFLOW / "lead-state-lifecycle.md")
        intake = read(ROOT / "visual-design-drafting/references/contracts/draft-intake.md")
        level2 = read(ROOT / "visual-design-drafting/references/workflow/level-2.md")
        for field, identifier in HANDOFF_ID_PREFIXES.items():
            self.assertIn(identifier, lifecycle, f"인계 기록 절에 '{field}'의 ID "
                                                  f"예시 {identifier}가 없다")
            self.assertIn(identifier, intake, f"draft-intake.md에 ID 예시 {identifier}가 없다")
        for token in ("id_origin", "LEVEL2_NORMALIZED", "NO-EVIDENCE", "부여"):
            self.assertIn(token, lifecycle, f"인계 기록 절에 ID 규칙 '{token}'가 없다")
        for token in ("id_origin", "LEVEL2_NORMALIZED", "NO-EVIDENCE", "다시 매기"):
            self.assertIn(token, intake, f"draft-intake.md에 ID 규칙 '{token}'가 없다")
        self.assertIn("다시 매기", level2, "level-2.md가 ID 재부여를 긍정하지 않는다")

    def test_deliverable_list_is_a_fifth_handoff_field(self) -> None:
        """인계 5번째 필드 '필요 결과물'(`DEL-xx`)이 레벨 1·2 문서에서 같은 뜻으로 이어진다."""
        lifecycle = read(WORKFLOW / "lead-state-lifecycle.md")
        level2 = read(ROOT / "visual-design-drafting/references/workflow/level-2.md")
        intake = read(ROOT / "visual-design-drafting/references/contracts/draft-intake.md")
        evidence = read(ROOT / "visual-design-drafting/references/contracts/evidence-map.md")
        handoff = read(ROOT / "visual-design-drafting/references/contracts/draft-handoff.md")
        # 레벨 1: 항목별 품목·매체·목적·우선순위·연결 근거 ID와 두 자리 DEL 번호.
        for token in ("필요 결과물", "DEL-01", "품목", "매체", "목적",
                      "우선순위", "두 자리"):
            self.assertIn(token, lifecycle, f"인계 기록 절에 '{token}'가 없다")
        self.assertIn("조사·삼각검증", self.level1 + self.skill,
                      "레벨 1이 필요 결과물을 조사·삼각검증 뒤에 정한다고 밝히지 않는다")
        # 레벨 2: 필수 인계 필드와 시안 트랙 매핑.
        for token in ("필요 결과물", "deliverables", "DEL-01", "draft_track"):
            self.assertIn(token, intake, f"draft-intake.md에 '{token}'가 없다")
        for token in ("필요 결과물", "DEL", "draft-a", "draft-b"):
            self.assertIn(token, level2, f"level-2.md에 '{token}' 연결이 없다")
        for name, text in (("evidence-map.md", evidence), ("draft-handoff.md", handoff)):
            for token in ("필요 결과물", "DEL"):
                self.assertIn(token, text, f"{name}에 '{token}' 연결이 없다")
        # 픽스처·가이드: 5필드 계약이 E3 채택 턴과 판정표에 반영됐다.
        scope = load_cases()["scope"]
        self.assertIn("필요 결과물", scope["handoff_fields"])
        e3 = [case for case in load_cases()["cases"] if case["id"] == "E3"][0]
        self.assertIn("필요 결과물", " ".join(e3["turns"][1]["checks"]))
        self.assertTrue(any("DEL" in row["pass"] for row in e3["rubric"]),
                        "E3 판정표에 DEL-xx를 요구하는 항목이 없다")
        self.assertIn("필요 결과물", read(GUIDE))

    def test_handoff_lives_in_the_review_adoption_section(self) -> None:
        lifecycle = read(WORKFLOW / "lead-state-lifecycle.md")
        for name, text in (("level-1.md", self.level1), ("lead-state-lifecycle.md", lifecycle)):
            self.assertIn("## 채택", text, f"{name}에 채택 절 규칙이 없다")
            self.assertIn("review-vN.md", text, f"{name}가 채택 절 파일명을 밝히지 않는다")
            self.assertIn("번호가 가장 높은", text,
                          f"{name}가 레벨 2가 여는 리뷰 파일을 밝히지 않는다")
            self.assertIn("handoff.md", text, f"{name}가 별도 인계 파일을 언급하지 않는다")
        self.assertIn("visual-design-drafting", self.level1,
                      "level-1.md가 레벨 2 다음 단계를 밝히지 않는다")
        self.assertIn("PARTIAL", self.level1,
                      "레벨 2가 채택 절 없는 리뷰를 PARTIAL로 본다는 연결이 없다")
        self.assertIn("visual-design-drafting", self.skill,
                      "planning SKILL.md가 레벨 2 다음 단계를 밝히지 않는다")

    def test_forbidden_scope(self) -> None:
        self.assertIn("새 인터뷰·설문·현장조사", self.skill)
        self.assertIn("시제품·실험", self.skill)
        self.assertIn("시각적 평가와 제작은 레벨 1 범위 밖", self.skill)
        self.assertIn("진행 중 사용자에게 새 조사를 맡기지 않는다", self.level1)
        # 질문지 초안은 문서로만, 시행은 범위 밖.
        diagram = read(ROOT / "docs/architecture.html")
        self.assertIn("질문지 초안은 가능하지만 모집·설문 시행은 이 루프 밖이다", diagram)

    def test_claim_tags(self) -> None:
        exchange = read(WORKFLOW / "task-exchange.md")
        for tag in ("[측정/기록]", "[추론]", "[추측]"):
            self.assertIn(tag, exchange, f"주장 구분 '{tag}'가 task-exchange.md에 없다")
            self.assertIn(tag, self.level1,
                          f"7단계가 '{tag}'를 검토 보고서에 적용하지 않는다")
        self.assertIn("review-vN.md", exchange, "태그 규칙이 총괄 자신의 보고서를 가리키지 않는다")
        self.assertIn("총괄", exchange)


class MethodIndexTest(unittest.TestCase):
    """방법 카드 인덱스와 실제 카드 파일의 정합."""

    def test_index_links_each_card_once(self) -> None:
        entries = index_entries()
        targets = [target for target, _ in entries]
        self.assertEqual(len(targets), len(set(targets)), "인덱스에 중복 링크가 있다")
        cards = {p.relative_to(METHODS).as_posix() for p in METHODS.glob("*/*.md")}
        self.assertEqual(set(targets), cards, "인덱스와 카드 파일 집합이 다르다")

    def test_index_label_matches_card_title(self) -> None:
        for target, label in index_entries():
            card = method_card_path(target)
            self.assertTrue(card.is_file(), f"카드 파일이 없다: {target}")
            title = read(card).splitlines()[0].removeprefix("# ").strip()
            self.assertEqual(label, title, f"인덱스 이름과 카드 제목이 다르다: {target}")

    def test_category_counts(self) -> None:
        total = 0
        for heading in re.findall(r"(?m)^## (.+?) · (\d+)개$", read(INDEX)):
            _, count = heading
            total += int(count)
        self.assertEqual(total, len(index_entries()))
        self.assertEqual(total, len(list(METHODS.glob("*/*.md"))))


class FixtureContractTest(unittest.TestCase):
    """세 실전 브리프 픽스처의 기대 계약."""

    def setUp(self) -> None:
        self.data = load_cases()
        self.cases = {case["id"]: case for case in self.data["cases"]}
        self.scope = self.data["scope"]

    def test_three_cases(self) -> None:
        self.assertEqual(list(self.cases), ["E1", "E2", "E3"])
        self.assertEqual(len(self.scope["task_states"]), 6)

    def test_status_is_a_known_execution_state(self) -> None:
        self.assertIn(self.data["status"], ALLOWED_CASE_STATUSES,
                      "cases.json의 status가 허용된 실행 상태가 아니다")

    def test_guide_banner_matches_execution_state(self) -> None:
        guide = read(GUIDE)
        path = EVAL / "runs.jsonl"
        records = ([line for line in read(path).splitlines() if line.strip()]
                   if path.exists() else [])
        if self.data["status"] == "authored-not-executed":
            self.assertFalse(records,
                             "runs.jsonl에 기록이 있는데 status가 authored-not-executed다")
            self.assertIn("실행 기록이 없다", guide,
                          "실행 전인데 가이드가 그 사실을 밝히지 않는다")
        else:
            self.assertNotIn("아직 어떤 세션에서도 실행되지 않았다", guide,
                             "status를 실행됨으로 바꿨는데 가이드가 실행 전이라고 말한다")

    def test_material_fixtures_exist(self) -> None:
        for case in self.data["cases"]:
            materials = case.get("materials")
            if not materials:
                continue
            folder = TESTS / materials["path"]
            self.assertTrue(folder.is_dir(), f"{case['id']} 자료 폴더가 없다: {materials['path']}")
            self.assertIn("README.md", materials["files"],
                          f"{case['id']} 자료에 범위·한계를 적은 README가 없다")
            for name in materials["files"]:
                self.assertTrue((folder / name).is_file(),
                                f"{case['id']} 자료 파일이 없다: {name}")
            self.assertIn("materials/", case["turns"][0]["text"],
                          f"{case['id']} 프롬프트가 자료 위치를 알려 주지 않는다")
            self.assertTrue(case["expected"].get("materials_not_provided", "").strip(),
                            f"{case['id']}에 자료 미제공 분기가 없다")
        self.assertNotIn("materials", self.cases["E1"],
                         "E1은 제공 자료가 없는 브리프이므로 자료 폴더를 두지 않는다")

    def test_scope_matches_documents(self) -> None:
        self.assertEqual(self.scope["level1_steps"], 7)
        skill = read(PLANNING / "SKILL.md")
        for action in self.scope["level1_forbidden_actions"]:
            path, phrase = FORBIDDEN_SOURCES[action]
            self.assertIn(phrase, read(doc_path(path)),
                          f"금지 행위 '{action}'의 근거 문구가 {path}에 없다")
        self.assertIn("새 인터뷰", skill)
        for tag in self.scope["required_claim_tags"]:
            self.assertIn(tag, read(WORKFLOW / "task-exchange.md"))

    def test_each_case_forbids_level1_scope(self) -> None:
        for case in self.data["cases"]:
            forbidden = case["expected"]["forbidden"]
            missing = set(self.scope["level1_forbidden_actions"]) - set(forbidden)
            self.assertFalse(missing, f"{case['id']}에 금지 행위가 빠졌다: {missing}")

    def test_print_case_keeps_level_two_three_boundary(self) -> None:
        forbidden = self.cases["E3"]["expected"]["forbidden"]
        self.assertIn("레벨 2 시안 워크플로 실행", forbidden)
        self.assertIn("레벨 3 비평·타이포 프리셋 적용", forbidden)

    def test_tasks_and_method_ids_exist(self) -> None:
        indexed = {target for target, _ in index_entries()}
        for case in self.data["cases"]:
            tasks = case["tasks_after_agreement"]
            ids = [task["id"] for task in tasks]
            self.assertEqual(len(ids), len(set(ids)), f"{case['id']} 과제 ID 중복")
            for task in tasks:
                self.assertTrue(task["question"].strip())
                self.assertGreaterEqual(len(task["acceptable_method_ids"]), 1,
                                        f"{task['id']}에 방법 카드가 없다")
                for method_id in task["acceptable_method_ids"]:
                    self.assertIn(method_id, indexed,
                                  f"{task['id']}의 방법 카드가 인덱스에 없다: {method_id}")
                    self.assertTrue(method_card_path(method_id).is_file())
                for dependency in task["depends_on"]:
                    self.assertIn(dependency, ids,
                                  f"{task['id']}의 선행 과제가 없다: {dependency}")

    def test_tasks_are_acyclic(self) -> None:
        for case in self.data["cases"]:
            graph = {task["id"]: task["depends_on"]
                     for task in case["tasks_after_agreement"]}
            state: dict[str, int] = {}

            def visit(node: str) -> None:
                self.assertNotEqual(state.get(node), 1,
                                    f"{case['id']} 과제 선행 관계에 순환이 있다")
                if state.get(node) == 2:
                    return
                state[node] = 1
                for dependency in graph[node]:
                    visit(dependency)
                state[node] = 2

            for node in graph:
                visit(node)

    def test_ambiguous_case_holds_the_split(self) -> None:
        case = self.cases["E1"]
        first, second = case["turns"]
        self.assertEqual(first["expected_steps"], [1, 2],
                         "모호한 브리프는 맥락 확인 전에 분할하면 안 된다")
        self.assertEqual(first["kind"], "initial")
        self.assertNotIn(3, first["expected_steps"])
        self.assertTrue(case["expected"]["must_not_before_agreement"])
        self.assertGreaterEqual(len(case["expected"]["context_question_topics"]), 3)
        topics = " ".join(case["expected"]["context_question_topics"])
        for needed in ("기대 출력", "판단할 질문", "규격", "자산"):
            self.assertIn(needed, topics)
        self.assertTrue(case["expected"]["settled_items"])
        self.assertGreaterEqual(len(second["expected_steps"]), 3)

    def test_existing_evidence_case_requires_ids(self) -> None:
        case = self.cases["E2"]
        self.assertTrue(case["expected"]["claim_tags_required"])
        self.assertIn("근거 ID", " ".join(case["turns"][0]["checks"]))
        self.assertIn("새 인터뷰", case["expected"]["forbidden"])
        survey_task = [task for task in case["tasks_after_agreement"]
                       if any(method.endswith("existing-survey-response-review.md")
                              for method in task["acceptable_method_ids"])]
        self.assertTrue(survey_task, "제공 설문을 기존 설문 응답 조사로 잇지 않았다")
        triangulation = [task for task in case["tasks_after_agreement"]
                         if "04-evidence-analysis/triangulation.md"
                         in task["acceptable_method_ids"]]
        self.assertTrue(triangulation[0]["depends_on"],
                        "삼각검증 과제는 선행 분석 결과에 의존해야 한다")

    def test_print_case_handoff(self) -> None:
        case = self.cases["E3"]
        self.assertEqual(case["expected"]["handoff_fields"],
                         self.scope["handoff_fields"])
        kinds = [turn["kind"] for turn in case["turns"]]
        self.assertEqual(kinds, ["initial", "adoption"])
        self.assertIn("확정", case["turns"][1]["text"])
        rubric_ids = {row["id"] for row in case["rubric"]}
        self.assertIn("E3-7", rubric_ids)

    def test_rubric_rows_are_complete(self) -> None:
        for case in self.data["cases"]:
            rows = case["rubric"]
            self.assertGreaterEqual(len(rows), 6, f"{case['id']} 판정 항목이 적다")
            ids = [row["id"] for row in rows]
            self.assertEqual(len(ids), len(set(ids)), f"{case['id']} 판정 ID 중복")
            for row in rows:
                self.assertTrue(row["id"].startswith(case["id"] + "-"),
                                f"판정 ID 접두사 오류: {row['id']}")
                for key in ("check", "pass", "fail_example"):
                    self.assertTrue(row[key].strip(), f"{row['id']}의 {key}가 비었다")


class GuideContractTest(unittest.TestCase):
    """사람이 붙여 넣는 평가 가이드가 픽스처와 어긋나지 않는지."""

    def setUp(self) -> None:
        self.data = load_cases()
        self.template = load_template()
        self.text = read(GUIDE)

    def test_guide_covers_every_case_and_rubric(self) -> None:
        for case in self.data["cases"]:
            self.assertIn(case["id"], self.text)
            for row in case["rubric"]:
                self.assertIn(f"| {row['id']} |", self.text,
                              f"가이드에 판정 항목 {row['id']}가 없다")

    def test_guide_prompts_match_fixtures(self) -> None:
        blocks = guide_prompt_blocks()
        expected = {}
        for case in self.data["cases"]:
            for index, turn in enumerate(case["turns"]):
                expected[turn["id"]] = assemble_prompt(self.template, case, index)
        self.assertEqual(set(blocks), set(expected),
                         "가이드 프롬프트 블록과 픽스처 턴이 일치하지 않는다")
        for turn_id, prompt in expected.items():
            self.assertEqual(blocks[turn_id], prompt.strip("\n"),
                             f"{turn_id} 프롬프트가 cases.json과 다르다")

    def test_prompt_does_not_leak_expected_answers(self) -> None:
        for case in self.data["cases"]:
            prompt = assemble_prompt(self.template, case, 0)
            for task in case["tasks_after_agreement"]:
                self.assertNotIn(task["id"], prompt)
                for method_id in task["acceptable_method_ids"]:
                    self.assertNotIn(method_id.split("/", 1)[1], prompt)
            for row in case["rubric"]:
                self.assertNotIn(row["id"], prompt)
                self.assertNotIn(row["pass"], prompt)
            self.assertIn("사용자의 의뢰", prompt)
            self.assertIn(case["turns"][0]["text"][:20], prompt)

    def test_guide_states_it_is_not_evidence(self) -> None:
        for phrase in ("자동 테스트가 확인하는 것", "실행 기록",
                       "새 인터뷰", "질문지 초안"):
            self.assertIn(phrase, self.text, f"가이드에 '{phrase}' 안내가 없다")
        # 실행 기록이 생겨 배너를 고쳐도 이 경고는 남아야 한다(표현은 둘 중 하나면 된다).
        self.assertTrue("PASS가 아니다" in self.text or "PASS 처리하지 않는다" in self.text,
                        "가이드가 테스트 통과를 PASS로 오해하지 않게 하는 문장이 없다")
        self.assertNotIn("검증 완료", self.text)


class PromptToolTest(unittest.TestCase):
    """프롬프트 출력 도구가 픽스처와 같은 문자열·해시를 내는지."""

    def test_cli_matches_fixtures(self) -> None:
        import subprocess
        import sys

        template = load_template()
        tool = TESTS / "eval_prompt.py"
        for case in load_cases()["cases"]:
            for index, turn in enumerate(case["turns"]):
                result = subprocess.run(
                    [sys.executable, str(tool), turn["id"]],
                    capture_output=True, text=True, check=False,
                    encoding="utf-8")
                self.assertEqual(result.returncode, 0, result.stderr)
                expected = assemble_prompt(template, case, index)
                self.assertEqual(result.stdout, expected + "\n")
                digest = hashlib.sha256(expected.encode("utf-8")).hexdigest()
                self.assertIn("prompt_sha256: " + digest, result.stderr)

    def test_cli_rejects_unknown_turn(self) -> None:
        import subprocess
        import sys

        result = subprocess.run(
            [sys.executable, str(TESTS / "eval_prompt.py"), "E9-T9"],
            capture_output=True, text=True, check=False, encoding="utf-8")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unknown turn", result.stderr)


class PackagingTest(unittest.TestCase):
    """평가 자산이 배포 플러그인 사본에 섞이지 않는지."""

    def test_eval_assets_stay_out_of_the_plugin_package(self) -> None:
        packaged = (ROOT / "plugins/visual-design/skills/visual-design-planning")
        self.assertFalse((packaged / "tests").exists(),
                         "평가 케이스는 canonical 스킬 폴더에만 둔다")
        for path in ("tests/eval-cases.md", "tests/test_level1_eval_contract.py",
                     "tests/eval_prompt.py",
                     "tests/evaluation/level1/cases.json",
                     "tests/evaluation/level1/fixtures/README.md",
                     "tests/evaluation/level1/fixtures/e2/README.md",
                     "tests/evaluation/level1/fixtures/e3/README.md"):
            self.assertTrue((PLANNING / path).is_file(), f"평가 자산이 없다: {path}")


class RunRecordTest(unittest.TestCase):
    """실행 기록이 있다면 형식·경로·근거 인용을 검사한다.

    기록이 없으면 기존과 같은 안내만 확인하고 통과한다. 실제 실행 전에는
    이 검사가 아무 기록도 요구하지 않는다.
    """

    REQUIRED = {"run_id", "case_id", "turn_id", "date", "model",
                "skill_version", "isolation", "prompt_sha256", "transcript",
                "artifacts", "verdicts"}
    ALLOWED_SUFFIXES = (".md", ".jsonl", ".json", ".txt", ".csv",
                        ".png", ".jpg", ".jpeg", ".svg", ".html", ".pdf")
    PLACEHOLDERS = {"todo", "tbd", "n/a", "미정", "없음", "-", "?"}

    def _path_problem(self, value: object) -> str | None:
        if not isinstance(value, str) or not value.strip():
            return "빈 경로"
        if value.startswith(("http://", "https://")):
            return None
        if ".." in Path(value).parts:
            return "상위 경로 이동(..)"
        if not Path(value).name:
            return "파일 이름이 없는 경로"
        if Path(value).suffix.lower() not in self.ALLOWED_SUFFIXES:
            return f"허용하지 않는 확장자: {Path(value).suffix or '(없음)'}"
        return None

    def test_run_records_if_present(self) -> None:
        path = EVAL / "runs.jsonl"
        cases = {case["id"]: case for case in load_cases()["cases"]}
        template = load_template()
        lines = ([line for line in read(path).splitlines() if line.strip()]
                 if path.exists() else [])
        if not lines:
            self.assertIn("실행 기록이 없다", read(GUIDE),
                          "실행 기록이 없으면 가이드가 그 상태를 밝혀야 한다")
            return
        for number, line in enumerate(lines, 1):
            record = json.loads(line)
            missing = self.REQUIRED - set(record)
            self.assertFalse(missing, f"{number}행에 필수 필드가 없다: {sorted(missing)}")

            self.assertIsInstance(record["run_id"], str)
            self.assertTrue(record["run_id"].strip(), f"{number}행 run_id가 비었다")
            self.assertIn(record["case_id"], cases, f"{number}행의 케이스 ID가 픽스처에 없다")
            case = cases[record["case_id"]]
            turn = [turn for turn in case["turns"] if turn["id"] == record["turn_id"]]
            self.assertTrue(turn, f"{number}행의 턴 ID가 픽스처에 없다")

            try:
                parsed_date = datetime.fromisoformat(record["date"])
            except (TypeError, ValueError):
                self.fail(f"{number}행 date가 ISO 8601이 아니다: {record['date']!r}")
            self.assertIsNotNone(parsed_date.tzinfo,
                                 f"{number}행 date에 시간대가 없다")
            self.assertTrue(str(record["model"]).strip(), f"{number}행 model이 비었다")
            self.assertRegex(str(record["skill_version"]), r"^\d+\.\d+\.\d+$",
                             f"{number}행 skill_version 형식이 다르다")
            self.assertIn(record["isolation"], ("network-off", "network-on"),
                          f"{number}행 isolation 값이 잘못됐다")

            expected = assemble_prompt(template, case, case["turns"].index(turn[0]))
            self.assertEqual(record["prompt_sha256"],
                             hashlib.sha256(expected.encode("utf-8")).hexdigest(),
                             f"{number}행의 프롬프트 해시가 픽스처와 다르다")

            problem = self._path_problem(record["transcript"])
            self.assertIsNone(problem, f"{number}행 transcript 경로: {problem}")

            artifacts = record["artifacts"]
            self.assertIsInstance(artifacts, list, f"{number}행 artifacts가 목록이 아니다")
            self.assertTrue(artifacts, f"{number}행 artifacts가 비었다")
            self.assertEqual(len(artifacts), len(set(artifacts)),
                             f"{number}행 artifacts에 중복 경로가 있다")
            for artifact in artifacts:
                problem = self._path_problem(artifact)
                self.assertIsNone(problem, f"{number}행 artifact 경로: {problem}")
                parts = Path(artifact).parts
                if parts and parts[0] == "runs":
                    self.assertGreaterEqual(len(parts), 3,
                                            f"{number}행 artifact가 runs/<run-id>/ 파일이 아니다")
                    self.assertTrue(record["run_id"].startswith(parts[1]),
                                    f"{number}행 artifact의 실행 폴더({parts[1]})가 "
                                    f"run_id({record['run_id']})와 맞지 않는다")

            if "materials" in record:
                materials = record["materials"]
                self.assertTrue(materials == "none" or
                                (isinstance(materials, str) and materials.strip()),
                                f"{number}행 materials가 비었다")

            verdicts = record["verdicts"]
            self.assertIsInstance(verdicts, list, f"{number}행 verdicts가 목록이 아니다")
            self.assertTrue(verdicts, f"{number}행 verdicts가 비었다")
            rubric_ids = {row["id"] for row in case["rubric"]}
            for verdict in verdicts:
                self.assertIn(verdict["rubric_id"], rubric_ids,
                              f"{number}행에 픽스처에 없는 판정 ID가 있다")
                self.assertIn(verdict["verdict"], ("pass", "fail", "blocked"),
                              f"{number}행 verdict 값이 잘못됐다")
                if verdict["verdict"] in ("pass", "fail"):
                    evidence = verdict.get("evidence", "")
                    self.assertIsInstance(evidence, str)
                    self.assertTrue(evidence.strip(),
                                    f"{verdict['rubric_id']}: 근거 없는 {verdict['verdict']}")
                    self.assertGreaterEqual(len(evidence.strip()), 4,
                                            f"{verdict['rubric_id']}: 근거가 너무 짧다")
                    self.assertNotIn(evidence.strip().lower(), self.PLACEHOLDERS,
                                     f"{verdict['rubric_id']}: 자리표시자 근거")


if __name__ == "__main__":
    unittest.main()
