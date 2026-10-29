"""Acceptance cases for learner edits or reference solutions."""

import pytest

from common.exercise_support import exercise_cases, load_exercise


@pytest.mark.parametrize("filename,value,expected", exercise_cases("16_swarms"))
def test_exercise(filename, value, expected, request):
    folder = "exercises" if request.config.getoption("--exercise-starters") else "solutions"
    assert load_exercise("16_swarms", folder, filename).solve(value) == expected
