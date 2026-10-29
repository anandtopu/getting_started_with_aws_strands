"""Build it yourself: Model interface with scripted text and tool events.

Run: uv run python modules/02_model_providers/examples/04_custom_model.py --mock
Expected: Lesson complete.
Cost: mock/local $0 hosted inference; live hosted calls use tokens.
AWS required: No. Resources created: none.
"""

from strands import Agent
from strands.models import Model

from common.lessons import complete, lesson_settings
from common.pretty import console, run_cli


class OneSentenceModel(Model):
    """Build it yourself: one fixed response, with a complete streaming contract."""

    def __init__(self) -> None:
        self.config = {"model_id": "nimbus-one-sentence", "temperature": 0}

    def get_config(self) -> dict:
        return dict(self.config)

    def update_config(self, **settings) -> None:
        self.config.update(settings)

    async def stream(self, messages, tool_specs=None, system_prompt=None, **kwargs):
        # KEY IDEA: adapters translate provider output into SDK events, not an AgentResult.
        yield {"messageStart": {"role": "assistant"}}
        yield {"contentBlockStart": {"start": {}}}
        yield {"contentBlockDelta": {"delta": {"text": "Nimbus asks for your destination."}}}
        yield {"contentBlockStop": {}}
        yield {"messageStop": {"stopReason": "end_turn"}}
        yield {
            "metadata": {
                "usage": {"inputTokens": 10, "outputTokens": 7, "totalTokens": 17},
                "metrics": {"latencyMs": 0},
            }
        }

    async def structured_output(self, output_model, prompt, system_prompt=None, **kwargs):
        # This adapter deliberately supports text only; reject unsupported use clearly.
        raise ValueError("OneSentenceModel does not support structured output")
        yield  # pragma: no cover -- abstract interface requires an async generator


def main() -> None:
    _, cfg = lesson_settings()
    model = OneSentenceModel()  # Module 02's deliberate model-factory exception.
    agent = Agent(model=model, callback_handler=None, retry_strategy=None)
    complete(agent("Start a Nimbus conversation."), cfg.model_copy(update={"provider": "mock"}))
    console.print("Next read common/testing.py: it adds toolUse events and explicit exhaustion.")


if __name__ == "__main__":
    run_cli(main)
