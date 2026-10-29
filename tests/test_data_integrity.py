"""Check relational, policy, image and reproducibility contracts in synthetic data."""

import hashlib
import sqlite3
from collections import Counter

import pytest
from PIL import Image
from pypdf import PdfReader

from common.data import (
    bookings_connection,
    copy_bookings,
    data_path,
    load_csv,
    load_json,
    load_jsonl,
)
from scripts.build_data import build


def test_counts_and_manifest_hashes():
    assert len(load_json("destinations.json")) == 30
    for filename, count in [("flights.csv", 500), ("hotels.csv", 150), ("reviews.csv", 300)]:
        assert len(load_csv(filename)) == count
    assert len(load_jsonl("support_tickets.jsonl")) == 100
    assert len({r["date"] for r in load_csv("ops/cost_report.csv")}) == 90
    for name, expected in load_json("manifest.json")["sha256"].items():
        assert hashlib.sha256(data_path(name).read_bytes()).hexdigest() == expected, name


def test_booking_financial_and_inventory_invariants():
    with bookings_connection() as db:
        assert db.execute("PRAGMA foreign_key_check").fetchall() == []
        assert db.execute("SELECT count(*) FROM bookings").fetchone()[0] == 300
        rows = db.execute("""SELECT b.booking_id,b.total_cents,SUM(i.quantity*i.unit_price_cents)
            FROM bookings b JOIN booking_items i USING(booking_id)
            GROUP BY b.booking_id""").fetchall()
        assert all(row[1] == row[2] for row in rows)
        rows = db.execute("""SELECT p.amount_cents,SUM(r.amount_cents) FROM payments p
            JOIN refunds r USING(payment_id) GROUP BY p.payment_id""").fetchall()
        assert all(row[1] <= row[0] for row in rows)
        booked = dict(
            db.execute("""SELECT inventory_id,SUM(quantity) FROM booking_items
            JOIN bookings USING(booking_id) WHERE item_type='flight' AND status='confirmed'
            GROUP BY inventory_id""").fetchall()
        )
    for flight in load_csv("flights.csv"):
        assert int(flight["seats_left"]) == int(flight["capacity"]) - booked.get(
            flight["flight_id"], 0
        )


def test_committed_database_is_read_only_and_copy_is_isolated(tmp_path):
    with bookings_connection() as db, pytest.raises(sqlite3.OperationalError, match="readonly"):
        db.execute("DELETE FROM bookings")
    destination = copy_bookings(tmp_path / "working.db")
    with sqlite3.connect(destination) as db:
        db.execute("UPDATE customers SET name='Edited' WHERE customer_id='CUS-001'")
    with bookings_connection() as db:
        assert (
            db.execute("SELECT name FROM customers WHERE customer_id='CUS-001'").fetchone()[0]
            != "Edited"
        )
    with pytest.raises(FileExistsError):
        copy_bookings(destination)
    with pytest.raises(ValueError):
        data_path("../.env")


def test_pdf_page_citations_and_receipt_labels():
    pdf = PdfReader(data_path("policies/nimbus_terms.pdf"))
    assert len(pdf.pages) == 10
    for index, page in enumerate(pdf.pages, 1):
        assert f"Page {index} of 10" in page.extract_text()
    for case in load_jsonl("eval/policy_qa.jsonl"):
        if "source" in case:
            code = (
                data_path(case["source"])
                .read_text(encoding="utf-8")
                .split("\n\n")[1]
                .split(" |")[0]
            )
            assert code in pdf.pages[case["pdf_page"] - 1].extract_text()
    receipts = load_jsonl("eval/receipts.jsonl")
    assert sum(bool(r["anomaly"]) for r in receipts) == 2
    for receipt in receipts:
        with Image.open(data_path(receipt["file"])) as image:
            assert image.size == (800, 1000)
        mismatch = receipt["total_cents"] != receipt["subtotal_cents"] + receipt["tax_cents"]
        assert mismatch == bool(receipt["anomaly"])


def test_incidents_and_evaluation_split():
    logs = load_jsonl("ops/app_logs.jsonl")
    assert Counter(row["message"] for row in logs)["dependency_timeout"] == 20
    assert sum(row["deployment_id"] == "release-bad" for row in logs) == 20
    tickets = load_jsonl("support_tickets.jsonl")
    practice = {t["ticket_id"] for t in tickets if t["split"] == "practice"}
    evaluation = {c["id"] for c in load_jsonl("eval/ticket_triage.jsonl")}
    assert len(evaluation) == 20 and not practice & evaluation


def test_generator_reproduces_committed_fixtures(tmp_path):
    rebuilt = build(tmp_path / "data")
    committed = load_json("manifest.json")
    assert rebuilt["counts"] == committed["counts"]
    assert rebuilt["sha256"].keys() == committed["sha256"].keys()
    for name, digest in rebuilt["sha256"].items():
        generated = tmp_path / "data" / name
        original = data_path(name)
        # SQLite headers and compression libraries can vary between operating systems.
        if name.endswith(".db"):
            with sqlite3.connect(generated) as new_db, bookings_connection() as source_db:
                assert list(new_db.iterdump()) == list(source_db.iterdump())
        elif name.endswith(".png"):
            with Image.open(generated) as new_image, Image.open(original) as source_image:
                assert new_image.size == source_image.size
                assert new_image.convert("RGB").tobytes() == source_image.convert("RGB").tobytes()
        elif name.endswith(".pdf"):
            assert [p.extract_text() for p in PdfReader(generated).pages] == [
                p.extract_text() for p in PdfReader(original).pages
            ]
        else:
            assert digest == committed["sha256"][name], name
    with pytest.raises(ValueError, match="not empty"):
        build(tmp_path / "data")
