"""Real BidiAgent lifecycle with deterministic PCM events or explicitly selected Nova Sonic."""

import asyncio
import base64

from strands import tool
from strands.bidi import BidiAgent
from strands.bidi.models.model import BidiModel
from strands.bidi.types.events import (
    BidiAudioDeltaEvent,
    BidiBargeInEvent,
    BidiConnectionStartEvent,
    BidiConnectionStopEvent,
    BidiResponseStartEvent,
    BidiResponseStopEvent,
    BidiToolUseBlocksEvent,
)

from common.config import CourseError, course_value


class RecordedVoiceModel(BidiModel):
    """Contract fixture, not speech recognition or synthesis; PCM samples are silence."""

    def __init__(self):
        self.config = {"model_id": "recorded-nimbus-events"}
        self.sent = []
        self.stopped = False
        self.ready = asyncio.Event()
        self.tool_returned = asyncio.Event()

    def get_config(self):
        return self.config.copy()

    def update_config(self, **kwargs):
        self.config.update(kwargs)

    async def start(self, **kwargs):
        self.stopped = False

    async def stop(self):
        self.stopped = True

    async def send(self, content):
        self.sent.append(content)
        if len(self.sent) == 1:
            self.ready.set()
        else:
            self.tool_returned.set()

    async def receive(self):
        await self.ready.wait()
        yield BidiConnectionStartEvent("fixture", self.model_id)
        yield BidiResponseStartEvent("reply")
        yield BidiAudioDeltaEvent(base64.b64encode(b"\0" * 320).decode(), "pcm", 16000, 1, "audio")
        yield BidiBargeInEvent()
        yield BidiToolUseBlocksEvent(
            [{"toolUseId": "voice-quote", "name": "request_booking", "input": {}}]
        )
        await self.tool_returned.wait()
        yield BidiResponseStopEvent("reply")
        yield BidiConnectionStopEvent("fixture", "user_request")


def voice_model(settings):
    if settings.provider == "mock":
        return RecordedVoiceModel()
    if settings.provider != "bedrock" or not course_value("BIDI_MODEL_ID"):
        raise CourseError("Voice needs Bedrock and an explicit BIDI_MODEL_ID; use --mock first.")
    try:
        from strands.bidi.models.bedrock import BedrockNovaSonicModel
    except ImportError as exc:
        raise CourseError(
            "Install the isolated modules/bonus/B1_voice project; see its README."
        ) from exc
    from common.cloud_clients import session

    return BedrockNovaSonicModel(
        boto_session=session(settings), model_id=course_value("BIDI_MODEL_ID")
    )


async def voice_session(settings):
    from common.models import get_model

    requests = []

    @tool
    def request_booking() -> dict:
        """Create a review request only. Spoken words cannot authorize a purchase."""
        requests.append("pending_human_review")
        return {"status": "pending_human_review", "booked": False}

    model = get_model(settings, voice=True)
    agent = BidiAgent(
        model=model,
        tools=[request_booking],
        system_prompt="Request a booking review; never purchase.",
    )
    playback, events = [], []
    async with asyncio.timeout(30):
        async with agent:
            await agent.send("Please request a Nimbus booking review.")
            async for event in agent.receive():
                events.append(event.get("type", type(event).__name__))
                if isinstance(event, BidiAudioDeltaEvent):
                    playback.append(event["audio"])
                if isinstance(event, BidiBargeInEvent):
                    playback.clear()  # KEY IDEA: stop queued playback when the user interrupts.
                if isinstance(event, BidiResponseStopEvent):
                    break
    return {
        "events": events,
        "queued_audio_chunks": len(playback),
        "requests": requests,
        "stopped": getattr(model, "stopped", True),
        "booked": False,
        "scope": "recorded events, no speech engine"
        if settings.provider == "mock"
        else "live voice response",
    }
