"""Persist the proposed answer; task correctness is decided by the verifier."""

import json
from pathlib import Path

from slimconfig import plain_output

from contract import AnswerInput, ResultOutput


def write_result(value: AnswerInput, workspace: Path) -> ResultOutput:
    path = workspace / "result.json"
    if path.is_symlink():
        raise ValueError("result.json must not be a symlink")
    workspace.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(plain_output(value), indent=2) + "\n", encoding="utf-8")
    return ResultOutput(path="result.json", count=len(value.rows))
