"""Pure helpers for typed values and exact artifact comparison."""

import json
from dataclasses import asdict, is_dataclass
from enum import Enum
from pathlib import Path


def plain(value):
    if is_dataclass(value):
        return plain(asdict(value))
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {key: plain(item) for key, item in value.items()}
    if isinstance(value, list):
        return [plain(item) for item in value]
    return value


def exact(left, right):
    # Unlike Python equality, distinguish true from 1 and 1 from 1.0.
    return json.dumps(plain(left), sort_keys=True, allow_nan=False) == json.dumps(
        plain(right), sort_keys=True, allow_nan=False
    )


def result(valid, message, **details):
    return {"valid": valid, "score": 1.0 if valid else 0.0, "message": message, "details": details}


def artifact(output, workspace):
    if output is None or output.path != "result.json":
        return None, "output must name result.json"
    path = Path(workspace) / "result.json"
    if path.is_symlink() or not path.is_file():
        return None, "result.json is missing or a symlink"
    try:
        value = json.loads(
            path.read_text(encoding="utf-8"), object_pairs_hook=unique_keys, parse_constant=reject_constant
        )
    except (ValueError, OSError):
        return None, "result.json is malformed or unreadable"
    if not isinstance(value, dict) or not isinstance(value.get("rows"), list):
        return None, "result.json must contain rows"
    if type(output.count) is not int or output.count != len(value["rows"]):
        return None, "submitted count differs from stored row count"
    return value, None


def unique_keys(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("duplicate JSON property")
        value[key] = item
    return value


def reject_constant(value):
    raise ValueError("non-finite JSON constant")
