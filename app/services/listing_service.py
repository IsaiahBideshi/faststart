from typing import Optional

from app.models.listing import ListingAvailability, ListingCondition
from app.repositories.game import GameRepository
from app.repositories.listing import ListingRepository


class ListingService:
    """Customer listing workflows + owner sell."""

    def __init__(self, listing_repo: ListingRepository, game_repo: GameRepository):
        self.listing_repo = listing_repo
        self.game_repo = game_repo

    def create_listing(
        self, *, owner_id: int, game_id: int, condition: str, price: float
    ):
        valid_conditions = {c.value for c in ListingCondition}
        cond = condition.value if hasattr(condition, "value") else str(condition)
        if cond not in valid_conditions:
            raise ValueError(
                f"Invalid condition '{condition}'. Expected one of {sorted(valid_conditions)}"
            )
        if float(price) <= 0:
            raise ValueError("price must be > 0")
        game = self.game_repo.get_by_id(game_id)
        if game is None:
            raise LookupError(f"Game {game_id} not found")
        return self.listing_repo.create(
            game_id=game_id, owner_id=owner_id, condition=cond, price=float(price)
        )

    def list_with_games(self, platform: Optional[str] = None):
        """Return (listing, game) pairs, optionally filtered by platform."""
        listings = self.listing_repo.list()
        result = []
        for listing in listings:
            game = self.game_repo.get_by_id(listing.gameId)
            if platform is not None:
                if game is None or game.platform != platform:
                    continue
            result.append((listing, game))
        return result

    def sell_listing(self, *, listing_id: int, owner_id: int):
        listing = self.listing_repo.get_by_id(listing_id)
        if listing is None:
            raise LookupError(f"Listing {listing_id} not found")
        if listing.ownerId != owner_id:
            raise PermissionError("Only the owner can sell this listing")
        if listing.availability != ListingAvailability.Available.value:
            raise ValueError("Only an active (Available) listing can be sold")
        listing.availability = ListingAvailability.Sold.value
        return self.listing_repo.save(listing)
