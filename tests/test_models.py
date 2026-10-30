"""Verify actual SDK model/tool/structured-output behavior without a network."""

import asyncio
import os
import subprocess
import sys

import pytest
from pydantic import BaseModel, Field
from strands import Agent, tool

from common.config import CourseError, Settings, load_settings
from common.models import get_model
from common.pretty import estimate_cost
from common.testing import ScriptedModel, tool_message


def test_one_line_provider_switch(tmp_path):
    env = tmp_path / ".env"
    env.write_text("MODEL_PROVIDER=ollama\nMODEL_ID=\n", encoding="utf-8")
    cfg = load_settings(env, environ={})
    assert cfg.provider == "ollama" and cfg.model_id.startswith("qwen")
    assert load_settings(env, environ={"MODEL_ID": "my-model"}).model_id == "my-model"


@pytest.mark.parametrize("value,expected", [("false", False), ("true", True)])
def test_ollama_thinking_reaches_request(tmp_path, value, expected):
    env = tmp_path / ".env"
    env.write_text("MODEL_PROVIDER=ollama\n", encoding="utf-8")
    cfg = load_settings(env, environ={"OLLAMA_THINK": value})
    model = get_model(cfg)
    assert model.get_config()["additional_args"] == {"think": expected}
    assert model.get_config()["max_tokens"] == 512


def test_ollama_default_preserves_short_lesson_budget(tmp_path):
    cfg = load_settings(tmp_path / "absent.env", environ={}, provider="ollama")
    assert cfg.ollama_think is False
    with pytest.raises(CourseError, match="ollama_think"):
        load_settings(tmp_path / "absent.env", environ={"OLLAMA_THINK": "maybe"})


def test_cli_handles_unicode_on_a_legacy_redirected_stream():
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "from common.pretty import run_cli; run_cli(lambda: print(chr(0x1F60A)))",
        ],
        env={**os.environ, "PYTHONIOENCODING": "ascii:strict"},
        capture_output=True,
        timeout=15,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert b"\\U0001f60a" in result.stdout


@pytest.mark.parametrize(
    "setting", ["BYPASS_TOOL_CONSENT=true", "AWS_ACCESS_KEY_ID=not-a-real-key"]
)
def test_reject_unsafe_dotenv(tmp_path, setting):
    env = tmp_path / ".env"
    env.write_text(setting, encoding="utf-8")
    with pytest.raises(CourseError):
        load_settings(env, environ={})


def test_scripted_model_runs_real_tool_and_returns_metrics():
    calls = []

    @tool
    def lookup_booking(booking_id: str) -> str:
        """Find a synthetic booking by its booking_id."""
        calls.append(booking_id)
        return "confirmed"

    model = get_model(
        provider="mock",
        responses=[tool_message("lookup_booking", {"booking_id": "BKG-0001"}), "Confirmed."],
    )
    result = Agent(model=model, tools=[lookup_booking], callback_handler=None)("Find my booking.")
    assert calls == ["BKG-0001"] and str(result).strip() == "Confirmed."
    assert result.stop_reason == "end_turn"
    assert result.metrics.accumulated_usage["inputTokens"] == 200
    assert model.requests[1]["messages"][-1]["content"][0]["toolResult"]["status"] == "success"


def test_structured_output_validation_retry():
    class Quote(BaseModel):
        price: int = Field(gt=0)

    model = get_model(
        provider="mock",
        responses=[
            tool_message("Quote", {"price": -1}, "bad"),
            tool_message("Quote", {"price": 75}, "good"),
        ],
    )
    result = Agent(model=model, structured_output_model=Quote, callback_handler=None)(
        "Quote a change."
    )
    assert result.structured_output.price == 75
    assert model.index == 2


@pytest.mark.parametrize("price", [75, -1])
def test_ollama_forced_schema_retry_keeps_validation_and_usage(monkeypatch, price):
    import ollama
    from strands.types.exceptions import StructuredOutputException

    class Quote(BaseModel):
        price: int = Field(gt=0)

    requests = []

    async def chat(self, **request):
        requests.append(request)

        async def chunks():
            yield ollama.ChatResponse(
                message=ollama.Message(
                    role="assistant",
                    content=(f'{{"price":{price}}}' if "format" in request else "Quote(price=75)"),
                ),
                done=True,
                done_reason="stop",
                prompt_eval_count=10,
                eval_count=5,
                total_duration=1000000,
            )

        return chunks()

    monkeypatch.setattr(ollama.AsyncClient, "chat", chat)
    model = get_model(Settings(provider="ollama", model_id="local-test"), output_schema=Quote)
    agent = Agent(model=model, structured_output_model=Quote, callback_handler=None)
    if price < 0:
        with pytest.raises(StructuredOutputException):
            agent("Quote")
    else:
        result = agent("Quote")
        assert result.structured_output.price == 75
        assert result.metrics.accumulated_usage["totalTokens"] == 30
    assert "format" not in requests[0] and requests[0]["tools"]
    assert requests[1]["format"] == Quote.model_json_schema()
    assert requests[1]["tools"] == []
    assert requests[1]["options"]["num_predict"] == 512
    assert "format" not in model.get_config()["additional_args"]


def test_streamed_text_and_config_copy():
    model = ScriptedModel(["Hello Nimbus"])
    config = model.get_config()
    config["temperature"] = 9
    assert model.get_config()["temperature"] == 0

    async def run():
        return [e async for e in Agent(model=model, callback_handler=None).stream_async("Hello")]

    events = asyncio.run(run())
    assert any(e.get("data") == "Hello Nimbus" for e in events)


def test_exhaustion_and_tool_error_are_visible():
    @tool
    def unavailable_booking() -> str:
        """Demonstrate a rejected booking lookup."""
        raise ValueError("Unknown synthetic booking")

    model = ScriptedModel([tool_message("unavailable_booking", {}), "Please check the booking ID."])
    Agent(model=model, tools=[unavailable_booking], callback_handler=None)("Find booking.")
    assert model.requests[1]["messages"][-1]["content"][0]["toolResult"]["status"] == "error"
    with pytest.raises(AssertionError, match="exhausted"):
        model._next()


def test_cost_unknown_is_not_zero():
    usage = {"inputTokens": 1000, "outputTokens": 100}
    assert estimate_cost(usage, Settings(provider="bedrock")) is None
    assert estimate_cost(usage, Settings(provider="ollama")) == 0
    assert estimate_cost(usage, Settings(input_price=1, output_price=5)) == pytest.approx(0.0015)


def test_bedrock_constructor_contract(monkeypatch):
    import boto3

    session = boto3.Session(
        aws_access_key_id="testing", aws_secret_access_key="testing", region_name="us-east-1"
    )
    monkeypatch.setattr(boto3, "Session", lambda **kwargs: session)
    model = get_model(Settings(provider="bedrock", model_id="course-fixture"))
    assert model.get_config()["model_id"] == "course-fixture"


@pytest.mark.parametrize(
    "provider,module",
    [
        ("ollama", "ollama"),
        ("anthropic", "anthropic"),
        ("openai", "openai"),
        ("litellm", "litellm"),
    ],
)
def test_optional_provider_constructor_contract(provider, module):
    pytest.importorskip(module, reason="Install --group providers for this adapter check")
    model_id = "ollama_chat/course-fixture" if provider == "litellm" else "course-fixture"
    cfg = Settings(
        provider=provider, model_id=model_id, anthropic_key="testing", openai_key="testing"
    )
    assert get_model(cfg).get_config()["model_id"] == model_id
