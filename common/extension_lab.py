"""Generated code remains data until it matches a reviewed template and approved digest."""

import hashlib
import json
from pathlib import Path

from pydantic import BaseModel, Field
from strands import Agent, tool

from common.models import get_model
from common.testing import tool_message


class ToolProposal(BaseModel):
    source: str = Field(max_length=3000)


def template(fee: int) -> str:
    if type(fee) is not int or fee not in (2500, 3000):
        raise ValueError("Only the two reviewed fee templates are allowed")
    return (
        "def baggage_fee(bags: int) -> int:\n"
        '    """Quote synthetic baggage cents; no purchase."""\n'
        "    if type(bags) is not int or not 0 <= bags <= 4:\n"
        '        raise ValueError("Choose 0 to 4 bags")\n'
        f"    return bags * {fee}\n"
    )


def digest(source: str) -> str:
    return hashlib.sha256(source.encode()).hexdigest()


def review(source: str, approved_digest: str):
    if digest(source) != approved_digest or source not in [template(2500), template(3000)]:
        raise PermissionError("Source is unreviewed or changed after approval")
    # Exact template equality is the permission boundary; this is not a Python sandbox.
    namespace = {}
    exec(compile(source, "<reviewed-nimbus-tool>", "exec"), namespace)
    function = namespace["baggage_fee"]
    if function(2) not in (5000, 6000):
        raise ValueError("Reviewed tool failed its contract")
    return tool(function)


def propose(settings):
    agent = Agent(
        model=get_model(
            settings, responses=[tool_message("ToolProposal", {"source": template(2500)})]
        ),
        structured_output_model=ToolProposal,
        callback_handler=None,
        system_prompt=(
            "Return exactly the requested reviewed baggage fee function. "
            "No imports or side effects."
        ),
    )
    result = agent("Propose this tool source:\n" + template(2500), limits={"turns": 2})
    return result.structured_output.source


def reload_demo(settings, directory: Path):
    directory.mkdir(parents=True, exist_ok=True)
    source = propose(settings)
    first = review(source, digest(template(2500)))
    agent = Agent(
        model=get_model(
            settings, responses=[tool_message("baggage_fee", {"bags": 2}), "Quote checked."]
        ),
        tools=[first],
        callback_handler=None,
    )
    agent("Quote two bags.", limits={"turns": 2})
    updated = template(3000)
    replacement = review(updated, digest(template(3000)))
    agent.tool_registry.process_tools([replacement])
    agent.model = get_model(
        settings, responses=[tool_message("baggage_fee", {"bags": 2}), "Updated quote checked."]
    )
    agent("Quote two bags with the reviewed replacement.", limits={"turns": 2})
    updated_result = next(
        block["toolResult"]
        for message in reversed(agent.messages)
        for block in message["content"]
        if "toolResult" in block
    )
    # Explicit replacement after review; no watcher loads arbitrary filesystem edits.
    audit = [
        {"sha256": digest(source), "cents": first(2)},
        {"sha256": digest(updated), "cents": replacement(2)},
    ]
    (directory / "review-history.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
    return {
        "versions": audit,
        "registered": agent.tool_names,
        "updated_tool_result": updated_result,
        "auto_execute_generated_code": False,
    }
