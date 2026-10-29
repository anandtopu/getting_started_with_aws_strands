"""Build it yourself: bounded boto3 Converse loop with toolConfig/toolUse/toolResult, then
Strands equivalent.

Run: uv run python modules/05_building_tools/examples/09_manual_converse_loop.py --mock
Expected: Lesson complete.
Cost: mock/local $0 hosted inference; live hosted calls use tokens.
AWS required: Yes; offline Stubber replay. Resources created: none.
"""

from contextlib import nullcontext

import boto3
from botocore.config import Config
from botocore.stub import Stubber
from strands import Agent

from common.config import load_settings
from common.lessons import complete, lesson_settings, require_bedrock
from common.models import get_model
from common.pretty import console, run_cli
from common.testing import tool_message
from common.tools import policy_lookup


def manual_loop(client, model_id: str) -> dict:
    messages = [{"role": "user", "content": [{"text": "Read Nimbus refund policy."}]}]
    specs = {"tools": [{"toolSpec": policy_lookup.TOOL_SPEC}]}
    for _ in range(3):
        response = client.converse(
            modelId=model_id,
            messages=messages,
            toolConfig=specs,
            inferenceConfig={"maxTokens": 256, "temperature": 0},
        )
        message = response["output"]["message"]
        messages.append(message)
        if response["stopReason"] == "end_turn":
            return message
        results = []
        for block in message["content"]:
            if "toolUse" in block:
                call = block["toolUse"]
                if call["name"] != "policy_lookup":
                    raise ValueError("Tool not allowed")
                results.append({"toolResult": policy_lookup.policy_lookup(call)})
        if not results:
            raise ValueError("No answer or allowed tool request")
        # KEY IDEA: append toolResult as a user message, then ask the model again.
        messages.append({"role": "user", "content": results})
    raise RuntimeError("Manual loop exceeded three turns")


def main() -> None:
    args, cfg = lesson_settings()
    target = load_settings(provider="bedrock")
    if args.mock:
        client = boto3.client(
            "bedrock-runtime",
            region_name=target.aws_region,
            aws_access_key_id="testing",
            aws_secret_access_key="testing",
        )
        stub = Stubber(client)
        for message, stop in [
            (tool_message("policy_lookup", {}), "tool_use"),
            ({"role": "assistant", "content": [{"text": "24 hours and 7 days."}]}, "end_turn"),
        ]:
            stub.add_response(
                "converse",
                {
                    "output": {"message": message},
                    "stopReason": stop,
                    "usage": {"inputTokens": 100, "outputTokens": 20, "totalTokens": 120},
                    "metrics": {"latencyMs": 0},
                },
            )
        context = stub
    else:
        require_bedrock(cfg)
        client = boto3.Session(
            profile_name=cfg.aws_profile or None, region_name=cfg.aws_region
        ).client(
            "bedrock-runtime",
            config=Config(connect_timeout=5, read_timeout=30, retries={"max_attempts": 1}),
        )
        context = nullcontext()
    with context:
        console.print("Manual:", manual_loop(client, target.model_id))
    model = get_model(cfg, responses=[tool_message("policy_lookup", {}), "24 hours and 7 days."])
    agent = Agent(model=model, tools=[policy_lookup], callback_handler=None, retry_strategy=None)
    result = agent("Read Nimbus refund policy.", limits={"turns": 3})
    complete(result, cfg)


if __name__ == "__main__":
    run_cli(main)
