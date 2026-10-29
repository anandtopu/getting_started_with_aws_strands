"""Explicitly configured AWS clients; offline contracts inject test credentials only."""

import boto3
from botocore.config import Config

from common.config import Settings


def session(settings: Settings):
    if settings.provider == "mock":
        return boto3.Session(
            aws_access_key_id="testing",
            aws_secret_access_key="testing",
            region_name=settings.aws_region,
        )
    return boto3.Session(region_name=settings.aws_region, profile_name=settings.aws_profile or None)


def client(service: str, settings: Settings):
    return session(settings).client(
        service, config=Config(connect_timeout=5, read_timeout=30, retries={"max_attempts": 1})
    )
