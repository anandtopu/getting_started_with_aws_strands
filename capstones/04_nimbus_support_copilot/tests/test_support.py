"""Compose actual retrieval, memory and interrupted approval, then check durable outcomes."""

import json
from pathlib import Path

import pytest

from common.approvals import ApprovalLedger
from common.config import load_settings
from common.flagship import local_support, release_report


@pytest.mark.parametrize(
    "case", json.loads((Path(__file__).parents[1] / "evaluation.json").read_text())
)
async def test_approval_and_replay(case, tmp_path):
    result = await local_support(
        load_settings(provider="mock"), tmp_path, decision=case["decision"]
    )
    assert result["approval"] == case["expected_status"]
    assert result["preferences"] == {"seat": "aisle"}
    assert "policies/refund.md" in result["policy"]["answer"]
    ledger = ApprovalLedger(tmp_path / "approvals.db")
    if case["decision"] == "approve":
        assert ledger.apply(result["request_id"], "CUS-001")["status"] == "already_applied"
    else:
        with pytest.raises(PermissionError):
            ledger.apply(result["request_id"], "CUS-001")
    with pytest.raises(PermissionError):
        ledger.get(result["request_id"], "CUS-002")


async def test_release_gate(tmp_path):
    pytest.importorskip("strands_evals")
    result = await release_report(load_settings(provider="mock"), tmp_path)
    assert result["evaluation_score"] == 1
