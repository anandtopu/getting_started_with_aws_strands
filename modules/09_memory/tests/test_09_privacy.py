"""Customer boundaries, retention and deletion must hold outside the model."""

import asyncio

import pytest
from strands import Agent

from common.models import get_model
from common.preferences import Preferences, user_key


def test_preferences_consent_scope_and_expiry(tmp_path):
    store = Preferences(tmp_path)
    with pytest.raises(PermissionError):
        store.save("CUS-001", "seat", "aisle", consent=False)
    with pytest.raises(ValueError):
        store.save("CUS-001", "passport", "synthetic", consent=True)
    store.save("CUS-001", "seat", "aisle", consent=True, now=100)
    assert store.read("CUS-002", now=101) == {}
    assert store.read("CUS-001", now=100 + 90 * 86400) == {}
    with pytest.raises(ValueError):
        store.session("CUS-001", "../../escape")


def test_session_resume_isolation_and_complete_registered_deletion(tmp_path):
    store = Preferences(tmp_path)
    manager = store.session("CUS-001", "trip")
    agent = Agent(
        model=get_model(provider="mock", responses=["Aisle noted."]),
        session_manager=manager,
        callback_handler=None,
    )
    agent("Aisle seat please.")
    restored = Agent(
        model=get_model(provider="mock", responses=[]),
        session_manager=store.session("CUS-001", "trip"),
        callback_handler=None,
    )
    assert len(restored.messages) == 2
    other = Agent(
        model=get_model(provider="mock", responses=[]),
        session_manager=store.session("CUS-002", "trip"),
        callback_handler=None,
    )
    assert other.messages == []
    store.save("CUS-002", "meal", "vegetarian", consent=True)
    store.delete_user("CUS-001")
    assert not (tmp_path / "sessions" / f"session_{manager.session_id}").exists()
    assert store.read("CUS-002") == {"meal": "vegetarian"}
    store.delete_user("CUS-001")  # Repeated deletion is harmless.


def test_mem0_adapter_scopes_search_and_delete(tmp_path):
    pytest.importorskip("mem0_strands")
    from mem0_strands import Mem0MemoryStore

    from common.memory_adapters import mem0_store

    store, backend = mem0_store("CUS-001", mock=True, directory=tmp_path)
    other = Mem0MemoryStore(user_id=user_key("CUS-002"), client=store.client)
    asyncio.run(store.add("aisle"))
    asyncio.run(other.add("window"))
    assert asyncio.run(store.search("seat"))[0].content == "aisle"
    backend.delete_all(user_id=user_key("CUS-001"))
    assert asyncio.run(store.search("seat")) == []
    assert asyncio.run(other.search("seat"))[0].content == "window"


def test_private_state_is_not_model_input():
    model = get_model(provider="mock", responses=["Please share a preference."])
    agent = Agent(model=model, callback_handler=None)
    agent.state.set("private_marker", "not-for-provider-123")
    agent("Hello")
    assert "not-for-provider-123" not in str(model.requests)


def test_agentcore_store_reads_exact_scoped_request():
    from common.memory_adapters import agentcore_manager

    model = get_model(provider="mock", responses=["Aisle noted."])
    with agentcore_manager(mock=True) as manager:
        records = asyncio.run(manager.search("seat preference"))
        Agent(model=model, memory_manager=manager, callback_handler=None)(records[0].content)
    assert "aisle seat" in str(model.requests)
    assert not model.requests[0]["tool_specs"]


def test_agentcore_scope_filter_and_service_errors():
    from botocore.exceptions import ClientError

    from common.memory_adapters import AgentCorePreferencesStore

    class Client:
        def retrieve_memory_records(self, **kwargs):
            assert kwargs["namespace"] == "/preferences/CUS-001/"
            return {
                "memoryRecordSummaries": [
                    {
                        "namespaces": ["/preferences/CUS-002/"],
                        "content": {"text": "Another traveler"},
                        "memoryRecordId": "unrelated",
                    }
                ]
            }

    store = AgentCorePreferencesStore(Client(), "NimbusDemo-1234567890", "CUS-001")
    assert asyncio.run(store.search("seat")) == []
    with pytest.raises(ValueError):
        asyncio.run(store.search("seat", {"max_search_results": 4}))
    with pytest.raises(ValueError):
        AgentCorePreferencesStore(Client(), "NimbusDemo-1234567890", "../CUS-002")

    class Denied:
        def retrieve_memory_records(self, **kwargs):
            raise ClientError({"Error": {"Code": "AccessDeniedException"}}, "RetrieveMemoryRecords")

    store = AgentCorePreferencesStore(Denied(), "NimbusDemo-1234567890", "CUS-001")
    with pytest.raises(ClientError):
        asyncio.run(store.search("seat"))
