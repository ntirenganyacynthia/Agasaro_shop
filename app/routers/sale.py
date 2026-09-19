from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependences import require_role
from app.schemas.sale import SaleRead
from app.services.sale import get_all_sales, get_sale


router = APIRouter(prefix="/sales", tags=["Sales"])
staff = require_role("admin", "cashier")


@router.get("/", response_model=list[SaleRead])
def read_sales(db: Session = Depends(get_db), current_user=Depends(staff)):
    return get_all_sales(db)


@router.get("/{sale_id}", response_model=SaleRead)
def read_sale(sale_id: int, db: Session = Depends(get_db), current_user=Depends(staff)):
    return get_sale(db, sale_id)
