"""Explicit offline service doubles and an opt-in local Mem0 configuration."""

import asyncio
import os
from contextlib import contextmanager
from datetime import UTC, datetime

from botocore.stub import Stubber
from strands.memory import MemoryEntry, MemoryManager

from common.aws_retrieval import aws_client
from common.config import course_value
from common.preferences import user_key


class FixtureMem0:
    """A contract double, not an implementation of Mem0's semantic extraction."""

    def __init__(self):
        self.rows = []

    def add(self, content, *, user_id, metadata=None, infer=False):
        if infer:
            raise ValueError("Fixture supports explicit facts only")
        row = {
            "id": str(len(self.rows) + 1),
            "memory": content,
            "user_id": user_id,
            "metadata": metadata or {},
            "score": 1.0,
        }
        self.rows.append(row)
        return {"results": [row]}

    def search(self, query, *, filters, top_k):
        return {"results": [r for r in self.rows if r["user_id"] == filters["user_id"]][:top_k]}

    def delete_all(self, *, user_id):
        self.rows = [r for r in self.rows if r["user_id"] != user_id]


def mem0_store(user_id: str, *, mock: bool, directory):
    os.environ["MEM0_TELEMETRY"] = "false"
    from mem0_strands import Mem0MemoryStore
    from mem0_strands.client import Mem0ServiceClient

    if mock:
        client = Mem0ServiceClient(client=FixtureMem0())
    else:
        from common.models import mem0_local_config

        client = Mem0ServiceClient(config=mem0_local_config(directory))
    return Mem0MemoryStore(
        user_id=user_key(user_id),
        client=client,
        writable=True,
        extraction=False,
        max_search_results=3,
    ), client.mem0


class AgentCorePreferencesStore:
    """Course-owned read-only MemoryStore; uses the stable AgentCore data-plane API."""

    name = "agentcore-preferences"
    description = "Preferences for the authenticated demo traveler"
    writable = False
    extraction = False
    max_search_results = 3

    def __init__(self, client, memory_id: str, customer: str):
        user_key(customer)  # Reject path separators; production supplies authenticated identity.
        self.client, self.memory_id = client, memory_id
        self.namespace = f"/preferences/{customer}/"

    async def search(self, query: str, options=None) -> list[MemoryEntry]:
        count = (options or {}).get("max_search_results", self.max_search_results)
        if not 1 <= count <= 3:
            raise ValueError("This demo permits one to three memories")
        response = await asyncio.to_thread(
            self.client.retrieve_memory_records,
            memoryId=self.memory_id,
            namespace=self.namespace,
            searchCriteria={"searchQuery": query, "topK": count},
            maxResults=count,
        )
        # One bounded result page is sufficient for this lesson; no exhaustive scan.
        return [
            MemoryEntry(content=row["content"]["text"], metadata={"id": row["memoryRecordId"]})
            for row in response.get("memoryRecordSummaries", [])[:count]
            if self.namespace in row["namespaces"]
        ]


@contextmanager
def agentcore_manager(*, mock: bool):
    """Read via MemoryManager without importing AgentCore's deprecated session aliases."""
    memory_id = "NimbusDemo-1234567890" if mock else course_value("AGENTCORE_MEMORY_ID")
    if not memory_id:
        raise ValueError("Set AGENTCORE_MEMORY_ID for an existing optional memory resource")
    client = aws_client("bedrock-agentcore", mock=mock)
    store = AgentCorePreferencesStore(client, memory_id, "CUS-001")
    manager = MemoryManager(
        stores=[store], injection=False, search_tool_config=False, add_tool_config=False
    )
    try:
        if mock:
            with Stubber(client) as stub:
                stub.add_response(
                    "retrieve_memory_records",
                    {
                        "memoryRecordSummaries": [
                            {
                                "memoryRecordId": "mem-00000000-0000-0000-0000-000000000001",
                                "memoryStrategyId": "Preferences-1234567890",
                                "namespaces": [store.namespace],
                                "createdAt": datetime(2026, 10, 29, tzinfo=UTC),
                                "content": {"text": "Traveler prefers an aisle seat."},
                            }
                        ]
                    },
                    {
                        "memoryId": memory_id,
                        "namespace": store.namespace,
                        "searchCriteria": {"searchQuery": "seat preference", "topK": 3},
                        "maxResults": 3,
                    },
                )
                yield manager
                stub.assert_no_pending_responses()
        else:
            yield manager
    finally:
        client.close()
