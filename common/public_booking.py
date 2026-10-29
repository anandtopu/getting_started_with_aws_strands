"""Dependency-free public booking API, also packaged unchanged in the Gateway Lambda."""

import csv
import re
from pathlib import Path


def refund_quote(amount_cents: int):
    if type(amount_cents) is not int or not 0 < amount_cents <= 50_000:
        raise ValueError("Refund amount requires supervisor review (limit USD 500.00)")
    return {"amount_cents": amount_cents, "within_limit": True, "quote_only": True}


def search_flights(destination: str):
    if not re.fullmatch(r"[A-Za-z -]{2,60}", destination):
        raise ValueError("Supply a destination city or airport code")
    path = Path(__file__).resolve().parents[1] / "data/flights.csv"
    with path.open(encoding="utf-8", newline="") as source:
        return [
            row
            for row in csv.DictReader(source)
            if destination.casefold() in row["destination"].casefold()
        ][:3]


def lambda_handler(event, context):
    name = context.client_context.custom["bedrockAgentCoreToolName"].split("___")[-1]
    if name == "refund_quote" and set(event) == {"amount_cents"}:
        return refund_quote(event["amount_cents"])
    if name == "search_flights" and set(event) == {"destination"}:
        return search_flights(event["destination"])
    raise ValueError("Unreviewed tool or arguments")
