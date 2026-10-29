"""Explicit AWS opt-in and hosting decisions for the production lessons."""

import argparse

from common.lessons import lesson_settings


def aws_settings(parser=None):
    parser = parser or argparse.ArgumentParser()
    parser.add_argument(
        "--live-aws", action="store_true", help="Call existing AWS resources; may incur cost"
    )
    args, cfg = lesson_settings(parser)
    if not args.mock and not args.live_aws:
        parser.error("Choose --mock for free contracts or --live-aws for existing AWS resources")
    return args, cfg


def choose_host(*, seconds, streaming, managed_sessions, local):
    if seconds <= 0:
        raise ValueError("Work duration must be positive")
    if local:
        return "local"
    if managed_sessions:
        return "AgentCore Runtime"
    if streaming or seconds > 900:
        return "Fargate"
    return "Lambda"
