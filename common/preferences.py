"""Explicit, scoped preference storage with retention and logical user deletion."""

import hashlib
import re
import sqlite3
from contextlib import closing
from pathlib import Path
from time import time

from strands.session.file_session_manager import FileSessionManager


def user_key(user_id: str) -> str:
    if not re.fullmatch(r"CUS-\d{3}", user_id):
        raise ValueError("Use an authenticated synthetic customer ID")
    return hashlib.sha256(user_id.encode()).hexdigest()[:24]


class Preferences:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.database = self.root / "preferences.db"
        with closing(self.connect()) as db, db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS preferences "
                "(owner TEXT, name TEXT, value TEXT, expires REAL, PRIMARY KEY(owner,name))"
            )
            db.execute(
                "CREATE TABLE IF NOT EXISTS sessions "
                "(owner TEXT, session TEXT, PRIMARY KEY(owner,session))"
            )

    def connect(self):
        db = sqlite3.connect(self.database)
        db.execute("PRAGMA secure_delete=ON")
        return db

    def save(self, user_id: str, name: str, value: str, *, consent: bool, now: float | None = None):
        if consent is not True:
            raise PermissionError("Preference storage requires explicit consent")
        choices = {"seat": {"aisle", "window"}, "meal": {"vegetarian", "standard"}}
        if name == "budget_usd":
            valid = value.isdecimal() and 1 <= int(value) <= 2000
        else:
            valid = value in choices.get(name, set())
        if not valid:
            raise ValueError("Only bounded seat, meal and budget preferences may be stored")
        with closing(self.connect()) as db, db:
            db.execute(
                "INSERT OR REPLACE INTO preferences VALUES (?,?,?,?)",
                (user_key(user_id), name, value, (time() if now is None else now) + 90 * 86400),
            )

    def read(self, user_id: str, *, now: float | None = None) -> dict:
        clock = time() if now is None else now
        with closing(self.connect()) as db, db:
            db.execute("DELETE FROM preferences WHERE expires<=?", (clock,))
            return dict(
                db.execute("SELECT name,value FROM preferences WHERE owner=?", (user_key(user_id),))
            )

    def session(self, user_id: str, session_id: str) -> FileSessionManager:
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,50}", session_id):
            raise ValueError("Session ID must be a short safe identifier")
        owner = user_key(user_id)
        scoped = f"{owner}-{session_id}"
        with closing(self.connect()) as db, db:
            db.execute("INSERT OR IGNORE INTO sessions VALUES (?,?)", (owner, scoped))
        return FileSessionManager(session_id=scoped, storage_dir=str(self.root / "sessions"))

    def delete_user(self, user_id: str) -> None:
        owner = user_key(user_id)
        with closing(self.connect()) as db, db:
            sessions = list(db.execute("SELECT session FROM sessions WHERE owner=?", (owner,)))
            for (session,) in sessions:
                FileSessionManager(session, str(self.root / "sessions")).delete_session(session)
            db.execute("DELETE FROM preferences WHERE owner=?", (owner,))
            db.execute("DELETE FROM sessions WHERE owner=?", (owner,))
        # This removes application-visible data. OS snapshots/backups need their own policy.
