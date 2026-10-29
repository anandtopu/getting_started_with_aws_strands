"""Short-term events and long-term preferences: Nimbus production lesson.

Run: uv run --all-groups python modules/21_agentcore/examples/01_memory.py --mock
Expected: Lesson complete. Mock cost/resources: $0 / none.
Live AWS calls require --live-aws where applicable; see module cost and cleanup tables.
"""

from common.agentcore_memory import preferences
from common.config import course_value
from common.lessons import complete
from common.pretty import run_cli
from common.production_lessons import aws_settings


def main() -> None:
    _, cfg = aws_settings()
    memory = (
        "NimbusDemo-1234567890" if cfg.provider == "mock" else course_value("AGENTCORE_MEMORY_ID")
    )
    # KEY IDEA: this standalone synthetic demo binds CUS-001 in trusted host code.
    print(preferences(cfg, memory, "CUS-001"))
    complete()


if __name__ == "__main__":
    run_cli(main)
