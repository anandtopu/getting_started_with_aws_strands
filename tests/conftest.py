"""Keep normal tests independent of accounts, real keys and external services."""

import os

import pytest

from common.network import offline_network

# Set before SDK/provider imports; no fallback credential lookup or remote telemetry.
os.environ["AWS_EC2_METADATA_DISABLED"] = "true"
os.environ["OTEL_SDK_DISABLED"] = "true"
os.environ["LITELLM_LOCAL_MODEL_COST_MAP"] = "True"
os.environ["ANONYMIZED_TELEMETRY"] = "False"


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--live", action="store_true", help="Explicitly enable billable integration tests"
    )


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    if not config.getoption("--live"):
        for item in items:
            if "live" in item.keywords:
                item.add_marker(pytest.mark.skip(reason="Real services require explicit --live"))


@pytest.fixture(autouse=True)
def isolated_environment(monkeypatch: pytest.MonkeyPatch, tmp_path, request):
    if request.node.get_closest_marker("live") and request.config.getoption("--live"):
        yield
        return
    for key in (
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
        "AWS_SESSION_TOKEN",
        "AWS_PROFILE",
        "ANTHROPIC_API_KEY",
        "OPENAI_API_KEY",
        "LITELLM_API_KEY",
        "BEDROCK_API_KEY",
    ):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("AWS_CONFIG_FILE", str(tmp_path / "no-config"))
    monkeypatch.setenv("AWS_SHARED_CREDENTIALS_FILE", str(tmp_path / "no-credentials"))
    monkeypatch.setenv("BYPASS_TOOL_CONSENT", "false")
    with offline_network():
        yield
