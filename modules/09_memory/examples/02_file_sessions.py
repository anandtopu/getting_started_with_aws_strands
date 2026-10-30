"""Resume file sessions with an application-derived customer namespace.

Run: uv run python modules/09_memory/examples/02_file_sessions.py --mock
Expected: Lesson complete.
Cost: offline $0; live model/embedding calls use configured rates.
AWS resources created by this script: none. Optional labs have separate CDK/cleanup.
"""

import tempfile
from pathlib import Path

from strands import Agent

from common.lessons import complete, lesson_settings
from common.models import get_model
from common.preferences import Preferences
from common.pretty import console, run_cli


def main() -> None:
    args, cfg = lesson_settings()
    with tempfile.TemporaryDirectory(prefix="nimbus-sessions-") as directory:
        preferences = Preferences(Path(directory))
        first_manager = preferences.session("CUS-001", "trip")
        first = Agent(
            model=get_model(cfg, responses=["Lisbon recorded."]),
            callback_handler=None,
            session_manager=first_manager,
        )
        first("I am planning Lisbon. Acknowledge in one short sentence.", limits={"turns": 2})
        # KEY IDEA: a new Agent restores history through the same scoped session ID.
        resumed = Agent(
            model=get_model(cfg, responses=["Lisbon."]),
            callback_handler=None,
            session_manager=preferences.session("CUS-001", "trip"),
        )
        console.print("Restored messages:", len(resumed.messages))
        result = resumed("Which city?", limits={"turns": 2})
        other = preferences.session("CUS-002", "trip")
        console.print("Different customer session:", other.session_id != first_manager.session_id)
        complete(result, cfg)


if __name__ == "__main__":
    run_cli(main)
