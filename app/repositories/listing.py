import logging
from typing import Optional

from sqlmodel import Session, select

from app.models.listing import Listing, ListingAvailability

logger = logging.getLogger(__name__)


class ListingRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, *, game_id: int, owner_id: int, condition: str, price: float) -> Listing:
        listing = Listing(
            gameId=game_id,
            ownerId=owner_id,
            condition=condition,
            availability=ListingAvailability.Available.value,
            price=price,
        )
        try:
            self.db.add(listing)
            self.db.commit()
            self.db.refresh(listing)
            return listing
        except Exception as e:
            logger.error(f"Error creating listing: {e}")
            self.db.rollback()
            raise

    def get_by_id(self, listing_id: int) -> Optional[Listing]:
        return self.db.get(Listing, listing_id)

    def list(self, platform: Optional[str] = None) -> list[Listing]:
        # Platform filtering is done in ListingService.list_with_games
        # (needs the Game row); keep this a plain listing query.
        _ = platform
        return list(self.db.exec(select(Listing)).all())

    def save(self, listing: Listing) -> Listing:
        try:
            self.db.add(listing)
            self.db.commit()
            self.db.refresh(listing)
            return listing
        except Exception as e:
            logger.error(f"Error saving listing: {e}")
            self.db.rollback()
            raise
