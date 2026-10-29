"""Small CLI conveniences; agent construction stays visible in each lesson."""

import argparse
from typing import Any

from common.config import CourseError, Settings, load_settings
from common.pretty import console, print_result


def lesson_settings(parser: argparse.ArgumentParser | None = None) -> tuple[Any, Settings]:
    parser = parser or argparse.ArgumentParser()
    parser.add_argument(
        "--mock", action="store_true", help="Replay fixtures without external calls"
    )
    args = parser.parse_args()
    return args, load_settings(provider="mock" if args.mock else None)


def complete(result: Any = None, settings: Settings | None = None) -> None:
    if result is not None and settings is not None:
        print_result(result, settings)
    console.print("Lesson complete.")


def require_bedrock(settings: Settings) -> None:
    if settings.provider != "bedrock":
        raise CourseError("AWS required: select Bedrock or use --mock for the offline contract.")
