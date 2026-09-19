from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Sale(Base):
    __tablename__ = "sales"

    sale_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    sale_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    total_amount = Column(Numeric(12, 2), nullable=False)
    sale_status = Column(String(30), nullable=False, default="pending", index=True)
    public_status_token = Column(String(64), unique=True, nullable=False, index=True)

    customer = relationship("Customer", back_populates="sales")
    user = relationship("User", back_populates="sales")
    sale_items = relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="sale", cascade="all, delete-orphan")
    receipt = relationship("Receipt", back_populates="sale", uselist=False, cascade="all, delete-orphan")
