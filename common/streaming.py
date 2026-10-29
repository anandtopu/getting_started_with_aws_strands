"""Bounded streams and protocol framing shared by the CLI and web lessons."""

import asyncio
import json
from contextlib import aclosing

from strands import Agent

from common.models import get_model


def sync_chunks(chunks):
    """Keep an async iterator in one task/context while a synchronous UI consumes text."""
    import queue
    import threading

    messages = queue.Queue(maxsize=16)
    stopped = threading.Event()
    end = object()
    context = {}

    async def send(value):
        while not stopped.is_set():
            try:
                messages.put_nowait(value)
                return
            except queue.Full:
                await asyncio.sleep(0.01)

    async def produce():
        context.update(loop=asyncio.get_running_loop(), task=asyncio.current_task())
        try:
            async with asyncio.timeout(30), aclosing(chunks):
                async for value in chunks:
                    if stopped.is_set():
                        break
                    await send(value)
        except Exception as exc:
            await send(exc)
        finally:
            await send(end)

    def run():
        try:
            asyncio.run(produce())
        except asyncio.CancelledError:
            pass  # Consumer shutdown cancels only this worker's owned task.

    worker = threading.Thread(target=run, daemon=True)
    worker.start()
    try:
        while True:
            value = messages.get(timeout=35)
            if value is end:
                return
            if isinstance(value, Exception):
                raise value
            yield value
    finally:
        stopped.set()
        loop, task = context.get("loop"), context.get("task")
        if loop and task and not task.done():
            try:
                loop.call_soon_threadsafe(task.cancel)
            except RuntimeError:
                pass  # The owned event loop finished between inspection and scheduling.
        worker.join(timeout=2)


def planner(settings):
    return Agent(
        model=get_model(settings, responses=["Fly to Boston, check in, then explore on foot."]),
        system_prompt="Suggest a short fictional trip plan. Do not claim to book anything.",
        callback_handler=None,
        retry_strategy=None,
    )


def sse(event, payload):
    if event not in {"text", "done", "error", "interrupt", "status"}:
        raise ValueError("Unsupported public event")
    return f"event: {event}\ndata: {json.dumps(payload, ensure_ascii=True)}\n\n"


async def public_stream(agent, prompt, *, disconnected=None, seconds=30):
    """Cancellation closes the iterator; do not share one Agent across concurrent requests."""

    async def connected():
        return False

    disconnected = disconnected or connected
    try:
        async with (
            asyncio.timeout(seconds),
            aclosing(agent.stream_async(prompt, limits={"turns": 4})) as events,
        ):
            async for event in events:
                if await disconnected():
                    return
                if "data" in event:
                    yield sse("text", {"text": event["data"]})
                if "result" in event:
                    result = event["result"]
                    if result.stop_reason == "interrupt":
                        yield sse("interrupt", {"count": len(result.interrupts)})
                    yield sse("done", {"stop_reason": result.stop_reason})
    except TimeoutError:
        yield sse("error", {"message": "Request timed out"})
    except asyncio.CancelledError:
        raise
    except Exception:
        yield sse("error", {"message": "Request failed; check the local service configuration"})
