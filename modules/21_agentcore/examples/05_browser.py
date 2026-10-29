"""Browser session reading a synthetic receipt: Nimbus production lesson.

Run: uv run --all-groups python modules/21_agentcore/examples/05_browser.py --mock
Expected: Lesson complete. Mock cost/resources: $0 / none.
Live AWS calls require --live-aws where applicable; see module cost and cleanup tables.
"""

from common.agentcore_tools import builtin_agent
from common.lessons import complete
from common.pretty import run_cli
from common.production_lessons import aws_settings


def main() -> None:
    _, cfg = aws_settings()
    # KEY IDEA: host-owned HTML avoids arbitrary sites, logins and model-selected URLs.
    print(builtin_agent(cfg, "browser"))
    complete()


if __name__ == "__main__":
    run_cli(main)
