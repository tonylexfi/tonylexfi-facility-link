from .checks import artifact, exact, result


def verify_input(value):
    return result(True, "typed answer accepted for storage; correctness is checked at task end")


def verify_output(given, made, workspace):
    stored, error = artifact(made, workspace)
    if error:
        return result(False, error)
    return result(exact(stored, given), "stored answer matches tool input")
