"""Check the boundary below the vended tools, including rejected consent and HTTP."""

import pytest

from common.reviewed_workspace import APPROVED_CODE, ReviewedWorkspace
from common.tools.travel_day import WEATHER_URL, convert_budget, weather_client


@pytest.mark.asyncio
async def test_consent_denial_path_escape_and_unreviewed_code(tmp_path):
    workspace = ReviewedWorkspace(tmp_path, lambda prompt: "no")
    with pytest.raises(PermissionError, match="declined"):
        await workspace.write_file("/notes.txt", b"private")
    assert not (tmp_path / "notes.txt").exists()
    with pytest.raises(PermissionError, match="outside"):
        workspace.resolve("/../escape.txt")
    with pytest.raises(PermissionError, match="reviewed"):
        await workspace.execute_code("import os", "python3")
    with pytest.raises(PermissionError, match="declined"):
        await workspace.execute_code(APPROVED_CODE, "python3")


@pytest.mark.asyncio
async def test_weather_transport_and_endpoint_allowlist():
    async with weather_client(True) as client:
        response = await client.get(WEATHER_URL)
        assert response.json()["current"]["temperature_2m"] == 18.5
        for method, url in [("POST", WEATHER_URL), ("GET", "https://example.com")]:
            with pytest.raises(PermissionError, match="forecast GET"):
                await client.request(method, url)


def test_decimal_currency_rejects_nonfinite_and_negative():
    assert "92.00" in convert_budget("100", "0.92")
    for amount in ("NaN", "Infinity", "-1", "100001"):
        with pytest.raises(ValueError):
            convert_budget(amount)
