"""SSM configuration and Secrets Manager transport credentials: Nimbus production lesson.

Run: uv run --all-groups python modules/20_deployment/examples/06_runtime_configuration.py --mock
Expected: Lesson complete. Mock cost/resources: $0 / none.
Live AWS calls require --live-aws where applicable; see module cost and cleanup tables.
"""

from common.config import course_value
from common.deployment_calls import runtime_configuration
from common.lessons import complete
from common.pretty import run_cli
from common.production_lessons import aws_settings


def main() -> None:
    _, cfg = aws_settings()
    parameter = (
        "/nimbus/service" if cfg.provider == "mock" else course_value("NIMBUS_SERVICE_PARAMETER")
    )
    secret = "nimbus-token" if cfg.provider == "mock" else course_value("NIMBUS_API_SECRET_ARN")
    # KEY IDEA: only a loaded/not-loaded flag leaves the credential boundary.
    print(runtime_configuration(cfg, parameter, secret))
    complete()


if __name__ == "__main__":
    run_cli(main)
