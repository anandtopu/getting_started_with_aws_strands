"""Repository-relative, read-only access to committed synthetic teaching data."""

import csv
import json
import shutil
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from common.config import ROOT, CourseError


def data_path(relative: str) -> Path:
    base = (ROOT / "data").resolve()
    path = (base / relative).resolve()
    if not path.is_relative_to(base):
        raise ValueError("Data paths must stay inside the data directory.")
    if not path.is_file():
        raise CourseError(f"Missing synthetic data: {relative}. Run scripts/build_data.py.")
    return path


def load_json(relative: str) -> Any:
    return json.loads(data_path(relative).read_text(encoding="utf-8"))


def load_jsonl(relative: str) -> list[dict[str, Any]]:
    return [
        json.loads(line) for line in data_path(relative).read_text(encoding="utf-8").splitlines()
    ]


def load_csv(relative: str) -> list[dict[str, str]]:
    with data_path(relative).open(encoding="utf-8", newline="") as source:
        return list(csv.DictReader(source))


@contextmanager
def bookings_connection() -> Iterator[sqlite3.Connection]:
    """The URI's read-only flag protects committed booking fixtures."""
    connection = sqlite3.connect(data_path("bookings.db").as_uri() + "?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys=ON")
    try:
        yield connection
    finally:
        connection.close()


def copy_bookings(destination: Path) -> Path:
    """Create a disposable working copy without silently overwriting user work."""
    destination = destination.resolve()
    if destination.is_relative_to((ROOT / "data").resolve()):
        raise ValueError("Working databases must be outside committed data/.")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("xb") as output, data_path("bookings.db").open("rb") as source:
        shutil.copyfileobj(source, output)
    return destination
