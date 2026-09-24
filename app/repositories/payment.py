import logging
from typing import Optional

from sqlmodel import Session, select

from app.models.payment import Payment
from app.schemas.gamefly import PaymentCreate

logger = logging.getLogger(__name__)


class PaymentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: PaymentCreate) -> Payment:
        payment = Payment(
            customerId=data.customer_id,
            amount=data.amount,
            rentalId=data.rental_id,
        )
        try:
            self.db.add(payment)
            self.db.commit()
            self.db.refresh(payment)
            return payment
        except Exception as e:
            logger.error(f"Error creating payment: {e}")
            self.db.rollback()
            raise

    def get_by_id(self, payment_id: int) -> Optional[Payment]:
        return self.db.get(Payment, payment_id)

    def list(self) -> list[Payment]:
        return list(self.db.exec(select(Payment)).all())

    def save(self, payment: Payment) -> Payment:
        try:
            self.db.add(payment)
            self.db.commit()
            self.db.refresh(payment)
            return payment
        except Exception as e:
            logger.error(f"Error saving payment: {e}")
            self.db.rollback()
            raise
