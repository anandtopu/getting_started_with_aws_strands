"""Store consented bounded preferences, expire them, and delete the user footprint.

Run: uv run python modules/09_memory/examples/04_local_preferences.py --mock
Expected: Lesson complete.
Cost: offline $0; live model/embedding calls use configured rates.
AWS resources created by this script: none. Optional labs have separate CDK/cleanup.
"""

import tempfile
from pathlib import Path

from common.lessons import complete, lesson_settings
from common.preferences import Preferences
from common.pretty import console, run_cli


def main() -> None:
    args, cfg = lesson_settings()
    with tempfile.TemporaryDirectory(prefix="nimbus-preferences-") as directory:
        store = Preferences(Path(directory))
        # KEY IDEA: a trusted application identity and consent are outside model arguments.
        store.save("CUS-001", "seat", "aisle", consent=True, now=0)
        store.save("CUS-002", "meal", "vegetarian", consent=True, now=86400)
        console.print("CUS-001:", store.read("CUS-001", now=1))
        console.print("Expired at day 90:", store.read("CUS-001", now=90 * 86400))
        store.delete_user("CUS-001")
        console.print("Other traveler remains:", store.read("CUS-002", now=90 * 86400))
    complete()


if __name__ == "__main__":
    run_cli(main)
