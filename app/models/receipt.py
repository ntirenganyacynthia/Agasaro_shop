from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Receipt(Base):
    __tablename__ = "receipts"

    receipt_id = Column(Integer, primary_key=True, index=True)

    sale_id = Column(
        Integer,
        ForeignKey("sales.sale_id"),
        nullable=False,
        unique=True
    )

    receipt_number = Column(
        String(100),
        unique=True,
        nullable=False
    )

    issued_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    sale = relationship(
        "Sale",
        back_populates="receipt"
    )