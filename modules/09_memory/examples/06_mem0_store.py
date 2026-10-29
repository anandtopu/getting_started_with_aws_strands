"""Use the supported Mem0 store and MemoryManager, then delete the scoped backend data.

Run: uv run --group memory python modules/09_memory/examples/06_mem0_store.py --mock
Expected: Lesson complete.
Cost: offline $0; live model/embedding calls use configured rates.
AWS resources created by this script: none. Optional labs have separate CDK/cleanup.
"""

import asyncio
import tempfile
from pathlib import Path

from strands.memory import MemoryManager

from common.lessons import complete, lesson_settings
from common.memory_adapters import mem0_store
from common.preferences import user_key
from common.pretty import console, run_cli


def main() -> None:
    args, cfg = lesson_settings()
    with tempfile.TemporaryDirectory(prefix="nimbus-mem0-") as directory:
        store, backend = mem0_store("CUS-001", mock=args.mock, directory=Path(directory))
        try:
            # KEY IDEA: explicit facts avoid unbounded automatic conversation extraction.
            manager = MemoryManager(stores=[store], injection=False)
            asyncio.run(manager.add("Traveler prefers vegetarian meals."))
            console.print("Scoped recall:", asyncio.run(manager.search("meal preference")))
            backend.delete_all(user_id=user_key("CUS-001"))
            assert not asyncio.run(manager.search("meal preference"))
            console.print("Mem0 scoped deletion verified.")
        finally:
            if not args.mock:
                backend.close()
                backend.vector_store.client.close()
    complete()


if __name__ == "__main__":
    run_cli(main)
