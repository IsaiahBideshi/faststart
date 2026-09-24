from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class PaymentBase(SQLModel):
    # Spec calls this Amount / payment_date / customerId.
    # Python field is `amount`; toJSON() exposes both `amount` and `Amount`.
    customerId: Optional[int] = Field(default=None, foreign_key="user.id", index=True)
    amount: float
    payment_date: datetime = Field(default_factory=_utcnow)
    # RentalPayment extends Payment with rentalId (FK). Single-table: nullable.
    rentalId: Optional[int] = Field(default=None, foreign_key="rental.rentalId", index=True)


class Payment(PaymentBase, table=True):
    paymentId: Optional[int] = Field(default=None, primary_key=True)

    def toJSON(self) -> dict:
        return {
            "paymentId": self.paymentId,
            "customerId": self.customerId,
            "payment_date": self.payment_date.isoformat() if self.payment_date else None,
            "amount": self.amount,
            "Amount": self.amount,
            "rentalId": self.rentalId,
        }


class RentalPayment(Payment):
    """Spec subclass: a Payment linked to a rental via rentalId (FK)."""
