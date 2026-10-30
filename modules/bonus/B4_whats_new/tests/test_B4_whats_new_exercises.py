"""Acceptance checks for edited starters or solutions."""

import pytest

from common.exercise_support import exercise_cases, load_exercise


@pytest.mark.parametrize("filename,value,expected", exercise_cases("bonus/B4_whats_new"))
def test_exercise(filename, value, expected, request):
    folder = "exercises" if request.config.getoption("--exercise-starters") else "solutions"
    assert load_exercise("bonus/B4_whats_new", folder, filename).solve(value) == expected
