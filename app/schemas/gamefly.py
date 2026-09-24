from datetime import datetime
from typing import Optional

from pydantic import field_validator
from sqlmodel import SQLModel

from app.models.game import Platform
from app.models.listing import ListingAvailability, ListingCondition


# ---------- Games ----------

class GameCreate(SQLModel):
    title: str
    platform: Platform
    genre: Optional[str] = None
    rating: Optional[str] = None
    boxart: Optional[str] = None


class GameResponse(SQLModel):
    gameId: int
    title: str
    rating: Optional[str] = None
    platform: str
    boxart: Optional[str] = None
    genre: Optional[str] = None


# ---------- Listings ----------

class ListingCreate(SQLModel):
    game_id: int
    condition: ListingCondition
    price: float

    @field_validator("price")
    @classmethod
    def price_must_be_positive(cls, v: float) -> float:
        if v is None or float(v) <= 0:
            raise ValueError("price must be > 0")
        return v


class ListingResponse(SQLModel):
    listingId: int
    gameId: int
    ownerId: int
    condition: str
    availability: str
    price: float


class ListingWithGameResponse(ListingResponse):
    game: Optional[GameResponse] = None


class SellListingRequest(SQLModel):
    # Intentionally empty-ish: selling needs no extra data.
    # Accept an optional confirm flag for clients that want to send a body.
    confirm: Optional[bool] = None


# ---------- Payments ----------

class PaymentCreate(SQLModel):
    amount: float
    customer_id: Optional[int] = None
    rental_id: Optional[int] = None

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: float) -> float:
        if v is None or float(v) <= 0:
            raise ValueError("amount must be > 0")
        return v


class PaymentResponse(SQLModel):
    paymentId: int
    customerId: Optional[int] = None
    payment_date: Optional[datetime] = None
    amount: float
    rentalId: Optional[int] = None


# ---------- Rentals ----------

class RentalCreate(SQLModel):
    listing_id: int
    customer_id: int


class RentalReturnUpdate(SQLModel):
    # Spec: "payment or payment_id" — accept either a linked id or inline amount.
    payment_id: Optional[int] = None
    amount: Optional[float] = None
    customer_id: Optional[int] = None


class RentalResponse(SQLModel):
    rentalId: int
    listingId: int
    renterId: int
    rentalDate: Optional[datetime] = None
    returnDate: Optional[datetime] = None
