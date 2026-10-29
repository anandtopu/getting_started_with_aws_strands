"""Exercise Streamlit's real widget/session runtime across repeated turns."""

import sys

import pytest

from common.config import ROOT


def test_streamlit_repeated_messages_and_isolated_sessions(monkeypatch):
    pytest.importorskip("streamlit")
    from streamlit.testing.v1 import AppTest

    path = ROOT / "modules/10_streaming/examples/04_streamlit_chat.py"
    monkeypatch.setattr(sys, "argv", [str(path), "--mock", "--ui"])
    first = AppTest.from_file(str(path), default_timeout=30).run()
    assert not first.exception
    for message in ("Boston please", "What next?"):
        first.chat_input[0].set_value(message).run()
        assert not first.exception
    assert len(first.session_state["nimbus_chat"]) == 4
    second = AppTest.from_file(str(path), default_timeout=30).run()
    assert second.session_state["nimbus_chat"] == []
    assert second.session_state["nimbus_agent"] is not first.session_state["nimbus_agent"]
    first.button[0].click().run()
    assert first.session_state["nimbus_chat"] == []
