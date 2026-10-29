"""Official MCP 2.x server for synthetic reservations. Never talks to an airline."""

import argparse
import os
import secrets
import sqlite3
import uuid
from contextlib import closing
from pathlib import Path

from mcp.server.mcpserver import MCPServer

from common.config import ROOT
from common.data import load_csv


def booking_server(database: Path):
    if database.resolve().is_relative_to(ROOT / "data"):
        raise ValueError("Use a disposable database outside committed data")
    database.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(database)) as db, db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS reservations
            (key TEXT PRIMARY KEY, id TEXT, owner TEXT, flight TEXT, cents INTEGER);
        """)
    catalog = {r["flight_id"]: r for r in load_csv("flights.csv")}
    server = MCPServer("NimbusBookings", log_level="ERROR")

    @server.tool()
    def search_flights(destination: str = "Porto") -> list[dict]:
        """Return up to three synthetic flights; a search never reserves a seat."""
        return [
            {k: r[k] for k in ("flight_id", "origin", "destination", "price_usd")}
            for r in catalog.values()
            if r["destination"].casefold() == destination.casefold()
        ][:3]

    @server.tool()
    def create_booking(flight_id: str, idempotency_key: str) -> dict:
        """Reserve one synthetic seat for the server's fixed CUS-001 demo identity."""
        if flight_id not in catalog or not 1 <= len(idempotency_key) <= 64:
            raise ValueError("Unknown flight or invalid idempotency key")
        from decimal import Decimal

        cents = int(Decimal(catalog[flight_id]["price_usd"]) * 100)
        with closing(sqlite3.connect(database, timeout=10)) as db, db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute(
                "SELECT id,flight FROM reservations WHERE key=?", (idempotency_key,)
            ).fetchone()
            if row:
                if row[1] != flight_id:
                    raise ValueError("Idempotency key is already bound to different terms")
                return {"booking_id": row[0], "status": "already_reserved"}
            count = db.execute(
                "SELECT count(*) FROM reservations WHERE flight=?", (flight_id,)
            ).fetchone()[0]
            if count >= int(catalog[flight_id]["seats_left"]):
                raise ValueError("No synthetic seats remain")
            booking_id = "LOCAL-" + uuid.uuid4().hex[:12]
            db.execute(
                "INSERT INTO reservations VALUES (?,?,?,?,?)",
                (idempotency_key, booking_id, "CUS-001", flight_id, cents),
            )
            return {"booking_id": booking_id, "status": "reserved", "cents": cents}

    @server.tool()
    def get_booking(booking_id: str) -> dict:
        """Read a reservation owned by the server's fixed synthetic customer."""
        with closing(sqlite3.connect(database)) as db:
            row = db.execute(
                "SELECT flight,cents FROM reservations WHERE id=? AND owner='CUS-001'",
                (booking_id,),
            ).fetchone()
        if row is None:
            raise ValueError("Unknown reservation for this customer")
        return {"booking_id": booking_id, "flight_id": row[0], "cents": row[1]}

    return server


class BearerOnly:
    """Loopback demo authentication; production MCP requires its OAuth security model."""

    def __init__(self, app, token, shutdown=None):
        self.app, self.token, self.shutdown = app, token, shutdown

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            header = dict(scope["headers"]).get(b"authorization", b"").decode()
            if not secrets.compare_digest(header, "Bearer " + self.token):
                await send({"type": "http.response.start", "status": 401, "headers": []})
                await send({"type": "http.response.body", "body": b"Authentication required"})
                return
            if scope["path"] == "/_shutdown" and scope["method"] == "POST" and self.shutdown:
                self.shutdown()
                await send({"type": "http.response.start", "status": 200, "headers": []})
                await send({"type": "http.response.body", "body": b"Stopping local demo"})
                return
        await self.app(scope, receive, send)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", type=Path, required=True)
    parser.add_argument("--port", type=int)
    args = parser.parse_args()
    server = booking_server(args.database)
    if args.port is None:
        server.run(transport="stdio")
    else:
        import uvicorn

        token = os.environ.get("NIMBUS_SERVER_TOKEN")
        if not token:
            raise ValueError("HTTP server requires a random local bearer token")
        app = server.streamable_http_app(stateless_http=True, json_response=True)

        def shutdown():
            runner.should_exit = True

        runner = uvicorn.Server(
            uvicorn.Config(
                BearerOnly(app, token, shutdown),
                host="127.0.0.1",
                port=args.port,
                log_level="error",
                access_log=False,
            )
        )
        runner.run()


if __name__ == "__main__":
    # The child process also blocks external networking during offline verification.
    from contextlib import nullcontext

    from common.network import offline_network

    with offline_network() if os.environ.get("NIMBUS_OFFLINE") == "1" else nullcontext():
        main()
