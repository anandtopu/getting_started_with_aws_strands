"""Acceptance cases for the edited starter or reference solution."""

import pytest

from common.exercise_support import exercise_cases, load_exercise


@pytest.mark.parametrize("filename,value,expected", exercise_cases("14_mcp"))
def test_exercise(filename, value, expected, request):
    folder = "exercises" if request.config.getoption("--exercise-starters") else "solutions"
    assert load_exercise("14_mcp", folder, filename).solve(value) == expected
