from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    customer_email = Column(String(254), nullable=True)
    customer_phonenumber = Column(String(20), nullable=True, index=True)

    sales = relationship("Sale", back_populates="customer")
