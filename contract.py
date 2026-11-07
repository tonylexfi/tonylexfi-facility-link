"""Typed declarations for the task and every tool."""

from dataclasses import dataclass
from enum import Enum
from typing import Annotated

from slimconfig import Output


class Case(Enum):
    STANDARD = "standard"
    BOUNDARY = "boundary"


class Tool(Enum):
    READ_CASE = "read_case"
    WRITE_RESULT = "write_result"
    REFERENCE = "reference"


class Task(Enum):
    SOLVE = "tonylexfi-facility-link"


class Method(Enum):
    SITE_KEY = "site_key"
    COMPOSITE = "composite"
    AMBIGUOUS = "ambiguous"
    UNMATCHED = "unmatched"


@dataclass
class Facility(Output):
    id: Annotated[str, "Record identifier"]
    site_key: Annotated[str, "Publisher facility id, empty when absent"]
    name_key: Annotated[str, "Prepared exact name key"]
    address_key: Annotated[str, "Prepared exact address key"]
    zip_code: Annotated[str, "Prepared postal string; retain leading zeros"]


@dataclass
class CaseInput(Output):
    case: Annotated[Case, "Which reproducible fixture case to solve"]


@dataclass
class DataOutput(Output):
    case: Annotated[Case, "Case identity"]
    registry: Annotated[list[Facility], "Canonical facility records"]
    incoming: Annotated[list[Facility], "Incoming records with prepared keys"]


@dataclass
class AnswerRow(Output):
    record_id: Annotated[str, "Incoming record identifier"]
    facility_id: Annotated[str | None, "Unique canonical id, otherwise null"]
    method: Annotated[Method, "How the match or abstention was decided"]


@dataclass
class AnswerInput(Output):
    rows: Annotated[list[AnswerRow], "Complete answer rows in the required canonical order"]


@dataclass
class ResultOutput(Output):
    path: Annotated[str, "Must be result.json in the workspace"]
    count: Annotated[int, "Number of answer rows written"]


@dataclass
class ReferenceOutput(Output):
    case: Annotated[Case, "Pinned case identity"]
    data: Annotated[DataOutput, "Immutable ground-truth case snapshot"]


TOOLS = {
    Tool.READ_CASE: (CaseInput, DataOutput),
    Tool.WRITE_RESULT: (AnswerInput, ResultOutput),
    Tool.REFERENCE: (CaseInput, ReferenceOutput),
}
TASKS = {Task.SOLVE: (CaseInput, ResultOutput)}
