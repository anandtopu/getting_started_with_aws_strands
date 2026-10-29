"""Class-based tools sharing a database connection; read-only queries.

Run: uv run python modules/05_building_tools/examples/05_resource_sharing.py --mock
Expected: Lesson complete.
Cost: mock/local $0 hosted inference; live hosted calls use tokens.
AWS required: No. Resources created: none.
"""

import sqlite3
import threading
from contextlib import closing

from strands import Agent, tool

from common.data import data_path
from common.lessons import complete, lesson_settings
from common.models import get_model
from common.pretty import console, run_cli


class BookingDesk:
    def __init__(self, connection):
        self.connection = connection
        self.lock = threading.Lock()

    @tool
    def booking_total(self, booking_id: str) -> int:
        """Read a synthetic booking total in cents.

        Args:
            booking_id: Booking ID in the demo database; use only synthetic fixtures.
        """
        with self.lock:
            row = self.connection.execute(
                "SELECT total_cents FROM bookings WHERE booking_id=?", (booking_id,)
            ).fetchone()
        if row is None:
            raise ValueError("Unknown booking")
        return row[0]


def main() -> None:
    _, cfg = lesson_settings()
    # KEY IDEA: SDK calls run on another thread; serialize access to this shared read-only handle.
    with closing(
        sqlite3.connect(
            data_path("bookings.db").as_uri() + "?mode=ro", uri=True, check_same_thread=False
        )
    ) as connection:
        desk = BookingDesk(connection)
        agent = Agent(
            model=get_model(cfg, responses=[] if cfg.provider == "mock" else None),
            tools=[desk.booking_total],
            callback_handler=None,
        )
        result = agent.tool.booking_total(booking_id="BKG-0001")
        console.print(result)
        assert result["status"] == "success"
    console.print(
        "For model-driven concurrent tools, open one connection per call as booking.py does."
    )
    complete()


if __name__ == "__main__":
    run_cli(main)
