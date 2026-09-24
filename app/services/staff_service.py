"""Staff facade matching the assignment class diagram.

    Staff.list_game(owner, game, condition, price)
    Staff.confirm_rental(renter, listing)
    Staff.confirm_return(renter, rental)

Each method accepts either model objects or integer ids so unit tests can
pass lightweight fakes while integration tests use real rows.
"""

from typing import Optional


def _id(obj) -> Optional[int]:
    if obj is None:
        return None
    for attr in ("id", "listingId", "gameId", "rentalId"):
        if hasattr(obj, attr):
            v = getattr(obj, attr)
            if isinstance(v, int):
                return v
    if isinstance(obj, int):
        return obj
    return None


class StaffService:
    def __init__(self, listing_service, rental_service, game_service=None):
        self.listing_service = listing_service
        self.rental_service = rental_service
        self.game_service = game_service

    # -- create_listing: needs a real DB (FK linkage) -> integration test --
    def create_listing(self, owner_id: int, game_id: int, condition: str, price: float):
        owner = _id(owner_id) if not isinstance(owner_id, int) else owner_id
        game = _id(game_id) if not isinstance(game_id, int) else game_id
        cond = condition.value if hasattr(condition, "value") else condition
        return self.listing_service.create_listing(
            owner_id=owner, game_id=game, condition=cond, price=price
        )

    def list_game(self, owner, game, condition: str, price: float):
        """Spec name: Staff.list_game(owner, game, condition, price)."""
        return self.create_listing(
            _id(owner),  # type: ignore[arg-type]
            _id(game),  # type: ignore[arg-type]
            condition,
            price,
        )

    def confirm_rental(self, renter, listing):
        renter_id = renter if isinstance(renter, int) else _id(renter)
        listing_id = listing if isinstance(listing, int) else _id(listing)
        return self.rental_service.confirm_rental(
            listing_id=listing_id, renter_id=renter_id  # type: ignore[arg-type]
        )

    def confirm_return(self, renter, rental, payment=None, payment_id=None, amount=None):
        rental_id = rental if isinstance(rental, int) else _id(rental)
        renter_id = renter if isinstance(renter, int) else _id(renter)
        pid = payment_id
        amt = amount
        cid = renter_id
        if payment is not None:
            if isinstance(payment, int):
                pid = payment
            elif hasattr(payment, "paymentId"):
                pid = payment.paymentId
            elif isinstance(payment, dict):
                pid = payment.get("payment_id") or payment.get("paymentId")
                amt = amt if amt is not None else payment.get("amount")
                cid = payment.get("customer_id", cid)
        return self.rental_service.confirm_return(
            rental_id=rental_id,  # type: ignore[arg-type]
            payment_id=pid,
            amount=amt,
            customer_id=cid,
        )
