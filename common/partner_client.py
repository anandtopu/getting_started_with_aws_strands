"""Own the partner process and authenticated client; do not pass credentials in prompts."""

import asyncio
import os
import secrets
import socket
import subprocess
import sys
import time
from contextlib import contextmanager
from typing import Literal
from urllib.parse import urlsplit

import httpx
from pydantic import BaseModel, ConfigDict

from common.config import ROOT
from common.mcp_clients import child_environment


class UpgradeOffer(BaseModel):
    model_config = ConfigDict(extra="forbid")
    offer_id: Literal["UP-001"]
    flight_id: Literal["FLT-0001"]
    cents: Literal[7500]
    currency: Literal["USD"]
    quote_only: Literal[True]


@contextmanager
def partner_process(settings, *, backend="strands"):
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    token = secrets.token_urlsafe(24)
    env = {**child_environment(), "NIMBUS_PARTNER_TOKEN": token}
    args = [
        sys.executable,
        "-m",
        "common.partner_server",
        "--port",
        str(port),
        "--backend",
        backend,
    ]
    if settings.provider == "mock":
        args.append("--mock")
    else:
        if os.environ.get("NIMBUS_OFFLINE") != "1":
            env.pop("NIMBUS_OFFLINE", None)
        # The local child reads the same course configuration. Never forward model keys in prompts.
        for key in ("MODEL_PROVIDER", "MODEL_ID", "AWS_PROFILE", "AWS_REGION", "OLLAMA_HOST"):
            if key in os.environ:
                env[key] = os.environ[key]
    process = subprocess.Popen(
        args,
        cwd=ROOT,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
    )
    url = f"http://127.0.0.1:{port}/"
    try:
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline:
            if process.poll() is not None:
                raise RuntimeError(
                    "Partner failed to start; install --group multiagent --group partner"
                )
            try:
                with httpx.Client(trust_env=False, timeout=0.3) as client:
                    response = client.get(
                        url + ".well-known/agent-card.json",
                        headers={"Authorization": "Bearer " + token},
                    )
                    if response.status_code == 200:
                        break
            except httpx.HTTPError:
                pass
            time.sleep(0.05)
        else:
            raise TimeoutError("Local partner startup deadline reached")
        yield url, token
    finally:
        try:
            with httpx.Client(trust_env=False, timeout=2) as client:
                client.post(url + "_shutdown", headers={"Authorization": "Bearer " + token})
            process.wait(timeout=8)
        except (httpx.HTTPError, subprocess.TimeoutExpired):
            if process.poll() is None:
                if os.name == "nt":
                    subprocess.run(
                        ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                        check=False,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        timeout=10,
                        creationflags=subprocess.CREATE_NO_WINDOW,
                    )
                else:
                    process.kill()
                process.wait(timeout=5)


async def ask_partner(url, token, *, streaming=False):
    from a2a.client import ClientConfig
    from strands.agent.a2a_agent import A2AAgent

    async with httpx.AsyncClient(
        headers={"Authorization": "Bearer " + token},
        timeout=10,
        trust_env=False,
        follow_redirects=False,
    ) as http:
        remote = A2AAgent(endpoint=url, client_config=ClientConfig(httpx_client=http), timeout=10)
        async with asyncio.timeout(15):
            card = await remote.get_agent_card()
            expected, advertised = urlsplit(url), urlsplit(card.url)
            if (advertised.scheme, advertised.netloc) != (expected.scheme, expected.netloc):
                raise ValueError("The partner card advertises an unapproved destination")
            events = []
            if streaming:
                result = None
                async for event in remote.stream_async("Quote a seat upgrade on FLT-0001"):
                    if event.get("type") == "a2a_stream":
                        payload = event["event"]
                        if isinstance(payload, tuple):
                            payload = payload[1]
                        events.append(type(payload).__name__)
                    if "result" in event:
                        result = event["result"]
            else:
                result = await remote.invoke_async("Quote a seat upgrade on FLT-0001")
            offer = validated_partner_result(result)
        return {
            "card_name": card.name,
            "protocol_version": card.protocol_version,
            "offer": offer.model_dump(),
            "events": events,
            "usage": "Remote provider tokens are not supplied by this A2A response",
        }


def validated_partner_result(result):
    if (
        result is None
        or result.stop_reason != "end_turn"
        or result.state.get("a2a_task_state") != "completed"
    ):
        raise ValueError("Partner did not complete a quote")
    # AgentResult.__str__ joins blocks with newlines, corrupting streamed
    # JSON when A2A artifact parts split inside a key or string value.
    payload = "".join(block.get("text", "") for block in result.message["content"])
    return UpgradeOffer.model_validate_json(payload)
