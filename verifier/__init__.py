from contract import Task, Tool

from . import read_case, reference, write_result
from .checks import artifact, exact, result
from .rules import expected

TOOLS = {Tool.READ_CASE: read_case, Tool.WRITE_RESULT: write_result, Tool.REFERENCE: reference}


def verify_input(tool, value):
    return TOOLS[Tool(tool)].verify_input(value)


def verify_output(tool, input_value, output_value, workspace):
    return TOOLS[Tool(tool)].verify_output(input_value, output_value, workspace)


def verify_task(task, arguments, output, reference, workspace):
    if task != Task.SOLVE.value:
        return result(False, "unknown task")
    if reference is None or reference.case != arguments.case or reference.data.case != arguments.case:
        return result(False, "missing or mismatched pinned reference")
    stored, error = artifact(output, workspace)
    if error:
        return result(False, error)
    wanted = expected(reference.data)
    valid = exact(stored, wanted)
    return result(
        valid,
        "all decisions and totals match" if valid else "answer differs from deterministic ground truth",
        expected=wanted,
        actual=stored,
    )
