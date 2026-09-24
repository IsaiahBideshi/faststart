from typing import Optional

from app.repositories.payment import PaymentRepository
from app.schemas.gamefly import PaymentCreate


class PaymentService:
    def __init__(self, payment_repo: PaymentRepository):
        self.payment_repo = payment_repo

    def create_payment(
        self,
        amount: float,
        customer_id: Optional[int] = None,
        rental_id: Optional[int] = None,
    ):
        if amount is None or float(amount) <= 0:
            raise ValueError("amount must be > 0")
        return self.payment_repo.create(
            PaymentCreate(
                amount=float(amount),
                customer_id=customer_id,
                rental_id=rental_id,
            )
        )
