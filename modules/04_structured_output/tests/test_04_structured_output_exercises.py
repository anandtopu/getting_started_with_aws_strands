"""Exercise acceptance tests; --exercise-starters checks the learner's edits."""

import pytest

from common.exercise_support import exercise_cases, load_exercise


@pytest.mark.parametrize("filename,value,expected", exercise_cases("04_structured_output"))
def test_exercise(filename, value, expected, request):
    folder = "exercises" if request.config.getoption("--exercise-starters") else "solutions"
    module = load_exercise("04_structured_output", folder, filename)
    assert module.solve(value) == expected
