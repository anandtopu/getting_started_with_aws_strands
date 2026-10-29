"""Validated Nimbus outputs introduced in module 04."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Category(StrEnum):
    REFUND = "refund"
    CHANGE = "change"
    BAGGAGE = "baggage"
    BOOKING = "booking"
    PRIVACY = "privacy"


class TicketTriage(BaseModel):
    model_config = ConfigDict(extra="forbid")
    category: Category
    urgency: str = Field(pattern="^(normal|high)$")
    summary: str = Field(min_length=5, max_length=200)
    booking_id: str | None = Field(default=None, pattern=r"^BKG-\d{4}$")


class TripLeg(BaseModel):
    flight_id: str = Field(pattern=r"^FLT-\d{4}$")
    destination: str = Field(min_length=2)
    price_cents: int = Field(gt=0)


class Itinerary(BaseModel):
    model_config = ConfigDict(extra="forbid")
    traveler: str = Field(min_length=2)
    legs: list[TripLeg] = Field(min_length=1, max_length=4)
    total_cents: int = Field(gt=0)
    hotel_id: str | None = Field(default=None, pattern=r"^HTL-\d{3}$")

    @model_validator(mode="after")
    def check_total(self) -> "Itinerary":
        # This schema totals flights only; hotel cost needs its own explicit field.
        if self.total_cents != sum(leg.price_cents for leg in self.legs):
            raise ValueError("Itinerary total must equal the sum of flight prices")
        return self


def validate_inventory(itinerary: Itinerary) -> None:
    """Reject model-invented flight prices, destinations and hotel references."""
    from decimal import Decimal

    from common.data import load_csv

    flights = {row["flight_id"]: row for row in load_csv("flights.csv")}
    for leg in itinerary.legs:
        row = flights.get(leg.flight_id)
        if row is None or leg.destination != row["destination"]:
            raise ValueError("Itinerary flight does not match Nimbus inventory")
        if leg.price_cents != int(Decimal(row["price_usd"]) * 100) or int(row["seats_left"]) < 1:
            raise ValueError("Itinerary price or availability does not match Nimbus inventory")
    if itinerary.hotel_id and itinerary.hotel_id not in {
        row["hotel_id"] for row in load_csv("hotels.csv")
    }:
        raise ValueError("Itinerary hotel does not match Nimbus inventory")
