"""The exact Lambda handler runs locally: Nimbus production lesson.

Run: uv run --all-groups python modules/20_deployment/examples/04_lambda_handler.py --mock
Expected: Lesson complete. Mock cost/resources: $0 / none.
Live AWS calls require --live-aws where applicable; see module cost and cleanup tables.
"""

from common.lessons import complete, lesson_settings
from common.pretty import run_cli
from common.production_support import lambda_handler


def main() -> None:
    _, cfg = lesson_settings()
    # KEY IDEA: the image uses this same handler, without credentials bundled into it.
    print(lambda_handler({"prompt": "Refund processing time?"}, None, settings=cfg))
    complete()


if __name__ == "__main__":
    run_cli(main)
