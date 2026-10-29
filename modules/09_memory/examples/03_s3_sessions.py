"""Round-trip S3 sessions with moto; live mode uses an existing tagged bucket.

Run: uv run python modules/09_memory/examples/03_s3_sessions.py --mock
Expected: Lesson complete.
Cost: offline $0; live model/embedding calls use configured rates.
AWS resources created by this script: none. Optional labs have separate CDK/cleanup.
"""

from contextlib import nullcontext

import boto3
from moto import mock_aws
from strands import Agent
from strands.session.s3_session_manager import S3SessionManager

from common.config import course_value, load_settings
from common.lessons import complete, lesson_settings
from common.models import get_model
from common.pretty import console, run_cli


def main() -> None:
    args, cfg = lesson_settings()
    target = load_settings(provider="bedrock")
    context = mock_aws() if args.mock else nullcontext()
    with context:
        session = boto3.Session(
            region_name=target.aws_region,
            **(
                {"aws_access_key_id": "testing", "aws_secret_access_key": "testing"}
                if args.mock
                else {"profile_name": target.aws_profile or None}
            ),
        )
        bucket = "nimbus-session-fixture" if args.mock else course_value("NIMBUS_SESSION_BUCKET")
        if not bucket:
            raise ValueError("Set NIMBUS_SESSION_BUCKET after deploying the optional session lab")
        if args.mock:
            session.client("s3").create_bucket(
                Bucket=bucket,
                **(
                    {}
                    if target.aws_region == "us-east-1"
                    else {"CreateBucketConfiguration": {"LocationConstraint": target.aws_region}}
                ),
            )

        def manager():
            return S3SessionManager(
                "demo-trip", bucket=bucket, prefix="CUS-001", boto_session=session
            )

        first = Agent(
            model=get_model(cfg, responses=["Budget saved in this session."]),
            session_manager=manager(),
            callback_handler=None,
        )
        first("My budget is 600 dollars.", limits={"turns": 2})
        # KEY IDEA: a new manager reads the persisted messages; moto exercises actual S3 requests.
        restored = Agent(
            model=get_model(cfg, responses=[] if args.mock else None),
            session_manager=manager(),
            callback_handler=None,
        )
        assert len(restored.messages) == 2
        console.print("S3 restored messages:", len(restored.messages))
        manager().delete_session("demo-trip")
        console.print("Demo session deleted; bucket cleanup belongs to the infrastructure lab.")
    complete()


if __name__ == "__main__":
    run_cli(main)
