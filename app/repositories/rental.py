import logging
from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Session, select

from app.models.rental import Rental

logger = logging.getLogger(__name__)


class RentalRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, *, listing_id: int, renter_id: int) -> Rental:
        rental = Rental(listingId=listing_id, renterId=renter_id)
        try:
            self.db.add(rental)
            self.db.commit()
            self.db.refresh(rental)
            return rental
        except Exception as e:
            logger.error(f"Error creating rental: {e}")
            self.db.rollback()
            raise

    def get_by_id(self, rental_id: int) -> Optional[Rental]:
        return self.db.get(Rental, rental_id)

    def list(self) -> list[Rental]:
        return list(self.db.exec(select(Rental)).all())

    def save(self, rental: Rental) -> Rental:
        try:
            self.db.add(rental)
            self.db.commit()
            self.db.refresh(rental)
            return rental
        except Exception as e:
            logger.error(f"Error saving rental: {e}")
            self.db.rollback()
            raise

    def mark_returned(self, rental: Rental) -> Rental:
        rental.returnDate = datetime.now(timezone.utc)
        return self.save(rental)
