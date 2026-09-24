from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class ListingCondition(str, Enum):
    New = "New"
    LikeNew = "LikeNew"
    Good = "Good"
    Fair = "Fair"
    Poor = "Poor"


class ListingAvailability(str, Enum):
    Available = "Available"
    Rented = "Rented"
    Sold = "Sold"


class ListingBase(SQLModel):
    gameId: int = Field(foreign_key="game.gameId", index=True)
    ownerId: int = Field(foreign_key="user.id", index=True)
    condition: str = Field(index=True)
    availability: str = Field(
        default=ListingAvailability.Available.value, index=True
    )
    price: float


class Listing(ListingBase, table=True):
    listingId: Optional[int] = Field(default=None, primary_key=True)

    def toJSON(self) -> dict:
        return {
            "listingId": self.listingId,
            "gameId": self.gameId,
            "ownerId": self.ownerId,
            "condition": self.condition,
            "availability": self.availability,
            "price": self.price,
        }
