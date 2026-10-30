"""Readable output with honest token-cost estimates and safe error messages."""

import sys
from collections.abc import Callable
from typing import Any

from rich.console import Console
from rich.table import Table

from common.config import CourseError, Settings

console = Console(highlight=False)


def estimate_cost(usage: dict[str, int], settings: Settings) -> float | None:
    if settings.provider == "mock" or settings.provider == "ollama":
        return 0.0
    if settings.input_price is None or settings.output_price is None:
        return None
    return (
        usage.get("inputTokens", 0) * settings.input_price
        + usage.get("outputTokens", 0) * settings.output_price
    ) / 1_000_000


def print_event(**event: Any) -> None:
    """Show text and tool names; never echo raw tool inputs or hidden reasoning."""
    if event.get("data"):
        console.print(str(event["data"]), end="", markup=False)
    call = event.get("current_tool_use")
    if call and call.get("name") and not call.get("input"):
        console.print(f"\nTool: {call['name']}", markup=False)


def print_result(result: Any, settings: Settings) -> None:
    console.print(str(result), markup=False)
    usage = result.metrics.accumulated_usage
    table = Table("Metric", "Value")
    for name in ("inputTokens", "outputTokens", "totalTokens"):
        table.add_row(name, str(usage.get(name, 0)))
    table.add_row("cycles", str(result.metrics.cycle_count))
    table.add_row("cycle time (seconds)", f"{sum(result.metrics.cycle_durations):.3f}")
    cost = estimate_cost(usage, settings)
    label = "unknown; configure dated prices" if cost is None else f"${cost:.6f}"
    table.add_row("inference estimate", label)
    console.print(table)
    if settings.provider == "mock":
        console.print("Scripted usage for testing; not measured model billing.")


def friendly_error(exc: Exception) -> str:
    if isinstance(exc, CourseError):
        return str(exc)
    response = getattr(exc, "response", {})
    code = response.get("Error", {}).get("Code", "") if isinstance(response, dict) else ""
    name = type(exc).__name__
    if code in {"AccessDeniedException", "UnauthorizedException"}:
        return "Access denied. Check model access, inference-profile permissions and AWS_REGION."
    if code in {"ExpiredTokenException", "ExpiredToken"} or "SSO" in name:
        return "Your SSO session needs renewal. Run aws sso login with your named profile."
    if code == "ValidationException":
        return "Check MODEL_ID, its inference profile, region and supported model parameters."
    if code == "ThrottlingException":
        return "The provider throttled the request. Wait, then retry with less concurrency."
    if name in {"ProfileNotFound", "NoCredentialsError", "PartialCredentialsError"}:
        return "Configure your named AWS SSO profile, then sign in with aws sso login."
    if isinstance(exc, (ConnectionError, OSError)) or "Connect" in name:
        return "Cannot connect. Check the service address; for Ollama, start its local service."
    return f"The request failed ({name}). Check provider settings and the troubleshooting guide."


def run_cli(main: Callable[[], int | None]) -> None:
    """Keep expected provider failures readable without printing credentials."""
    # Real model text may contain emoji even when a redirected Windows stream uses cp1252.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="backslashreplace")
    try:
        status = main()
    except KeyboardInterrupt:
        console.print("Cancelled.")
        raise SystemExit(130) from None
    except Exception as exc:
        console.print(friendly_error(exc), style="red", markup=False)
        console.print("Run: uv run python scripts/check_env.py")
        raise SystemExit(1) from None
    raise SystemExit(status or 0)
