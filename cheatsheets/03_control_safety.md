# Tier 3 | Control and safety

Modules 10-14. [Printable PDF](../output/pdf/03_control_safety.pdf).

## Mental model

The host owns permissions, deadlines and approvals. The model proposes actions. Guardrails filter content; they do not replace identity or business rules.

## Streaming and async

Use stream_async for incremental events and invoke_async for a result. Await I/O; bound concurrency. In notebooks use await instead of nested asyncio.run.

## Hooks and interrupts

Hooks observe or enforce lifecycle checks. Interrupts return control for a human decision. Resume only after the host validates the decision and its caller.

## Approval checklist

Bind approval to user, action, amount and request ID. Reject stale or mismatched decisions. Use an idempotency key so retries cannot pay twice.

## MCP lifecycle

Start client -> discover allowed tools -> invoke agent inside context -> close client. Validate schemas, credentials and transport. Server descriptions are untrusted input.

## Prompt injection

Separate retrieved content from instructions. Restrict tool capabilities, validate output, redact telemetry, and test malicious documents. Do not rely only on a prompt.

## Useful commands

uv run pytest -q tests/test_tier3_boundaries.py
uv run python scripts/find_leftovers.py --regions us-east-1

## Checkpoint

Demonstrate approval denial and safe retry, authenticated local MCP, and a failed injection attempt. Stop local servers and delete optional Guardrail resources.

See [the feature map](../docs/FEATURE_MAP.md) for source examples and [costs](../docs/COSTS.md) for live pricing.
