"""Remember explicit traveler preferences across new sessions and demonstrate deletion.

Run: uv run python modules/09_memory/use_case/preferences_assistant.py --mock
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
    with tempfile.TemporaryDirectory(prefix="nimbus-traveler-") as directory:
        store = Preferences(Path(directory))
        for name, value in {"seat": "aisle", "meal": "vegetarian", "budget_usd": "600"}.items():
            store.save("CUS-001", name, value, consent=True)
        # KEY IDEA: select only approved preference fields for the new session.
        selected = store.read("CUS-001")
        agent = Agent(
            model=get_model(
                cfg, responses=["Aisle, vegetarian meals, budget $600. Please confirm dates."]
            ),
            session_manager=store.session("CUS-001", "new-trip"),
            callback_handler=None,
            system_prompt=f"Nimbus planner. Confirm these possibly stale preferences: {selected}",
        )
        result = agent("Start a new trip.", limits={"turns": 2})
        complete(result, cfg)
        store.delete_user("CUS-001")
        assert store.read("CUS-001") == {}
        console.print("Traveler preferences and registered sessions deleted.")


if __name__ == "__main__":
    run_cli(main)
