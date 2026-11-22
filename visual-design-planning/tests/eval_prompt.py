#!/usr/bin/env python3
"""레벨 1 평가 턴의 프롬프트를 표준출력으로 내고 SHA-256을 표준오류로 알린다.

사용:
    python3 visual-design-planning/tests/eval_prompt.py E1-T1 > prompt.txt

표준출력은 cases.json과 prompt-template.json으로 조립한 그 턴의 프롬프트이고,
표준오류에는 실행 기록(runs.jsonl)의 prompt_sha256에 넣을 해시가 나온다.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

EVAL = Path(__file__).resolve().parent / "evaluation" / "level1"


def load(name: str) -> dict:
    return json.loads((EVAL / name).read_text(encoding="utf-8"))


def assemble(case: dict, turn_index: int, template: dict) -> str:
    turn = case["turns"][turn_index]
    if turn_index == 0:
        return (template["common"] + template["skill_prefix"]
                + template["input_prefix"] + turn["text"])
    return template["followup_prefix"] + turn["text"]


def find_turn(turn_id: str) -> tuple[dict, int]:
    for case in load("cases.json")["cases"]:
        for index, turn in enumerate(case["turns"]):
            if turn["id"] == turn_id:
                return case, index
    raise SystemExit("unknown turn: " + turn_id)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: eval_prompt.py <turn-id>  (예: E1-T1)", file=sys.stderr)
        return 2
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    case, index = find_turn(argv[1])
    prompt = assemble(case, index, load("prompt-template.json"))
    sys.stdout.write(prompt + "\n")
    print("prompt_sha256: " + hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
