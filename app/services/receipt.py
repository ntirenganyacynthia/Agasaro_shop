from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.receipt import Receipt


def get_all_receipts(db: Session):
    return db.query(Receipt).order_by(Receipt.receipt_id.desc()).limit(500).all()


def get_receipt(db: Session, receipt_id: int):
    receipt = db.query(Receipt).filter(Receipt.receipt_id == receipt_id).first()
    if receipt is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receipt not found.")
    return receipt
