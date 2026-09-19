from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Payment(Base):
    __tablename__ = "payments"
    __table_args__ = (
        UniqueConstraint("idempotency_key", name="uq_payments_idempotency_key"),
        UniqueConstraint("provider_reference", name="uq_payments_provider_reference"),
    )

    payment_id = Column(Integer, primary_key=True, index=True)

    sale_id = Column(Integer, ForeignKey("sales.sale_id"), nullable=False, index=True)

    payment_method = Column(String(50), nullable=False)

    amount_paid = Column(Numeric(12, 2), nullable=False)

    payment_status = Column(String(30), nullable=False, default="pending", index=True)

    payer_phone = Column(String(20), nullable=True)

    provider_reference = Column(String(100), nullable=True)

    provider_transaction_id = Column(String(100), nullable=True)

    provider_status = Column(String(50), nullable=True)

    idempotency_key = Column(String(100), nullable=True)

    status_message = Column(Text, nullable=True)

    payment_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    sale = relationship("Sale", back_populates="payments")
