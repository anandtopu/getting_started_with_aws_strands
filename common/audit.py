"""Provider-independent hooks; logs contain redacted copies, never raw prompts."""

import re
from time import monotonic

from strands.hooks import (
    AfterInvocationEvent,
    AfterModelCallEvent,
    AfterToolCallEvent,
    AfterToolsEvent,
    AgentInitializedEvent,
    BeforeInvocationEvent,
    BeforeModelCallEvent,
    BeforeToolCallEvent,
    BeforeToolsEvent,
    HookProvider,
    HookRegistry,
    MessageAddedEvent,
    MessageUpdatedEvent,
)


def redact(value):
    """Teaching redactor for email/US phone patterns; not comprehensive PII detection."""
    if isinstance(value, str):
        value = re.sub(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", "[EMAIL]", value)
        return re.sub(r"\b\d{3}[-.]\d{3}[-.]\d{4}\b", "[PHONE]", value)
    if isinstance(value, dict):
        return {k: redact(v) for k, v in value.items()}
    if isinstance(value, list):
        return [redact(v) for v in value]
    return value


class AuditPolicy(HookProvider):
    """One instance per agent. Application context supplies budget and tool authority."""

    def __init__(self, *, allowed=("quote_trip",), max_tools=3):
        self.allowed = set(allowed)
        self.max_tools = max_tools
        self.calls = 0
        self.rows = []
        self.events = []
        self.started = monotonic()

    def register_hooks(self, registry: HookRegistry, **kwargs):
        for event in (
            AgentInitializedEvent,
            BeforeInvocationEvent,
            AfterInvocationEvent,
            BeforeModelCallEvent,
            AfterModelCallEvent,
            BeforeToolsEvent,
            AfterToolsEvent,
            MessageAddedEvent,
            MessageUpdatedEvent,
        ):
            registry.add_callback(event, self.observe)
        registry.add_callback(BeforeInvocationEvent, self.before_invocation)
        registry.add_callback(BeforeToolCallEvent, self.before_tool)
        registry.add_callback(AfterToolCallEvent, self.after_tool)

    def observe(self, event):
        self.events.append(type(event).__name__)
        if isinstance(event, (MessageAddedEvent, MessageUpdatedEvent)):
            self.rows.append({"event": type(event).__name__, "message": redact(event.message)})

    def before_invocation(self, event):
        # Redact before these input messages enter agent history/provider input.
        event.messages = redact(event.messages)

    def before_tool(self, event):
        self.events.append(type(event).__name__)
        self.calls += 1
        name = event.tool_use["name"]
        if name not in self.allowed or self.calls > self.max_tools:
            event.cancel_tool = "Tool is not authorized or its call budget is exhausted"
        elif name == "quote_trip":
            # Catalog price is authoritative; never accept a model-supplied lower price.
            destination = event.tool_use["input"].get("destination", "").strip().upper()
            event.tool_use["input"]["destination"] = destination
            price = {"BOS": 35000, "LAX": 90000}.get(destination)
            budget = event.invocation_state.get("budget_cents", 0)
            if price is None or price > budget:
                event.cancel_tool = "Trip exceeds the trusted budget or destination is unknown"
        self.rows.append(
            {"event": "tool_attempt", "name": name, "blocked": bool(event.cancel_tool)}
        )

    def after_tool(self, event):
        self.events.append(type(event).__name__)
        event.result = redact(event.result)
        self.rows.append(
            {
                "event": "tool_result",
                "name": event.tool_use["name"],
                "status": event.result["status"],
                "seconds": event.duration,
            }
        )


def quote_tool():
    from strands import tool

    @tool
    def quote_trip(destination: str) -> dict:
        """Return a synthetic catalog quote for BOS or LAX; does not purchase travel."""
        return {
            "destination": destination,
            "cents": {"BOS": 35000, "LAX": 90000}[destination],
            "contact": "travel@example.com",
        }

    return quote_trip
