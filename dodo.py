code = "streamcontrol dodo.py"
tests = "tests"


def _build_action(actions, verbosity=2):
    return {"verbosity": verbosity, "actions": actions}


def task_black():
    return _build_action([f"black {code} {tests}"])


def task_bandit():
    return _build_action([f"bandit -r {code}"])


def task_pyproject_lint():
    return _build_action(["poetry check"])


def task_flake8():
    # line length of 88 to match black
    return _build_action(
        [
            (
                "flake8"
                " --max-line-length=88"
                " --count"
                " --statistics"
                f" {code} {tests}"
            )
        ]
    )


def task_isort():
    return _build_action([f"isort {code} {tests}"])
