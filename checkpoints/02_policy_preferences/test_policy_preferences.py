"""End-to-end user isolation and cited answers in a persisted support session."""

from common.config import load_settings
from common.preferences import Preferences
from common.rag_agent import answer_policy
from common.retrieval import load_chunks


def test_policy_preferences_checkpoint(tmp_path):
    store = Preferences(tmp_path)
    store.save("CUS-001", "seat", "aisle", consent=True)
    store.save("CUS-002", "seat", "window", consent=True)
    manager = store.session("CUS-001", "support")
    result, evidence = answer_policy(
        load_settings(provider="mock"),
        "approved refund timing",
        load_chunks(pdf=True),
        session_manager=manager,
        preferences=store.read("CUS-001"),
    )
    assert result.structured_output.citations
    assert evidence
    store.delete_user("CUS-001")
    assert not (tmp_path / "sessions" / f"session_{manager.session_id}").exists()
    assert store.read("CUS-002") == {"seat": "window"}
