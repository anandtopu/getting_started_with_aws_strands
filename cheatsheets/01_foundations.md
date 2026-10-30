# Tier 1 | Foundations

Modules 00-06. [Printable PDF](../output/pdf/01_foundations.pdf).

## Mental model

Agent = model + instructions + explicit tools. The SDK loops: model request, tool use, tool result, next model request, final response.

## First offline run

uv sync
uv run python modules/01_first_agent/examples/01_hello_agent.py --mock

## Choose a provider

Use common.models.get_model(). Set MODEL_PROVIDER in .env. Ollama runs locally; Bedrock uses your named SSO profile. Never save AWS keys in .env.

## Read the result

AgentResult exposes message, stop_reason and metrics. Inspect input/output tokens before estimating cost. Mock tokens do not predict real usage.

## Tools and schemas

Define a small typed function with @tool. Validate runtime arguments and structured output. Use integer cents. A model request is not authorization.

## Conversation

Messages hold text, toolUse and toolResult blocks. Keep related tool blocks together. Trim or summarize with a conversation manager before context grows too large.

## Before a live call

SSO login; budget alert; supported model and region; explicit output-token limit. Keep risky-tool consent enabled. No infrastructure deployment is needed.

## Checkpoint

Explain one complete tool cycle. Show a bad input rejected by validation. Compare two providers without changing business logic.

See [the feature map](../docs/FEATURE_MAP.md) for source examples and [costs](../docs/COSTS.md) for live pricing.
