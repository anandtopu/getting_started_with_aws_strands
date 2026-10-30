"""Acceptance checks for edited starters or solutions."""

import pytest

from common.exercise_support import exercise_cases, load_exercise


@pytest.mark.parametrize("filename,value,expected", exercise_cases("bonus/B3_self_extending"))
def test_exercise(filename, value, expected, request):
    folder = "exercises" if request.config.getoption("--exercise-starters") else "solutions"
    assert load_exercise("bonus/B3_self_extending", folder, filename).solve(value) == expected
