"""The hand-built adapter and cost calculation satisfy the taught contract."""

import runpy

from strands import Agent

from common.config import ROOT


def test_minimal_model_emits_real_sdk_result():
    source = runpy.run_path(str(ROOT / "modules/02_model_providers/examples/04_custom_model.py"))
    model = source["OneSentenceModel"]()
    config = model.get_config()
    config["temperature"] = 9
    assert model.get_config()["temperature"] == 0
    result = Agent(model=model, callback_handler=None)("Help a traveler")
    assert str(result).strip() == "Nimbus asks for your destination."
    assert result.metrics.accumulated_usage["totalTokens"] == 17
