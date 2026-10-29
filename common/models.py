"""Construct every course model in one place, with optional providers loaded lazily."""

import os
from collections.abc import Sequence
from typing import Any

from strands.models import Model

from common.config import CourseError, Settings, load_settings


def get_model(
    settings: Settings | None = None,
    *,
    provider: str | None = None,
    responses: Sequence[dict[str, Any] | str | Exception] | None = None,
) -> Model:
    cfg = settings or load_settings(provider=provider)
    if provider and settings and provider != settings.provider:
        raise ValueError("Pass settings or a provider override, not conflicting selections.")
    if cfg.provider == "mock":
        from common.testing import ScriptedModel

        if responses is None:
            raise ValueError("Mock models require an explicit response script.")
        return ScriptedModel(responses)
    try:
        if cfg.provider == "bedrock":
            import boto3
            from botocore.config import Config
            from strands.models import BedrockModel

            session = boto3.Session(
                profile_name=cfg.aws_profile or None, region_name=cfg.aws_region
            )
            return BedrockModel(
                boto_session=session,
                model_id=cfg.model_id,
                temperature=cfg.temperature,
                max_tokens=cfg.max_tokens,
                boto_client_config=Config(
                    connect_timeout=10,
                    read_timeout=90,
                    retries={"max_attempts": 2, "mode": "standard"},
                ),
            )
        if cfg.provider == "ollama":
            from strands.models.ollama import OllamaModel

            return OllamaModel(
                host=cfg.ollama_host,
                model_id=cfg.model_id,
                temperature=cfg.temperature,
                max_tokens=cfg.max_tokens,
                ollama_client_args={"timeout": 120},
            )
        if cfg.provider == "anthropic":
            from strands.models.anthropic import AnthropicModel

            if not cfg.anthropic_key:
                raise CourseError("Set ANTHROPIC_API_KEY or select Ollama for the free local path.")
            return AnthropicModel(
                model_id=cfg.model_id,
                max_tokens=cfg.max_tokens,
                client_args={"api_key": cfg.anthropic_key, "timeout": 90, "max_retries": 2},
                # Adaptive-reasoning models may reject temperature; do not force it globally.
            )
        if cfg.provider == "openai":
            from strands.models.openai import OpenAIModel

            if not cfg.openai_key:
                raise CourseError("Set OPENAI_API_KEY or select Ollama for the free local path.")
            params: dict[str, Any] = {"max_completion_tokens": cfg.max_tokens}
            if cfg.model_id.startswith("gpt-6"):
                # GPT-6 Chat Completions tool calls require reasoning_effort=none.
                params["reasoning_effort"] = "none"
            else:
                params["temperature"] = cfg.temperature
            return OpenAIModel(
                model_id=cfg.model_id,
                params=params,
                client_args={"api_key": cfg.openai_key, "timeout": 90, "max_retries": 2},
            )
        if cfg.provider == "litellm":
            # LiteLLM otherwise downloads a price map at import time, including in tests.
            os.environ.setdefault("LITELLM_LOCAL_MODEL_COST_MAP", "True")
            from strands.models.litellm import LiteLLMModel

            args: dict[str, Any] = {"timeout": 120}
            if cfg.model_id.startswith(("ollama/", "ollama_chat/")):
                args["api_base"] = cfg.ollama_host
            elif cfg.litellm_key:
                args["api_key"] = cfg.litellm_key
            else:
                raise CourseError("Remote LiteLLM needs LITELLM_API_KEY; default routing is local.")
            return LiteLLMModel(
                model_id=cfg.model_id,
                client_args=args,
                params={"temperature": cfg.temperature, "max_tokens": cfg.max_tokens},
            )
    except ImportError as exc:
        raise CourseError("Missing provider dependency. Run uv sync --group providers.") from exc
    raise CourseError(f"Unsupported provider: {cfg.provider}")
