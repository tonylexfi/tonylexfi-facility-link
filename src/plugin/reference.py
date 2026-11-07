"""Pin the immutable case before the model starts; not exposed to the agent."""

from pathlib import Path

from contract import CaseInput, ReferenceOutput

from .read_case import read_case


def reference(value: CaseInput, workspace: Path) -> ReferenceOutput:
    return ReferenceOutput(case=value.case, data=read_case(value, workspace))
