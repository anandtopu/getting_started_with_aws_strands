"""Small reusable boundaries for the multi-agent lessons."""

import json
import time
from dataclasses import dataclass, field

from strands import Agent
from strands.agent.agent_result import AgentResult
from strands.hooks import BeforeInvocationEvent, BeforeModelCallEvent, HookProvider
from strands.multiagent.base import MultiAgentBase, MultiAgentResult, NodeResult, Status
from strands.telemetry.metrics import EventLoopMetrics

from common.models import get_model
from common.pretty import estimate_cost


class ModelTurnBudget(HookProvider):
    """Each node invocation gets a small independent model-call allowance."""

    def __init__(self, maximum=3):
        self.maximum, self.calls = maximum, 0

    def register_hooks(self, registry, **kwargs):
        registry.add_callback(BeforeInvocationEvent, self.reset)
        registry.add_callback(BeforeModelCallEvent, self.check)

    def reset(self, event):
        self.calls = 0

    def check(self, event):
        self.calls += 1
        if self.calls > self.maximum:
            raise RuntimeError("Node model-call budget exhausted")


def worker(settings, name, responses, *, tools=(), prompt=None, **kwargs):
    return Agent(
        name=name,
        model=get_model(settings, responses=responses),
        tools=list(tools),
        system_prompt=prompt
        or f"You are Nimbus's {name}. Use synthetic facts only; never book or pay.",
        hooks=[ModelTurnBudget()],
        callback_handler=None,
        retry_strategy=None,
        **kwargs,
    )


def summarize(result):
    """Multi-agent metrics already aggregate descendants: do not sum them twice."""
    order = getattr(result, "node_history", getattr(result, "execution_order", []))
    return {
        "status": result.status.value,
        "order": [node.node_id for node in order],
        "nodes": {name: node.status.value for name, node in result.results.items()},
        "executions": result.execution_count,
        "usage": dict(result.accumulated_usage),
        "milliseconds": result.execution_time,
    }


def report(result, settings):
    record = summarize(result)
    repeated = len(record["order"]) != len(set(record["order"]))
    record["inference_estimate_usd"] = (
        None if repeated else estimate_cost(record["usage"], settings)
    )
    record["usage_note"] = (
        "SDK totals can count cumulative usage again on revisits; not billing evidence"
        if repeated
        else "SDK aggregate; do not add descendant totals again"
    )
    record["usage_kind"] = "scripted fixture" if settings.provider == "mock" else "provider usage"
    print(json.dumps(record, indent=2))
    return record


@dataclass
class StepOutput:
    value: dict
    usage: dict = field(
        default_factory=lambda: {"inputTokens": 0, "outputTokens": 0, "totalTokens": 0}
    )


class FunctionNode(MultiAgentBase):
    """Graph executor for application steps; explicitly propagate any child model usage."""

    def __init__(self, name, function):
        self.name, self.function = name, function

    async def invoke_async(self, task, invocation_state=None, **kwargs):
        started = time.monotonic()
        value = await self.function(task, invocation_state or {})
        measured = value if isinstance(value, StepOutput) else StepOutput(value)
        result = AgentResult(
            stop_reason="end_turn",
            message={"role": "assistant", "content": [{"text": json.dumps(measured.value)}]},
            metrics=EventLoopMetrics(),
            state={},
        )
        return MultiAgentResult(
            status=Status.COMPLETED,
            execution_count=1,
            accumulated_usage=measured.usage,
            execution_time=int((time.monotonic() - started) * 1000),
            results={
                self.name: NodeResult(
                    result=result,
                    status=Status.COMPLETED,
                    accumulated_usage=measured.usage,
                    execution_count=1,
                )
            },
        )
