"""Code Interpreter with fixed reviewed Python: Nimbus production lesson.

Run: uv run --all-groups python modules/21_agentcore/examples/04_code_interpreter.py --mock
Expected: Lesson complete. Mock cost/resources: $0 / none.
Live AWS calls require --live-aws where applicable; see module cost and cleanup tables.
"""

from common.agentcore_tools import builtin_agent
from common.lessons import complete
from common.pretty import run_cli
from common.production_lessons import aws_settings


def main() -> None:
    _, cfg = aws_settings()
    # KEY IDEA: executeCode is the confirmed API method; stop in finally on every outcome.
    print(builtin_agent(cfg, "code"))
    complete()


if __name__ == "__main__":
    run_cli(main)
