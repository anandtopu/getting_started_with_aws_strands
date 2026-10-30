"""Bind approval to reviewed bytes.

Run: uv run python modules/bonus/B3_self_extending/examples/02_review_generated_tool.py --mock
Expected: checked result and Lesson complete. Mock cost $0; no AWS resources.
Live calls use configured provider prices; see this module's README."""

from common.extension_lab import digest, review, template
from common.lessons import complete, lesson_settings
from common.pretty import run_cli


def main() -> None:
    _, cfg = lesson_settings()
    # KEY IDEA: the helper runs the real SDK with explicit boundaries.
    source = template(2500)
    print({"two_bags_cents": review(source, digest(source))(2)})
    complete()


if __name__ == "__main__":
    run_cli(main)
