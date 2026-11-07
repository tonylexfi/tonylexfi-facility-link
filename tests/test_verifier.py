"""Correct, incorrect, missing, malformed and boundary checks against hand-written gold answers."""

import json
from dataclasses import replace
from pathlib import Path

import pytest
from slimconfig import build_output, plain_output

import verifier
from contract import AnswerInput, Case, CaseInput, ResultOutput, Task
from plugin.read_case import read_case
from plugin.reference import reference
from plugin.write_result import write_result

ROOT = Path(__file__).parent


def setup_case(tmp_path, case="standard"):
    given = build_output({"case": case}, CaseInput)
    gold = json.loads((ROOT / "gold" / (case + ".json")).read_text())
    answer = build_output(gold, AnswerInput)
    made = build_output(plain_output(write_result(answer, tmp_path)), ResultOutput)
    pinned = reference(given, tmp_path)
    return given, answer, made, pinned


def judge(tmp_path, case="standard"):
    given, _answer, made, pinned = setup_case(tmp_path, case)
    return verifier.verify_task(Task.SOLVE.value, given, made, pinned, str(tmp_path))


@pytest.mark.parametrize("case", ["standard", "boundary"])
def test_correct_and_boundary(tmp_path, case):
    verdict = judge(tmp_path, case)
    assert verdict["valid"] and verdict["score"] == 1.0
    assert verdict == judge(tmp_path, case)


def test_every_tool_contract_and_verdict(tmp_path):
    given, answer, made, pinned = setup_case(tmp_path)
    for name, value, output in [
        ("read_case", given, read_case(given, tmp_path)),
        ("reference", given, pinned),
        ("write_result", answer, made),
    ]:
        assert verifier.verify_input(name, value)["valid"]
        assert verifier.verify_output(name, value, output, str(tmp_path))["valid"]


def test_missing_output(tmp_path):
    given, _answer, _made, pinned = setup_case(tmp_path)
    assert not verifier.verify_task(Task.SOLVE.value, given, None, pinned, str(tmp_path))["valid"]


def test_missing_reference(tmp_path):
    given, _answer, made, _pinned = setup_case(tmp_path)
    assert not verifier.verify_task(Task.SOLVE.value, given, made, None, str(tmp_path))["valid"]


def test_wrong_reference_case(tmp_path):
    given, _answer, made, pinned = setup_case(tmp_path)
    pinned = replace(pinned, case=Case.BOUNDARY)
    assert not verifier.verify_task(Task.SOLVE.value, given, made, pinned, str(tmp_path))["valid"]


@pytest.mark.parametrize(
    "content", ["not json", "[]", "null", '{"rows": "bad"}', '{"rows": []}', '{"rows": [{"invented": true}]}']
)
def test_malformed_and_wrong_file(tmp_path, content):
    given, _answer, made, pinned = setup_case(tmp_path)
    (tmp_path / "result.json").write_text(content)
    assert not verifier.verify_task(Task.SOLVE.value, given, made, pinned, str(tmp_path))["valid"]


def test_missing_file(tmp_path):
    given, _answer, made, pinned = setup_case(tmp_path)
    (tmp_path / "result.json").unlink()
    assert not verifier.verify_task(Task.SOLVE.value, given, made, pinned, str(tmp_path))["valid"]


@pytest.mark.parametrize("path", ["../result.json", "/tmp/result.json", "other.json"])
def test_refuses_other_paths(tmp_path, path):
    given, _answer, made, pinned = setup_case(tmp_path)
    assert not verifier.verify_task(Task.SOLVE.value, given, replace(made, path=path), pinned, str(tmp_path))["valid"]


def test_wrong_count(tmp_path):
    given, _answer, made, pinned = setup_case(tmp_path)
    assert not verifier.verify_task(
        Task.SOLVE.value, given, replace(made, count=made.count + 1), pinned, str(tmp_path)
    )["valid"]


def test_correct_count_wrong_decision(tmp_path):
    given, answer, made, pinned = setup_case(tmp_path)
    value = plain_output(answer)
    field = next(iter(value["rows"][0]))
    value["rows"][0][field] = "invented"
    (tmp_path / "result.json").write_text(json.dumps(value))
    verdict = verifier.verify_task(Task.SOLVE.value, given, made, pinned, str(tmp_path))
    assert not verdict["valid"] and verdict["score"] == 0


def test_duplicate_decision(tmp_path):
    given, answer, made, pinned = setup_case(tmp_path)
    value = plain_output(answer)
    value["rows"].append(value["rows"][0])
    (tmp_path / "result.json").write_text(json.dumps(value))
    assert not verifier.verify_task(
        Task.SOLVE.value, given, replace(made, count=made.count + 1), pinned, str(tmp_path)
    )["valid"]


def test_storage_verifier_detects_tampering(tmp_path):
    given, answer, made, pinned = setup_case(tmp_path)
    value = plain_output(answer)
    value["extra"] = "unrequested"
    (tmp_path / "result.json").write_text(json.dumps(value))
    assert not verifier.verify_output("write_result", answer, made, str(tmp_path))["valid"]
    assert not verifier.verify_task(Task.SOLVE.value, given, made, pinned, str(tmp_path))["valid"]


def test_symlink_refused(tmp_path):
    given, answer, made, pinned = setup_case(tmp_path)
    saved = tmp_path / "saved.json"
    (tmp_path / "result.json").rename(saved)
    (tmp_path / "result.json").symlink_to(saved)
    assert not verifier.verify_task(Task.SOLVE.value, given, made, pinned, str(tmp_path))["valid"]
    with pytest.raises(ValueError):
        write_result(answer, tmp_path)


@pytest.mark.parametrize("value", [{}, {"case": "invented"}, {"case": 3}])
def test_malformed_task_contract(value):
    with pytest.raises((ValueError, TypeError, KeyError)):
        build_output(value, CaseInput)


def test_boolean_is_not_integer():
    from verifier.checks import exact

    assert not exact({"value": True}, {"value": 1})
    assert not exact({"value": 1.0}, {"value": 1})


@pytest.mark.parametrize(
    "content", ['{"rows":[],"rows":[]}', '{"rows":[],"value":NaN}', '{"rows":[],"value":Infinity}']
)
def test_nonstandard_json_is_refused(tmp_path, content):
    given, _answer, made, pinned = setup_case(tmp_path)
    (tmp_path / "result.json").write_text(content)
    verdict = verifier.verify_task(Task.SOLVE.value, given, made, pinned, str(tmp_path))
    assert verdict["valid"] is False and verdict["score"] == 0
