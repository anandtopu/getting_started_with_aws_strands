"""Gateway discovery, search and input policy: Nimbus production lesson.

Run: uv run --all-groups python modules/21_agentcore/examples/02_gateway.py --mock
Expected: Lesson complete. Mock cost/resources: $0 / none.
Live AWS calls require --live-aws where applicable; see module cost and cleanup tables.
"""

from common.config import course_value
from common.gateway_booking import gateway_probe
from common.gateway_openapi import openapi_target
from common.lessons import complete
from common.pretty import run_cli
from common.production_lessons import aws_settings


def main() -> None:
    _, cfg = aws_settings()
    request = openapi_target(
        cfg,
        "nimbus-booking-abcdefghij",
        f"https://abc123.execute-api.{cfg.aws_region}.amazonaws.com/demo",
    )
    print("OpenAPI request shape validated locally:", request["name"])
    print("Schema fixture only; registering a target needs a deployed IAM-protected API.")
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
