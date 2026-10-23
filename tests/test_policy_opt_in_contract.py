"""Regression checks for contradictory policy activation instructions, not model behavior."""
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

MODULE = Path(__file__).with_name("check-knowledge-contract.py")
spec = importlib.util.spec_from_file_location("contract", MODULE)
contract = importlib.util.module_from_spec(spec)
spec.loader.exec_module(contract)


class PolicyActivationTests(unittest.TestCase):
    def test_consistent_documents(self):
        contract.check_policy_activation()

    def test_missing_entry_guard_rejected(self):
        original = contract.read
        with patch.object(contract, "read", side_effect=lambda p:
                          original(p).replace("명시적 opt-in", "조건 확인")
                          if p.name == "SKILL.md" else original(p)):
            with self.assertRaisesRegex(AssertionError, "current-task opt-in"):
                contract.check_policy_activation()

    def test_handoff_without_activation_evidence_rejected(self):
        original = contract.read
        with patch.object(contract, "read", side_effect=lambda p:
                          original(p).replace("opt_in: true", "")
                          if p.name == "design-handoff.md" else original(p)):
            with self.assertRaisesRegex(AssertionError, "activation evidence"):
                contract.check_policy_activation()

    def test_positive_scenario_without_opt_in_rejected(self):
        original = contract.read
        with patch.object(contract, "read", side_effect=lambda p:
                          original(p).replace("A~H 프로젝트 프로파일을 명시적으로 적용", "기본값 추천")
                          if p.name == "architecture-scenarios.md" else original(p)):
            with self.assertRaisesRegex(AssertionError, "Positive preset scenario"):
                contract.check_policy_activation()


if __name__ == "__main__":
    unittest.main()
