"""Configuration checks never require an account or a running model."""

import pytest

from common.config import CourseError, load_settings


def test_provider_switch_and_invalid_setup(tmp_path):
    path = tmp_path / ".env"
    path.write_text("MODEL_PROVIDER=ollama\nMODEL_ID=\n", encoding="utf-8")
    assert load_settings(path, environ={}).provider == "ollama"
    with pytest.raises(CourseError, match="Invalid configuration"):
        load_settings(path, environ={"MODEL_MAX_TOKENS": "-1"})
