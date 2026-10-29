"""Durable approval ledger and replay-safe local mutations; no airline/payment API."""

import json
import sqlite3
import uuid
from contextlib import contextmanager
from pathlib import Path
from time import time

from strands import Agent, tool
from strands.hooks import BeforeToolCallEvent, HookProvider, HookRegistry

from common.models import get_model
from common.testing import tool_message


class ApprovalLedger:
    """Approval and mutation commit atomically in a disposable local SQLite database."""

    def __init__(self, path: Path):
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        with self.transaction() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS bookings (
                    id TEXT PRIMARY KEY, owner TEXT, paid INTEGER, refunded INTEGER,
                    nonrefundable INTEGER, changes INTEGER);
                CREATE TABLE IF NOT EXISTS requests (
                    id TEXT PRIMARY KEY, owner TEXT, booking TEXT, action TEXT, cents INTEGER,
                    expires REAL, needs_approval INTEGER, status TEXT, actor TEXT);
                CREATE TABLE IF NOT EXISTS audit (request TEXT, event TEXT, actor TEXT);
                INSERT OR IGNORE INTO bookings VALUES ('DEMO-001','CUS-001',100000,0,1,0);
                INSERT OR IGNORE INTO bookings VALUES ('DEMO-002','CUS-002',100000,0,0,0);
            """)

    @contextmanager
    def transaction(self):
        db = sqlite3.connect(self.path, timeout=10, isolation_level=None)
        db.row_factory = sqlite3.Row
        try:
            db.execute("BEGIN IMMEDIATE")
            yield db
            db.commit()
        except BaseException:
            db.rollback()
            raise
        finally:
            db.close()

    def propose(self, owner, booking, action, cents, *, now=None, ttl=300):
        if action not in {"refund", "change"} or type(cents) is not int or not 0 <= cents <= 100000:
            raise ValueError("Choose refund/change and integer cents within the demo payment")
        if (action == "refund" and cents == 0) or (action == "change" and cents != 0):
            raise ValueError("Refund must be positive; a fare change uses zero cents")
        with self.transaction() as db:
            row = db.execute(
                "SELECT * FROM bookings WHERE id=? AND owner=?", (booking, owner)
            ).fetchone()
            if row is None:
                raise PermissionError("Booking is outside the authenticated customer scope")
            if cents > row["paid"] - row["refunded"]:
                raise ValueError("Refund exceeds the remaining payment")
            needs = cents > 50000 or (action == "change" and row["nonrefundable"])
            request_id = uuid.uuid4().hex
            db.execute(
                "INSERT INTO requests VALUES (?,?,?,?,?,?,?,?,?)",
                (
                    request_id,
                    owner,
                    booking,
                    action,
                    cents,
                    (time() if now is None else now) + ttl,
                    int(needs),
                    "pending" if needs else "approved",
                    "policy" if not needs else None,
                ),
            )
            db.execute("INSERT INTO audit VALUES (?,?,?)", (request_id, "proposed", owner))
        return request_id

    def get(self, request_id, owner):
        with self.transaction() as db:
            row = db.execute(
                "SELECT * FROM requests WHERE id=? AND owner=?", (request_id, owner)
            ).fetchone()
            if row is None:
                raise PermissionError("Unknown request for this customer")
            return dict(row)

    def decide(self, request_id, owner, decision, *, supervisor, now=None):
        if supervisor != "SUPERVISOR-DEMO":
            raise PermissionError("Supervisor authentication required")
        if decision not in {"approve", "reject"}:
            raise ValueError("Decision must be approve or reject")
        clock = time() if now is None else now
        with self.transaction() as db:
            row = db.execute(
                "SELECT * FROM requests WHERE id=? AND owner=?", (request_id, owner)
            ).fetchone()
            if row is None:
                raise PermissionError("Unknown request for this customer")
            if row["status"] != "pending":
                raise ValueError("Request already decided; create a new request for changed terms")
            status = (
                "expired"
                if row["expires"] <= clock
                else ("approved" if decision == "approve" else "rejected")
            )
            db.execute(
                "UPDATE requests SET status=?,actor=? WHERE id=?", (status, supervisor, request_id)
            )
            db.execute("INSERT INTO audit VALUES (?,?,?)", (request_id, status, supervisor))
        return status

    def apply(self, request_id, owner, *, now=None):
        clock = time() if now is None else now
        with self.transaction() as db:
            row = db.execute(
                "SELECT * FROM requests WHERE id=? AND owner=?", (request_id, owner)
            ).fetchone()
            if row is None:
                raise PermissionError("Unknown request for this customer")
            if row["status"] == "applied":
                return {"status": "already_applied", "request_id": request_id}
            if row["status"] != "approved" or row["expires"] <= clock:
                raise PermissionError("Request is unapproved, rejected or expired")
            if row["action"] == "refund":
                changed = db.execute(
                    "UPDATE bookings SET refunded=refunded+? "
                    "WHERE id=? AND owner=? AND paid-refunded>=?",
                    (row["cents"], row["booking"], owner, row["cents"]),
                ).rowcount
            else:
                changed = db.execute(
                    "UPDATE bookings SET changes=changes+1 WHERE id=? AND owner=?",
                    (row["booking"], owner),
                ).rowcount
            if changed != 1:
                raise ValueError("Booking changed; request requires a fresh review")
            db.execute("UPDATE requests SET status='applied' WHERE id=?", (request_id,))
            db.execute("INSERT INTO audit VALUES (?,?,?)", (request_id, "applied", owner))
        return {"status": "applied", "request_id": request_id}


class SupervisorGate(HookProvider):
    def __init__(self, ledger, request_id, owner):
        self.ledger, self.request_id, self.owner = ledger, request_id, owner

    def register_hooks(self, registry: HookRegistry, **kwargs):
        registry.add_callback(BeforeToolCallEvent, self.check)

    def check(self, event):
        if event.tool_use["name"] != "apply_action":
            return
        if event.tool_use["input"].get("request_id") != self.request_id:
            event.cancel_tool = "The action is not bound to this invocation"
            return
        request = self.ledger.get(self.request_id, self.owner)
        if request["needs_approval"]:
            event.interrupt("supervisor-review", reason=request)
            # A model response or an interrupt string cannot substitute for the durable decision.
        request = self.ledger.get(self.request_id, self.owner)
        if request["status"] not in {"approved", "applied"}:
            event.cancel_tool = "Supervisor did not authorize this request"


def approval_agent(settings, ledger, request_id, owner="CUS-001", *, hooks=(), tools=()):
    @tool
    def apply_action(request_id: str) -> dict:
        """Apply the exact previously reviewed local request; checks approval again at commit."""
        if request_id != bound_id:
            raise PermissionError("Request is not bound to this invocation")
        return ledger.apply(request_id, owner)

    bound_id = request_id
    scripted = []
    if tools:
        scripted.append(
            tool_message("nimbus_search_flights", {"destination": "Porto"}, "alternatives")
        )
    scripted.extend(
        [
            tool_message("apply_action", {"request_id": request_id}),
            "The tool result records the action outcome.",
        ]
    )
    agent = Agent(
        model=get_model(settings, responses=scripted),
        tools=[apply_action, *tools],
        hooks=[SupervisorGate(ledger, request_id, owner), *hooks],
        callback_handler=None,
        retry_strategy=None,
        system_prompt=(
            "Process only the supplied request ID. A rejection is final. "
            "Report tool errors honestly. If flight search is available, first search Porto "
            "for alternatives, then process the request. Never create a new booking."
        ),
    )
    return agent


def responses_for(result):
    return [
        {"interruptResponse": {"interruptId": i.id, "response": "decision recorded"}}
        for i in result.interrupts
    ]


def request_prompt(ledger, request_id):
    return "Apply this request: " + json.dumps(ledger.get(request_id, "CUS-001"))
