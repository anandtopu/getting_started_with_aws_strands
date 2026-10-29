"""Explicit opt-in launch of the pinned, reviewed AWS MCP servers."""

import json
import os
import shutil
import sys
from contextlib import contextmanager

from mcp import StdioServerParameters
from mcp.client.stdio import stdio_client
from strands.tools.mcp import MCPClient

from common.config import ROOT


@contextmanager
def aws_server(settings, kind):
    definitions = json.loads((ROOT / "modules/14_mcp/aws_servers.json").read_text())
    item = definitions[kind]
    command = shutil.which("uvx")
    if not command:
        raise ValueError("Install uv so uvx is available")
    env = {"FASTMCP_LOG_LEVEL": "ERROR", "AWS_REGION": settings.aws_region}
    if kind == "pricing":
        env["AWS_PROFILE"] = settings.aws_profile
    package = item["package"]
    executable = package.split("==")[0] + (".exe" if os.name == "nt" else "")
    params = StdioServerParameters(command=command, args=["--from", package, executable], env=env)
    with MCPClient(
        lambda: stdio_client(params, errlog=sys.__stderr__), tool_filters={"allowed": item["tools"]}
    ) as client:
        yield client
