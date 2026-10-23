"""Static document mutations, not a test of model behavior or a runtime router."""
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

MODULE = Path(__file__).with_name("check-knowledge-contract.py")
spec = importlib.util.spec_from_file_location("contract", MODULE)
contract = importlib.util.module_from_spec(spec)
spec.loader.exec_module(contract)


class PolicyActivationTests(unittest.TestCase):
    def assert_mutation_rejected(self, filename, old, new, reason):
        original = contract.read

        def mutated(path):
            text = original(path)
            if path.name == filename:
                self.assertIn(old, text)
                return text.replace(old, new)
            return text

        with patch.object(contract, "read", side_effect=mutated):
            with self.assertRaisesRegex(AssertionError, reason):
                contract.check_policy_activation()

    def test_consistent_documents(self):
        contract.check_policy_activation()

    def test_either_activation_route_missing_rejected(self):
        for filename in ("SKILL.md", "knowledge-routing.md", "design-handoff.md",
                         "typography-presets.md"):
            for route in ("명시적 opt-in", "독립적으로 확인된 현재 프로젝트의 활성 프로파일"):
                with self.subTest(filename=filename, route=route):
                    self.assert_mutation_rejected(filename, route, "조건 확인",
                                                  "alternative activation routes")

    def test_handoff_still_requiring_repeated_opt_in_rejected(self):
        self.assert_mutation_rejected(
            "design-handoff.md", "주언어 확인만으로 프로파일 선택을 대신하지 않는다.",
            "주언어 확인만으로 프로파일 선택을 대신하지 않는다. "
            "opt-in이 없으면 정책값을 자동 채택하지 않는다.", "Repeated opt-in")

    def test_independent_profile_evidence_guard_missing_rejected(self):
        for field in ("현재 프로젝트의 사용자 승인·A~H 선택·유효한 적용 범위", "자료 위치와 적용 범위"):
            with self.subTest(field=field):
                self.assert_mutation_rejected("typography-presets.md", field,
                                              "프로파일 이름", "independent activation evidence guard")

    def test_handoff_without_activation_evidence_rejected(self):
        for field, reason in (
            ("opt_in: true", "Explicit opt-in handoff"),
            ("activation_basis: explicit_user_request_for_current_project", "Explicit opt-in handoff"),
            ("activation_basis: independently_verified_active_project_profile", "Active-profile handoff"),
            ("project: current_project", "Active-profile handoff"),
            ('evidence: "current_project_brief#typography"', "Active-profile handoff"),
        ):
            with self.subTest(field=field):
                self.assert_mutation_rejected("design-handoff.md", field, "", reason)

    def test_positive_scenario_without_opt_in_rejected(self):
        self.assert_mutation_rejected(
            "architecture-scenarios.md", "A~H 프로젝트 프로파일을 명시적으로 적용",
            "기본값 추천", "Positive preset scenario")

    def test_active_profile_scenario_requires_evidence_and_no_repeat(self):
        for field in ("| R-34 |", "별도 프로젝트 설정/브리프",
                      "현재 프로젝트의 사용자 승인·A~H 활성 프로파일", "자료 위치와 적용 범위",
                      "opt-in 반복 없음", "opt-in을 다시 요구", "17pt 초기 시안 미제시",
                      "활성화 근거 누락"):
            with self.subTest(field=field):
                self.assert_mutation_rejected("architecture-scenarios.md", field,
                                              "", "verified active-profile scenario")

    def test_no_activation_scenario_cannot_inherit_presets(self):
        for field in ("| R-35 |", "현재 작업의 opt-in 없음", "확인된 활성 프로파일 없음",
                      "저장소에 승인 기록만", "후보/미결정 유지", "A~H 자동 채택"):
            with self.subTest(field=field):
                self.assert_mutation_rejected("architecture-scenarios.md", field,
                                              "", "no-activation scenario")


if __name__ == "__main__":
    unittest.main()
