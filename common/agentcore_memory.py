"""Bounded Memory event/recall example with explicit event cleanup."""

import re
import uuid
from contextlib import nullcontext
from datetime import UTC, datetime

from botocore.stub import Stubber

from common.cloud_clients import client


def preferences(settings, memory_id: str, actor: str):
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,100}", actor):
        raise ValueError("Actor must be a trusted identity containing only letters, digits, _ or -")
    api = client("bedrock-agentcore", settings)
    session_id = "course-" + uuid.uuid4().hex
    now = datetime.now(UTC)
    create = {
        "memoryId": memory_id,
        "actorId": actor,
        "sessionId": session_id,
        "eventTimestamp": now,
        "payload": [
            {
                "conversational": {
                    "content": {"text": "Synthetic traveler prefers an aisle seat."},
                    "role": "USER",
                }
            }
        ],
    }
    recall = {
        "memoryId": memory_id,
        "namespace": f"/preferences/{actor}/",
        "searchCriteria": {"searchQuery": "seat preference", "topK": 3},
        "maxResults": 3,
    }
    stub = Stubber(api)
    if settings.provider == "mock":
        stub.add_response(
            "create_event", {"event": {**create, "eventId": "event-1234567890123"}}, create
        )
        stub.add_response(
            "retrieve_memory_records",
            {
                "memoryRecordSummaries": [
                    {
                        "memoryRecordId": "mem-00000000-0000-0000-0000-000000000001",
                        "memoryStrategyId": "Preferences-1234567890",
                        "namespaces": [recall["namespace"]],
                        "createdAt": now,
                        "content": {"text": "Traveler prefers an aisle seat."},
                    }
                ]
            },
            recall,
        )
        stub.add_response(
            "delete_event",
            {"eventId": "event-1234567890123"},
            {
                "memoryId": memory_id,
                "actorId": actor,
                "sessionId": session_id,
                "eventId": "event-1234567890123",
            },
        )
    with stub if settings.provider == "mock" else nullcontext():
        event = api.create_event(**create)["event"]
        try:
            records = api.retrieve_memory_records(**recall).get("memoryRecordSummaries", [])
            # Extraction is asynchronous: these may be older memories or an empty list.
            result = [
                r["content"]["text"] for r in records if recall["namespace"] in r["namespaces"]
            ]
        finally:
            api.delete_event(
                memoryId=memory_id, actorId=actor, sessionId=session_id, eventId=event["eventId"]
            )
        if settings.provider == "mock":
            stub.assert_no_pending_responses()
    return {
        "preferences": result,
        "event_deleted": True,
        "note": "Deleting an event does not delete asynchronously extracted long-term records",
    }
