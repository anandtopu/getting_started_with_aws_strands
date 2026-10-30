"""Reviewing and replacing generated tools use case.

Run: uv run python modules/bonus/B3_self_extending/use_case/reviewed_tool_builder.py --mock
Expected: checked result and Lesson complete. Mock cost $0; no AWS resources.
Live calls use configured provider prices; see this module's README."""

from common.config import ROOT
from common.extension_lab import reload_demo
from common.lessons import complete, lesson_settings
from common.pretty import run_cli


def main() -> None:
    _, cfg = lesson_settings()
    # KEY IDEA: the helper runs the real SDK with explicit boundaries.
    print(reload_demo(cfg, ROOT / ".nimbus/reviewed-tools"))
    complete()


if __name__ == "__main__":
    run_cli(main)
