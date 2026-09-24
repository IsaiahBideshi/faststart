from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class RentalBase(SQLModel):
    listingId: int = Field(foreign_key="listing.listingId", index=True)
    renterId: int = Field(foreign_key="user.id", index=True)


class Rental(RentalBase, table=True):
    rentalId: Optional[int] = Field(default=None, primary_key=True)
    rentalDate: datetime = Field(default_factory=_utcnow)
    returnDate: Optional[datetime] = Field(default=None)

    def toJSON(self) -> dict:
        return {
            "rentalId": self.rentalId,
            "listingId": self.listingId,
            "renterId": self.renterId,
            "rentalDate": self.rentalDate.isoformat() if self.rentalDate else None,
            "returnDate": self.returnDate.isoformat() if self.returnDate else None,
        }
