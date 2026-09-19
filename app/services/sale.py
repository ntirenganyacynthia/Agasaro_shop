from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.sale import Sale


def get_all_sales(db: Session):
    return db.query(Sale).order_by(Sale.sale_id.desc()).limit(500).all()


def get_sale(db: Session, sale_id: int):
    sale = db.query(Sale).filter(Sale.sale_id == sale_id).first()
    if sale is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale not found.")
    return sale
