"""Real subprocess MCP, hooks, interrupt/resume, stream and atomic action together."""

import asyncio
from importlib import import_module

import pytest

from common.config import load_settings


@pytest.mark.parametrize("decision,status", [("approve", "applied"), ("reject", "rejected")])
def test_support_checkpoint(tmp_path, decision, status):
    run_support = import_module("checkpoints.03_safe_support.solution").run_support
    report = asyncio.run(run_support(load_settings(provider="mock"), tmp_path, decision))
    assert report["status"] == status
    assert any(row.get("name") == "nimbus_search_flights" for row in report["audit"])
    assert any(row.get("name") == "apply_action" for row in report["audit"])
