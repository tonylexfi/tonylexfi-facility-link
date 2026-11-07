"""Read the fixed, synthetic case. No network or live-provider claim."""

import json
from pathlib import Path

from slimconfig import build_output

from contract import CaseInput, DataOutput


def read_case(value: CaseInput, workspace: Path) -> DataOutput:
    path = Path(__file__).parent / "fixtures" / (value.case.value + ".json")
    return build_output(json.loads(path.read_text(encoding="utf-8")), DataOutput)
