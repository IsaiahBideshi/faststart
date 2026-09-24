from typing import Optional

from app.models.listing import ListingAvailability
from app.repositories.listing import ListingRepository
from app.repositories.payment import PaymentRepository
from app.repositories.rental import RentalRepository
from app.repositories.user import UserRepository


class RentalService:
    """Staff rental workflows: confirm_rental + confirm_return (return)."""

    def __init__(
        self,
        rental_repo: RentalRepository,
        listing_repo: ListingRepository,
        payment_repo: PaymentRepository,
        user_repo: Optional[UserRepository] = None,
    ):
        self.rental_repo = rental_repo
        self.listing_repo = listing_repo
        self.payment_repo = payment_repo
        self.user_repo = user_repo

    # -- create / confirm rental -------------------------------------
    def confirm_rental(self, *, listing_id: int, renter_id: int):
        listing = self.listing_repo.get_by_id(listing_id)
        if listing is None:
            raise LookupError(f"Listing {listing_id} not found")
        if listing.availability != ListingAvailability.Available.value:
            raise ValueError("Listing is not available for rental")
        if self.user_repo is not None and self.user_repo.get_by_id(renter_id) is None:
            raise LookupError(f"Customer {renter_id} not found")
        rental = self.rental_repo.create(listing_id=listing_id, renter_id=renter_id)
        listing.availability = ListingAvailability.Rented.value
        self.listing_repo.save(listing)
        return rental

    # -- return --------------------------------------------------------
    def confirm_return(
        self,
        *,
        rental_id: int,
        payment_id: Optional[int] = None,
        amount: Optional[float] = None,
        customer_id: Optional[int] = None,
    ):
        rental = self.rental_repo.get_by_id(rental_id)
        if rental is None:
            raise LookupError(f"Rental {rental_id} not found")

        payment = None
        if payment_id is not None:
            payment = self.payment_repo.get_by_id(payment_id)
            if payment is None:
                raise LookupError(f"Payment {payment_id} not found")
            # Link standalone payment to this rental if not already linked.
            if payment.rentalId is None:
                payment.rentalId = rental.rentalId
                # customer defaults to the renter when not supplied.
                if payment.customerId is None:
                    payment.customerId = customer_id if customer_id is not None else rental.renterId
                self.payment_repo.save(payment)
            payment = self.payment_repo.get_by_id(payment.paymentId)
        elif amount is not None:
            if float(amount) <= 0:
                raise ValueError("amount must be > 0")
            from app.schemas.gamefly import PaymentCreate

            payment = self.payment_repo.create(
                PaymentCreate(
                    amount=float(amount),
                    customer_id=customer_id if customer_id is not None else rental.renterId,
                    rental_id=rental.rentalId,
                )
            )
        else:
            raise ValueError("Return requires payment_id or amount")

        self.rental_repo.mark_returned(rental)
        listing = self.listing_repo.get_by_id(rental.listingId)
        if listing is not None and listing.availability == ListingAvailability.Rented.value:
            listing.availability = ListingAvailability.Available.value
            self.listing_repo.save(listing)
        return self.rental_repo.get_by_id(rental.rentalId)
