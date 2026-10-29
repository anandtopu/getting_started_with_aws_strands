"""Scripted Model events for offline tests, based on the upstream fixture pattern.

Unlike a replacement Agent, this provider exercises the real Strands loop.
See THIRD_PARTY_NOTICES.md for the upstream source and attribution.
"""

import json
from collections.abc import AsyncGenerator, Sequence
from copy import deepcopy
from typing import Any

from pydantic import BaseModel
from strands.models import Model


def text_message(text: str) -> dict[str, Any]:
    return {"role": "assistant", "content": [{"text": text}]}


def tool_message(name: str, inputs: dict[str, Any], call_id: str = "call-1") -> dict[str, Any]:
    return {
        "role": "assistant",
        "content": [{"toolUse": {"name": name, "input": inputs, "toolUseId": call_id}}],
    }


class ScriptedModel(Model):
    """Replay complete assistant messages; fail loudly if the script is exhausted."""

    def __init__(
        self,
        responses: Sequence[dict[str, Any] | str | Exception],
        *,
        input_tokens: int = 100,
        output_tokens: int = 20,
    ) -> None:
        self.responses = [text_message(x) if isinstance(x, str) else deepcopy(x) for x in responses]
        self.requests: list[dict[str, Any]] = []
        self.index = 0
        self.config: dict[str, Any] = {"model_id": "scripted", "temperature": 0}
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens

    def get_config(self) -> dict[str, Any]:
        return deepcopy(self.config)

    def update_config(self, **model_config: Any) -> None:
        self.config.update(model_config)

    def _next(self) -> dict[str, Any]:
        if self.index >= len(self.responses):
            raise AssertionError("ScriptedModel exhausted: supply another expected model response.")
        response = self.responses[self.index]
        self.index += 1
        if isinstance(response, Exception):
            raise response
        return deepcopy(response)

    async def stream(
        self,
        messages: list[dict[str, Any]],
        tool_specs: list[dict[str, Any]] | None = None,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> AsyncGenerator[dict[str, Any], None]:
        self.requests.append(
            deepcopy(
                {"messages": messages, "tool_specs": tool_specs, "system_prompt": system_prompt}
            )
        )
        signal = kwargs.get("cancel_signal")
        if signal is not None and signal.is_set():
            return
        response = self._next()
        yield {"messageStart": {"role": "assistant"}}
        stop_reason = "end_turn"
        for block in response["content"]:
            if "toolUse" in block:
                call = block["toolUse"]
                stop_reason = "tool_use"
                yield {
                    "contentBlockStart": {
                        "start": {"toolUse": {"name": call["name"], "toolUseId": call["toolUseId"]}}
                    }
                }
                yield {
                    "contentBlockDelta": {
                        "delta": {"toolUse": {"input": json.dumps(call["input"])}}
                    }
                }
            elif "text" in block:
                yield {"contentBlockStart": {"start": {}}}
                yield {"contentBlockDelta": {"delta": {"text": block["text"]}}}
            elif "reasoningContent" in block:
                yield {"contentBlockStart": {"start": {}}}
                yield {
                    "contentBlockDelta": {
                        "delta": {
                            "reasoningContent": {
                                "text": block["reasoningContent"]["reasoningText"]["text"]
                            }
                        }
                    }
                }
            else:
                raise ValueError(
                    "ScriptedModel supports text, toolUse and reasoningContent blocks."
                )
            yield {"contentBlockStop": {}}
        yield {"messageStop": {"stopReason": stop_reason}}
        yield {
            "metadata": {
                "usage": {
                    "inputTokens": self.input_tokens,
                    "outputTokens": self.output_tokens,
                    "totalTokens": self.input_tokens + self.output_tokens,
                },
                "metrics": {"latencyMs": 0},
            }
        }

    async def structured_output(
        self,
        output_model: type[BaseModel],
        prompt: Any,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Satisfy the Model interface without calling deprecated Agent methods."""
        response = self._next()
        block = response["content"][0]
        payload = block["toolUse"]["input"] if "toolUse" in block else json.loads(block["text"])
        yield {"output": output_model.model_validate(payload)}
