"""Vended python_repl replacement, consent gate and BYPASS_TOOL_CONSENT explanation.

Run: uv run python modules/06_community_tools/examples/03_python_with_consent.py --mock
Expected: Lesson complete.
Cost: mock/local $0 hosted inference; live hosted calls use tokens.
AWS required: No; execution environment capability check. Resources created: none.
"""

import tempfile
from pathlib import Path

from strands import Agent
from strands.vended_tools.python_repl import make_python_repl

from common.lessons import complete, lesson_settings
from common.models import get_model
from common.pretty import console, run_cli
from common.reviewed_workspace import APPROVED_CODE, ReviewedWorkspace


def main() -> None:
    args, cfg = lesson_settings()
    with tempfile.TemporaryDirectory(prefix="nimbus-python-") as directory:
        backend = ReviewedWorkspace(Path(directory), (lambda prompt: "no") if args.mock else input)
        repl = make_python_repl(sandbox=backend)
        agent = Agent(
            model=get_model(cfg, responses=[] if args.mock else None),
            tools=[repl],
            callback_handler=None,
        )
        # KEY IDEA: a supplied execution backend checks exact code and asks consent.
        denied = agent.tool.python_repl(code="import os; print(os.environ)")
        assert denied["status"] == "error"
        if args.mock:
            rejected = agent.tool.python_repl(code=APPROVED_CODE)
            assert rejected["status"] == "error"
            backend.consent = lambda prompt: "yes"
        result = agent.tool.python_repl(code=APPROVED_CODE)
        console.print(result)
        console.print(
            "The teaching backend accepts one fixed snippet; it is not arbitrary-code isolation."
        )
    complete()


if __name__ == "__main__":
    run_cli(main)
