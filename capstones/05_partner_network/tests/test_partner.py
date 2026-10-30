"""Actual LangGraph/A2A process integration and strict returned-offer validation."""

import json
from pathlib import Path

import pytest

from common.config import load_settings
from common.partner_client import UpgradeOffer


def test_offer_rejection():
    case = json.loads((Path(__file__).parents[1] / "evaluation.json").read_text())
    expected = {"offer_id": "UP-001", **case["expected"]}
    assert UpgradeOffer.model_validate(expected).quote_only
    for variant in case["rejected_variants"]:
        with pytest.raises(ValueError):
            UpgradeOffer.model_validate({**expected, **variant})


async def test_langgraph_partner_process():
    pytest.importorskip("a2a")
    pytest.importorskip("langgraph")
    from common.partner_client import ask_partner, partner_process

    with partner_process(load_settings(provider="mock"), backend="langgraph") as (url, token):
        result = await ask_partner(url, token, streaming=True)
    assert result["offer"]["cents"] == 7500
    assert result["events"]
