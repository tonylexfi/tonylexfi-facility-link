from .checks import result


def verify_input(value):
    return result(value.case.value in ("standard", "boundary"), "case selector checked")


def verify_output(given, made, workspace):
    return result(given.case == made.case, "case identity checked")
