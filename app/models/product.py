from sqlalchemy import Column, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from app.database import Base


class Product(Base):
    __tablename__ = "products"

    product_id = Column(Integer, primary_key=True, index=True)

    category_id = Column(Integer, ForeignKey("categories.category_id"), nullable=False)

    supplier_id = Column(Integer, ForeignKey("suppliers.supplier_id"), nullable=False)
    product_name = Column(String(100), nullable=False)

    unit_price = Column(Numeric(12, 2), nullable=False)
    cost_price = Column(Numeric(12, 2), nullable=False)

    stock_quantity = Column(Numeric(12, 2), nullable=False, default=0)
    reserved_quantity = Column(Numeric(12, 2), nullable=False, default=0)

    category = relationship("Category", back_populates="products")
    
    supplier = relationship("Supplier", back_populates="products")
    sale_items = relationship("SaleItem", back_populates="product")

    @property
    def available_quantity(self):
        return self.stock_quantity - self.reserved_quantity
