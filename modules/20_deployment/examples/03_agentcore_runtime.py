"""Invoke Runtime with an isolated session: Nimbus production lesson.

Run: uv run --all-groups python modules/20_deployment/examples/03_agentcore_runtime.py --mock
Expected: Lesson complete. Mock cost/resources: $0 / none.
Live AWS calls require --live-aws where applicable; see module cost and cleanup tables.
"""

from common.config import course_value
from common.deployment_calls import invoke_runtime
from common.lessons import complete
from common.pretty import run_cli
from common.production_lessons import aws_settings


def main() -> None:
    _, cfg = aws_settings()
    arn = (
        "arn:aws:bedrock-agentcore:us-east-1:111122223333:runtime/nimbus-AbCdEf1234"
        if cfg.provider == "mock"
        else course_value("AGENTCORE_RUNTIME_ARN")
    )
    # KEY IDEA: a new UUID isolates runtime hosting; conversation persistence is separate.
    print(invoke_runtime(cfg, arn))
    complete()


if __name__ == "__main__":
    run_cli(main)
