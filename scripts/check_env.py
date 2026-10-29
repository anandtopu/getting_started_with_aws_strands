"""Check readiness; default mode is offline and makes no AWS/model calls.

Run: uv run python scripts/check_env.py
Expected: Python/package/configuration report. Cost: $0 unless --probe.
AWS resources: none. --aws reads identity/access; --probe makes one model call.
"""

import argparse
import importlib.metadata
import sys

import httpx

from common.config import CourseError, Settings, load_settings
from common.pretty import console, run_cli


def check_ollama(settings: Settings) -> None:
    response = httpx.get(settings.ollama_host.rstrip("/") + "/api/tags", timeout=5)
    response.raise_for_status()
    names = {entry["name"] for entry in response.json().get("models", [])}
    if settings.model_id not in names:
        raise CourseError(
            f"Ollama is running. Pull the configured model: ollama pull {settings.model_id}"
        )
    console.print("Ollama is reachable and the configured model is installed.")


def check_aws(settings: Settings) -> None:
    import boto3
    from botocore.config import Config

    session = boto3.Session(
        profile_name=settings.aws_profile or None, region_name=settings.aws_region
    )
    config = Config(connect_timeout=5, read_timeout=10, retries={"max_attempts": 1})
    identity = session.client("sts", config=config).get_caller_identity()
    if identity["Arn"].endswith(":root"):
        raise CourseError("Root identity detected. Sign in through IAM Identity Center instead.")
    console.print(
        f"AWS identity verified in {settings.aws_region}; account details are not printed."
    )
    bedrock = session.client("bedrock", config=config)
    model_id = settings.model_id
    if model_id.startswith(("us.", "eu.", "apac.", "global.", "jp.")):
        profile = bedrock.get_inference_profile(inferenceProfileIdentifier=model_id)
        console.print(f"Inference profile status: {profile['status']}")
        model_id = profile["models"][0]["modelArn"].split("/")[-1]
    available = bedrock.get_foundation_model_availability(modelId=model_id)
    for key in ("authorizationStatus", "entitlementAvailability", "regionAvailability"):
        console.print(f"{key}: {available.get(key, 'not reported')}", markup=False)
    console.print(
        "Readiness is advisory; only an explicitly requested inference probe tests a call."
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--aws", action="store_true")
    parser.add_argument("--ollama", action="store_true")
    parser.add_argument("--probe", action="store_true")
    parser.add_argument("--accept-cost", action="store_true")
    args = parser.parse_args()
    if not (3, 12) <= sys.version_info[:2] < (3, 14):
        raise CourseError("Use Python 3.12 (recommended) or 3.13.")
    settings = load_settings()
    console.print(f"Python {sys.version.split()[0]}; provider={settings.provider}")
    for package in ("strands-agents", "strands-agents-tools", "pydantic", "boto3", "ollama"):
        console.print(f"{package}: {importlib.metadata.version(package)}")
    console.print("Configuration parsed. Secrets are never displayed.")
    if args.aws:
        if settings.provider != "bedrock":
            raise CourseError("Select MODEL_PROVIDER=bedrock before the AWS model-readiness check.")
        check_aws(settings)
    if args.ollama:
        if settings.provider != "ollama":
            raise CourseError("Select MODEL_PROVIDER=ollama before the Ollama model check.")
        check_ollama(settings)
    if args.probe:
        if not args.accept_cost:
            raise CourseError(
                "A model probe can be billable. Add --accept-cost after setting a budget."
            )
        from strands import Agent

        from common.models import get_model

        probe_settings = settings.model_copy(update={"max_tokens": 64})
        result = Agent(model=get_model(probe_settings), callback_handler=None)(
            "Say Nimbus is ready."
        )
        console.print(str(result), markup=False)
    if not (args.aws or args.ollama or args.probe):
        console.print(
            "Offline checks passed. Credentials, model access and services were NOT contacted."
        )


if __name__ == "__main__":
    run_cli(main)
