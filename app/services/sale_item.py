from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.sale_item import SaleItem


def get_all_sale_items(db: Session):
    return db.query(SaleItem).order_by(SaleItem.sale_item_id.desc()).limit(1000).all()


def get_sale_item(db: Session, sale_item_id: int):
    item = db.query(SaleItem).filter(SaleItem.sale_item_id == sale_item_id).first()
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale item not found.")
    return item
