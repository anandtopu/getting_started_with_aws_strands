"""Inbound JWT verification and outbound OAuth: Nimbus production lesson.

Run: uv run --all-groups python modules/21_agentcore/examples/03_identity.py --mock
Expected: Lesson complete. Mock cost/resources: $0 / none.
Live AWS calls require --live-aws where applicable; see module cost and cleanup tables.
"""

from common.agentcore_identity import cognito_identity, demo_identity, outbound_oauth
from common.config import course_value
from common.lessons import complete
from common.pretty import run_cli
from common.production_lessons import aws_settings


def main() -> None:
    _, cfg = aws_settings()
    if cfg.provider == "mock":
        print(demo_identity())
        token, workload, provider = "offline-token", "NimbusCopilot", "partner"
    else:
        token = course_value("NIMBUS_ACCESS_TOKEN")
        print(
            cognito_identity(
                cfg, token, course_value("NIMBUS_USER_POOL_ID"), course_value("NIMBUS_CLIENT_ID")
            )
        )
        workload, provider = "NimbusCopilot", course_value("NIMBUS_OAUTH_PROVIDER")
    # KEY IDEA: third-party tokens never enter the agent's context or output.
    print(outbound_oauth(cfg, workload=workload, provider=provider, user_token=token))
    complete()


if __name__ == "__main__":
    run_cli(main)
