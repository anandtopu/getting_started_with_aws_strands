"""BedrockModel; model ID, region, boto3 profile/session, temperature, max tokens and inference
profiles.

Run: uv run python modules/02_model_providers/examples/01_bedrock_settings.py --mock
Expected: Lesson complete.
Cost: mock/local $0 hosted inference; live hosted calls use tokens.
AWS required: Yes; other providers instead. Resources created: none.
"""

import boto3
from strands.models import BedrockModel

from common.config import load_settings
from common.lessons import complete, lesson_settings, require_bedrock
from common.models import get_model
from common.pretty import console, run_cli


def main() -> None:
    args, cfg = lesson_settings()
    target = load_settings(provider="bedrock")
    if args.mock:
        session = boto3.Session(
            aws_access_key_id="testing",
            aws_secret_access_key="testing",
            region_name=target.aws_region,
        )
        # Construction contract only: no credentials are looked up and no call is made.
        model = BedrockModel(
            boto_session=session, model_id=target.model_id, temperature=0, max_tokens=128
        )
    else:
        require_bedrock(cfg)
        model = get_model(cfg)
    # KEY IDEA: set region on the boto3 session when supplying boto_session.
    console.print({k: model.get_config()[k] for k in ["model_id", "temperature", "max_tokens"]})
    complete()


if __name__ == "__main__":
    run_cli(main)
