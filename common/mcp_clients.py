"""Own local server lifetimes explicitly; reject unexpected tools before registration."""

import os
import secrets
import socket
import subprocess
import sys
import time
from contextlib import contextmanager

from mcp import StdioServerParameters
from mcp.client.stdio import stdio_client
from strands.tools.mcp import MCPClient

from common.config import ROOT


def child_environment():
    keys = {"PATH", "SYSTEMROOT", "WINDIR", "TEMP", "TMP", "HOME", "USERPROFILE", "VIRTUAL_ENV"}
    return {
        **{k: v for k, v in os.environ.items() if k.upper() in keys},
        "PYTHONUTF8": "1",
        "AWS_EC2_METADATA_DISABLED": "true",
        "OTEL_SDK_DISABLED": "true",
        "NIMBUS_OFFLINE": "1",
    }


def stdio_booking(database, *, prefix="nimbus", allowed=None):
    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "common.mcp_server", "--database", str(database)],
        cwd=str(ROOT),
        env=child_environment(),
    )
    return MCPClient(
        # Jupyter replaces sys.stderr with an OutStream without a file descriptor.
        lambda: stdio_client(params, errlog=sys.__stderr__),
        prefix=prefix,
        tool_filters={"allowed": allowed or ["search_flights", "create_booking", "get_booking"]},
    )


@contextmanager
def http_booking(database):
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    token = secrets.token_urlsafe(24)
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "common.mcp_server",
            "--database",
            str(database),
            "--port",
            str(port),
        ],
        cwd=ROOT,
        env={**child_environment(), "NIMBUS_SERVER_TOKEN": token},
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
    )
    try:
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline:
            if process.poll() is not None:
                raise RuntimeError("Local MCP server exited during startup")
            try:
                with socket.create_connection(("127.0.0.1", port), timeout=0.2):
                    break
            except OSError:
                time.sleep(0.05)
        else:
            raise TimeoutError("Local MCP server did not start")
        url = f"http://127.0.0.1:{port}/mcp"
        with MCPClient(
            url=url,
            headers={"Authorization": "Bearer " + token},
            prefix="nimbus",
            tool_filters={"allowed": ["search_flights"]},
        ) as client:
            yield client, url
    finally:
        import httpx

        # Windows venv launchers can own another interpreter process. Ask the server
        # itself to stop so its SQLite handles close before removing the directory.
        try:
            with httpx.Client(trust_env=False, timeout=2) as http:
                http.post(
                    f"http://127.0.0.1:{port}/_shutdown",
                    headers={"Authorization": "Bearer " + token},
                )
            process.wait(timeout=8)
        except (httpx.HTTPError, subprocess.TimeoutExpired):
            if process.poll() is None:
                if os.name == "nt":
                    subprocess.run(
                        ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        check=False,
                        timeout=10,
                        creationflags=subprocess.CREATE_NO_WINDOW,
                    )
                else:
                    process.kill()
                process.wait(timeout=5)


def reviewed_tools(client, expected):
    # list_tools_sync returns a page; this tiny server must have no hidden additional page.
    tools = client.list_tools_sync()
    if tools.pagination_token:
        raise ValueError("Unexpected additional tool page; review all capabilities before use")
    names = {t.tool_name for t in tools}
    if names != set(expected):
        raise ValueError(
            f"MCP capability review failed: expected {sorted(expected)}, got {sorted(names)}"
        )
    return tools
