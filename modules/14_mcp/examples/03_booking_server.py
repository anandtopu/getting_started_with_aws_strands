"""Booking server: Nimbus Tier 3 lesson.

Run: uv run python modules/14_mcp/examples/03_booking_server.py --mock
Expected: Lesson complete. Offline fixtures cost $0.
Live inference uses configured rates. AWS resources created by this script: none.
"""

import argparse
from pathlib import Path
from tempfile import TemporaryDirectory

from common.config import ROOT
from common.lessons import complete, lesson_settings
from common.mcp_clients import stdio_booking
from common.mcp_server import booking_server
from common.pretty import run_cli


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--serve", action="store_true")
    args, _ = lesson_settings(parser)
    if args.serve:
        booking_server(ROOT / ".nimbus/mcp_bookings.db").run(transport="stdio")
    else:
        with TemporaryDirectory() as directory:
            with stdio_booking(Path(directory) / "mcp.db") as client:
                args = {"flight_id": "FLT-0001", "idempotency_key": "demo-booking"}
                first = client.call_tool_sync("one", "create_booking", args)
                second = client.call_tool_sync("two", "create_booking", args)
                assert first["status"] == second["status"] == "success"
                print(first, second)
        complete()


if __name__ == "__main__":
    run_cli(main)
