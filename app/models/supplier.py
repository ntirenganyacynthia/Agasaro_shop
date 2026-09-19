from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Supplier(Base):
    __tablename__ = "suppliers"

    supplier_id = Column(Integer, primary_key=True, index=True)
    supplier_name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=True)
    phone_number = Column(String(20), nullable=True)
    address = Column(String(255), nullable=True)

    products = relationship(
        "Product",
        back_populates="supplier"
    )