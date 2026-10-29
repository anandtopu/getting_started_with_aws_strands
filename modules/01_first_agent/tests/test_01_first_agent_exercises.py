"""Exercise acceptance tests; --exercise-starters checks the learner's edits."""

import pytest

from common.exercise_support import exercise_cases, load_exercise


@pytest.mark.parametrize("filename,value,expected", exercise_cases("01_first_agent"))
def test_exercise(filename, value, expected, request):
    folder = "exercises" if request.config.getoption("--exercise-starters") else "solutions"
    module = load_exercise("01_first_agent", folder, filename)
    assert module.solve(value) == expected
