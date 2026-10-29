"""Prompt injection: Nimbus Tier 3 lesson.

Run: uv run python modules/13_guardrails/examples/02_prompt_injection.py --mock
Expected: Lesson complete. Offline fixtures cost $0.
Live inference uses configured rates. AWS resources created by this script: none.
"""

from common.lessons import complete, lesson_settings
from common.pretty import run_cli
from common.safety import injection_trial


def main():
    _, cfg = lesson_settings()
    for hardened in (False, True):
        report = injection_trial(cfg, hardened=hardened)
        print("Boundary enabled:", hardened, report)
        if hardened:
            assert not report["tool_executed"]
    print("Mock mode forces an attempted attack; live model behavior may differ.")
    complete()


if __name__ == "__main__":
    run_cli(main)
