"""Refund policy boundary: Nimbus production lesson.

Run: uv run --all-groups python modules/21_agentcore/examples/07_policy.py --mock
Expected: Lesson complete. Mock cost/resources: $0 / none.
Live AWS calls require --live-aws where applicable; see module cost and cleanup tables.
"""

from common.config import course_value
from common.gateway_booking import gateway_probe
from common.lessons import complete
from common.pretty import run_cli
from common.production_lessons import aws_settings


def main() -> None:
    _, cfg = aws_settings()
    # KEY IDEA: the server enforces the amount limit even if the model asks for more.
    print(
        gateway_probe(
            cfg,
            url=course_value("AGENTCORE_GATEWAY_URL"),
            token=course_value("NIMBUS_ACCESS_TOKEN"),
        )
    )
    complete()


if __name__ == "__main__":
    run_cli(main)
