"""A module-style tool: TOOL_SPEC plus an entry function with the same name."""

from common.data import data_path

TOOL_SPEC = {
    "name": "policy_lookup",
    "description": "Read Nimbus's refund policy.",
    "inputSchema": {"json": {"type": "object", "properties": {}, "required": []}},
}


def policy_lookup(tool: dict, **kwargs) -> dict:
    return {
        "toolUseId": tool["toolUseId"],
        "status": "success",
        "content": [{"text": data_path("policies/refund.md").read_text(encoding="utf-8")}],
    }
