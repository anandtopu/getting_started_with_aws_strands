"""Typed requests and authoritative prices for the synthetic trip lessons."""

from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from common.data import data_path, load_csv


class TripRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    city: Literal["Porto", "Chicago", "Lima"] = "Porto"
    travelers: int = Field(default=2, ge=1, le=6, strict=True)
    nights: int = Field(default=2, ge=1, le=7, strict=True)
    budget_cents: int = Field(default=100000, ge=1, le=10000000, strict=True)


class SpecialistAnswer(BaseModel):
    model_config = ConfigDict(extra="forbid")
    role: Literal["flight", "hotel", "policy"]
    reference: str
    cents: int = Field(ge=0, strict=True)
    summary: str = Field(min_length=1, max_length=800)


def catalog(role, request):
    if role == "policy":
        return {
            "role": role,
            "reference": "policies/refund.md",
            "cents": 0,
            "summary": "\n\n".join(
                data_path("policies/refund.md").read_text(encoding="utf-8").split("\n\n")[:5]
            ),
        }
    if role == "flight":
        rows = [
            r
            for r in load_csv("flights.csv")
            if r["destination"] == request.city
            and r["date"] == "2027-04-01"
            and int(r["seats_left"]) >= request.travelers
        ]
        row = min(rows, key=lambda r: Decimal(r["price_usd"]))
        cents = int(Decimal(row["price_usd"]) * 100) * request.travelers
        return dict(
            role=role,
            reference=row["flight_id"],
            cents=cents,
            summary=f"One-way synthetic flight to {request.city} on 2027-04-01.",
        )
    if role != "hotel":
        raise ValueError("Unknown specialist role")
    rows = [r for r in load_csv("hotels.csv") if r["city"] == request.city]
    row = min(rows, key=lambda r: Decimal(r["nightly_price_usd"]))
    cents = int(Decimal(row["nightly_price_usd"]) * 100) * request.nights
    return dict(
        role=role,
        reference=row["hotel_id"],
        cents=cents,
        summary=f"One synthetic room, {request.nights} nights; occupancy not verified.",
    )


def validate_offer(value, expected):
    offer = SpecialistAnswer.model_validate(value)
    if any(getattr(offer, key) != expected[key] for key in ("role", "reference", "cents")):
        raise ValueError("Specialist changed authoritative reference or price")
    return offer
