from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependences import require_role
from app.schemas.receipt import ReceiptRead
from app.services.receipt import get_all_receipts, get_receipt


router = APIRouter(prefix="/receipts", tags=["Receipts"])
staff = require_role("admin", "cashier")


@router.get("/", response_model=list[ReceiptRead])
def read_receipts(db: Session = Depends(get_db), current_user=Depends(staff)):
    return get_all_receipts(db)


@router.get("/{receipt_id}", response_model=ReceiptRead)
def read_receipt(receipt_id: int, db: Session = Depends(get_db), current_user=Depends(staff)):
    return get_receipt(db, receipt_id)
