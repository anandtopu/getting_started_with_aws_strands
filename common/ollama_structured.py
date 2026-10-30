"""Use Ollama's JSON schema mode for Strands' forced structured-output retry."""

import json

from strands.models.ollama import OllamaModel


class StructuredOllamaModel(OllamaModel):
    """Only the explicitly registered output schema gets this provider fallback.

    Ordinary tool selection still belongs to the model. On Strands' final forced
    retry, JSON schema constrains syntax; Strands and application validators still
    check the result. No fixture or application answer substitutes for inference.
    """

    def __init__(self, *args, output_schema, **kwargs):
        super().__init__(*args, **kwargs)
        self.output_schema = output_schema

    async def stream(
        self, messages, tool_specs=None, system_prompt=None, *, tool_choice=None, **kwargs
    ):
        if tool_choice != {"tool": {"name": self.output_schema.__name__}}:
            async for event in super().stream(
                messages, tool_specs, system_prompt, tool_choice=tool_choice, **kwargs
            ):
                yield event
            return
        schema = self.output_schema.model_json_schema()
        config = self.get_config().copy()
        config["additional_args"] = {
            **(config.get("additional_args") or {}),
            "format": schema,
            "tools": [],
        }
        # A separate adapter avoids mutating configuration shared by concurrent calls.
        constrained = OllamaModel(self.host, ollama_client_args=self.client_args, **config)
        prompt = (system_prompt or "") + (
            "\nFor this final response return one JSON object, not a tool call or Python "
            "constructor. Use only the retrieved evidence and preserve its identifiers. "
            "Required JSON schema: " + json.dumps(schema)
        )
        async for event in constrained.stream(messages, system_prompt=prompt, **kwargs):
            yield event
