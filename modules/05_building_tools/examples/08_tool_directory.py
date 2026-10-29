"""Trusted folder loading, hot reload and review before registration.

Run: uv run python modules/05_building_tools/examples/08_tool_directory.py --mock
Expected: Lesson complete.
Cost: mock/local $0 hosted inference; live hosted calls use tokens.
AWS required: No. Resources created: none.
"""

import contextlib

from strands import Agent

from common.config import ROOT
from common.lessons import complete, lesson_settings
from common.models import get_model
from common.pretty import console, run_cli


def main() -> None:
    _, cfg = lesson_settings()
    folder = ROOT / ".nimbus/tool_reload"
    (folder / "tools").mkdir(parents=True, exist_ok=True)
    tool_path = folder / "tools/nimbus_status.py"
    original = (
        "from strands import tool\n@tool\ndef nimbus_status() -> str:\n"
        '    "Read reviewed Nimbus status."\n'
        "    return 'ready'\n"
    )
    tool_path.write_text(original, encoding="utf-8")
    # KEY IDEA: importing a tool file executes Python. Only load operator-reviewed code.
    with contextlib.chdir(folder):
        agent = Agent(
            model=get_model(cfg, responses=[] if cfg.provider == "mock" else None),
            load_tools_from_directory=True,
            callback_handler=None,
        )
        console.print(agent.tool.nimbus_status())
        tool_path.write_text(
            original.replace("'ready'", "'updated and reviewed'"), encoding="utf-8"
        )
        # Explicit reload makes the walkthrough deterministic; the watcher also reloads on edits.
        agent.tool_registry.reload_tool("nimbus_status")
        result = agent.tool.nimbus_status()
        assert "updated and reviewed" in str(result)
        console.print(result)
        agent.cleanup()
    complete()


if __name__ == "__main__":
    run_cli(main)
