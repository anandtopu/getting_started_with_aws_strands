"""Public booking quotes behind a Gateway-compatible MCP boundary; no payment authority."""

import json
import re
import sys
from urllib.parse import urlsplit

from mcp import StdioServerParameters
from mcp.client.stdio import stdio_client
from strands.tools.mcp import MCPClient

from common.config import ROOT
from common.mcp_clients import child_environment
from common.public_booking import refund_quote, search_flights

TOOLS = ["nimbus___search_flights", "nimbus___refund_quote"]


def gateway_client(settings, *, url="", token=""):
    if settings.provider == "mock":
        params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "common.gateway_booking"],
            cwd=str(ROOT),
            env=child_environment(),
        )
        return MCPClient(
            lambda: stdio_client(params, errlog=sys.__stderr__),
            tool_filters={"allowed": [*TOOLS, "x_amz_bedrock_agentcore_search"]},
        )
    target = urlsplit(url)
    pattern = (
        r"[a-z0-9-]+\.gateway\.bedrock-agentcore\."
        + re.escape(settings.aws_region)
        + r"\.amazonaws\.com"
    )
    if (
        target.scheme != "https"
        or not re.fullmatch(pattern, target.hostname or "")
        or target.username
        or target.password
        or target.port not in (None, 443)
        or target.path != "/mcp"
        or target.query
        or target.fragment
        or not token
    ):
        raise ValueError("Supply the deployed regional Gateway HTTPS /mcp URL and a JWT")
    return MCPClient(
        url=url,
        headers={"Authorization": "Bearer " + token},
        tool_filters={"allowed": [*TOOLS, "x_amz_bedrock_agentcore_search"]},
    )


def gateway_probe(settings, *, url="", token=""):
    with gateway_client(settings, url=url, token=token) as gateway:
        discovered = gateway.list_tools_sync()
        names = {item.tool_name for item in discovered}
        if not set(TOOLS) <= names:
            raise ValueError("Gateway lacks the reviewed Nimbus tools")
        search = gateway.call_tool_sync(
            "search-1", "x_amz_bedrock_agentcore_search", {"query": "Nimbus refund quote"}
        )
        allowed = gateway.call_tool_sync(
            "quote-1", "nimbus___refund_quote", {"amount_cents": 50_000}
        )
        denied = gateway.call_tool_sync(
            "quote-2", "nimbus___refund_quote", {"amount_cents": 50_001}
        )
        if (
            search["status"] != "success"
            or allowed["status"] != "success"
            or denied["status"] != "error"
        ):
            raise ValueError("Gateway refund boundary check failed")
        return {
            "tools": sorted(names),
            "search_status": search["status"],
            "within_limit": allowed["status"],
            "over_limit": denied["status"],
            "scope": "Local MCP + Python boundary"
            if settings.provider == "mock"
            else "Live Gateway",
        }


def main():
    from mcp.server.mcpserver import MCPServer
    from pydantic import StrictInt

    from common.network import offline_network

    server = MCPServer("Nimbus public booking quotes", log_level="CRITICAL")
    server.tool(name="nimbus___search_flights")(search_flights)

    @server.tool(name="nimbus___refund_quote")
    def local_refund_quote(amount_cents: StrictInt) -> dict:
        """Quote a refund with strict integer cents and an inclusive USD 500 ceiling."""
        return refund_quote(amount_cents)

    @server.tool(name="x_amz_bedrock_agentcore_search")
    def local_tool_search(query: str) -> str:
        """Local keyword alternative; AWS Gateway supplies the real semantic index."""
        return json.dumps(
            [name for name in TOOLS if any(word in name for word in query.lower().split())]
        )

    with offline_network():
        server.run(transport="stdio")


if __name__ == "__main__":
    main()
