"""Load explicit course settings without changing process environment variables."""

import os
from pathlib import Path
from typing import Literal

from dotenv import dotenv_values
from pydantic import BaseModel, ConfigDict, Field, ValidationError

ROOT = Path(__file__).resolve().parents[1]
Provider = Literal["bedrock", "anthropic", "openai", "ollama", "litellm", "mock"]


def course_value(name: str) -> str:
    """Read a non-secret optional lesson setting using the same explicit precedence."""
    values = {
        **dotenv_values(ROOT / ".env.example", interpolate=False),
        **dotenv_values(ROOT / ".env", interpolate=False),
        **os.environ,
    }
    return values.get(name) or ""


class CourseError(RuntimeError):
    """A recoverable setup problem suitable for a beginner-facing message."""


class Settings(BaseModel):
    """Only recognized settings are retained; secrets are excluded from repr."""

    model_config = ConfigDict(frozen=True)
    provider: Provider = "bedrock"
    model_id: str = ""
    aws_region: str = "us-east-1"
    aws_profile: str = ""
    ollama_host: str = "http://localhost:11434"
    max_tokens: int = Field(default=512, ge=1, le=32768)
    temperature: float = Field(default=0, ge=0, le=2)
    anthropic_key: str = Field(default="", repr=False)
    openai_key: str = Field(default="", repr=False)
    litellm_key: str = Field(default="", repr=False)
    input_price: float | None = Field(default=None, ge=0)
    output_price: float | None = Field(default=None, ge=0)


def load_settings(
    env_file: Path | None = None,
    *,
    environ: dict[str, str] | None = None,
    provider: str | None = None,
) -> Settings:
    """Precedence: process > .env > public example; explicit provider wins."""
    values = {
        **dotenv_values(ROOT / ".env.example", interpolate=False),
        **dotenv_values(env_file or ROOT / ".env", interpolate=False),
        **(os.environ if environ is None else environ),
    }
    selected = (provider or values.get("MODEL_PROVIDER") or "bedrock").lower()
    if str(values.get("BYPASS_TOOL_CONSENT", "false")).lower() not in {"", "false", "0", "no"}:
        raise CourseError("Unset BYPASS_TOOL_CONSENT: course tools require human consent.")
    # Environment credentials are legitimate in CI/roles; reject secrets stored in .env.
    file_values = dotenv_values(env_file or ROOT / ".env", interpolate=False)
    if any(
        file_values.get(key)
        for key in ("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN")
    ):
        raise CourseError("Remove AWS credentials from .env. Use an SSO profile instead.")
    try:
        result = Settings(
            provider=selected,
            model_id=values.get("MODEL_ID") or values.get(f"{selected.upper()}_MODEL_ID") or "",
            aws_region=values.get("AWS_REGION") or "us-east-1",
            aws_profile=values.get("AWS_PROFILE") or "",
            ollama_host=values.get("OLLAMA_HOST") or "http://localhost:11434",
            max_tokens=values.get("MODEL_MAX_TOKENS") or 512,
            temperature=values.get("MODEL_TEMPERATURE") or 0,
            anthropic_key=values.get("ANTHROPIC_API_KEY") or "",
            openai_key=values.get("OPENAI_API_KEY") or "",
            litellm_key=values.get("LITELLM_API_KEY") or "",
            input_price=values.get("MODEL_INPUT_USD_PER_MILLION") or None,
            output_price=values.get("MODEL_OUTPUT_USD_PER_MILLION") or None,
        )
    except ValidationError as exc:
        fields = ", ".join(str(e["loc"][0]) for e in exc.errors())
        raise CourseError(f"Invalid configuration fields: {fields}. Check .env.example.") from exc
    if result.provider != "mock" and not result.model_id:
        raise CourseError("Set MODEL_ID or your provider's model ID in .env.")
    return result
