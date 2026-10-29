"""file_read, file_write, editor and shell with explicit consent and path restrictions.

Run: uv run python modules/06_community_tools/examples/02_files_and_consent.py --mock
Expected: Lesson complete.
Cost: mock/local $0 hosted inference; live hosted calls use tokens.
AWS required: No. Resources created: none.
"""

import tempfile
from pathlib import Path
from unittest.mock import patch

from strands import Agent
from strands.vended_tools.file_editor import make_file_editor
from strands.vended_tools.shell import make_shell
from strands_tools import file_read, file_write

from common.lessons import complete, lesson_settings
from common.models import get_model
from common.pretty import console, run_cli
from common.reviewed_workspace import ReviewedWorkspace


def main() -> None:
    args, cfg = lesson_settings()
    with tempfile.TemporaryDirectory(prefix="nimbus-files-") as directory:
        root = Path(directory)
        consent = (lambda prompt: "yes") if args.mock else input
        backend = ReviewedWorkspace(root, consent)
        tools = [
            make_file_editor(sandbox=backend),
            make_shell(sandbox=backend),
            file_read,
            file_write,
        ]
        agent = Agent(
            model=get_model(cfg, responses=[] if args.mock else None),
            tools=tools,
            callback_handler=None,
        )
        # KEY IDEA: paths/operations are checked below the model, before consent and execution.
        console.print(
            agent.tool.file_editor(command="create", path="/notes.txt", file_text="Lisbon")
        )
        console.print(
            agent.tool.file_editor(
                command="str_replace",
                path="/notes.txt",
                old_str="Lisbon",
                new_str="Lisbon budget EUR 92",
            )
        )
        console.print(agent.tool.shell(command="nimbus-status"))
        console.print(agent.tool.file_read(path=str(root / "notes.txt"), mode="text"))
        # Demonstrate the community writer's own refusal path, never bypass its prompt.
        with patch.object(file_write, "get_user_input", return_value="declined for this demo"):
            result = agent.tool.file_write(path=str(root / "declined.txt"), content="Not written")
        assert not (root / "declined.txt").exists()
        console.print("Community file_write consent refusal:", result["status"])
    complete()


if __name__ == "__main__":
    run_cli(main)
