"""Exercise real SDK extension behavior and the Runtime-hosted capstone boundary."""

import json

import pytest

from common.config import ROOT, Settings


@pytest.mark.asyncio
async def test_recorded_barge_in_discards_audio_and_closes():
    from common.voice_lab import voice_session

    report = await voice_session(Settings(provider="mock"))
    assert report["queued_audio_chunks"] == 0
    assert report["requests"] == ["pending_human_review"]
    assert report["stopped"] and not report["booked"]
    assert any("barge" in event.lower() for event in report["events"])


def test_generated_tool_tampering_and_actual_replacement(tmp_path):
    from common.extension_lab import digest, reload_demo, review, template

    with pytest.raises(PermissionError):
        review(template(3000), digest(template(2500)))
    malicious = 'print("unreviewed")'
    with pytest.raises(PermissionError):
        review(malicious, digest(malicious))
    report = reload_demo(Settings(provider="mock"), tmp_path)
    assert [r["cents"] for r in report["versions"]] == [5000, 6000]
    assert "6000" in json.dumps(report["updated_tool_result"])
    assert not report["auto_execute_generated_code"]


@pytest.mark.asyncio
async def test_public_cancellation_and_middleware():
    from common.release_lab import cancellation, middleware

    cfg = Settings(provider="mock")
    assert (await cancellation(cfg))["stop_reason"] == "cancelled"
    assert (await middleware(cfg))["stages"] == [
        "model:start",
        "model:stop",
        "tool:start",
        "tool:stop",
        "model:start",
        "model:stop",
    ]


@pytest.mark.asyncio
async def test_stable_redteam_and_experimental_config():
    pytest.importorskip("strands_evals")
    from common.release_lab import experimental_config, redteam

    report = await redteam(Settings(provider="mock"))
    assert report["cases"] == 3 and report["breaches"] == 0
    assert experimental_config(Settings(provider="mock"))["experimental"]


@pytest.mark.asyncio
async def test_runtime_hosts_memory_gateway_and_policy_without_returning_token():
    pytest.importorskip("bedrock_agentcore")
    pytest.importorskip("jwt")
    import httpx

    from common.deployment_apps import runtime_app

    token = "offline-credential-must-not-be-echoed"
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=runtime_app(Settings(provider="mock"))),
        base_url="http://localhost",
    ) as client:
        response = await client.post(
            "/invocations",
            json={
                "operation": "copilot",
                "access_token": token,
                "prompt": "Review my refund and Porto trip",
            },
        )
    assert response.status_code == 200
    for tool in ("search_policies", "recall_preferences", "nimbus___search_flights"):
        assert tool in response.text
    assert token not in response.text
    assert '"payment_executed": false' in response.text


def test_runtime_authentication_failure_precedes_service_access(monkeypatch):
    from common import flagship_runtime

    def deny(*args):
        raise ValueError("Invalid signed token")

    def no_service(*args, **kwargs):
        pytest.fail("Must authenticate before opening Gateway or Memory")

    monkeypatch.setattr(flagship_runtime, "cognito_identity", deny)
    monkeypatch.setattr(flagship_runtime, "gateway_client", no_service)
    monkeypatch.setattr(flagship_runtime, "preferences", no_service)
    with pytest.raises(ValueError, match="Invalid signed token"):
        flagship_runtime.hosted_copilot(
            {"operation": "copilot", "access_token": "invalid", "prompt": "Quote"}, Settings()
        )


def test_every_bonus_delivers_the_lesson_contract():
    for folder in (ROOT / "modules/bonus").iterdir():
        extension = "ts" if folder.name == "B2_typescript" else "py"
        assert len(list((folder / "examples").glob(f"*.{extension}"))) >= 3
        for name in ("exercises", "solutions"):
            assert len(list((folder / name).glob(f"*.{extension}"))) == 3
        for name in ("README.md", "quiz.md", "notebook.ipynb"):
            assert (folder / name).is_file()
        assert len(list((folder / "use_case").glob(f"*.{extension}"))) == 1
        assert list((folder / "tests").glob(f"*.{extension}"))
