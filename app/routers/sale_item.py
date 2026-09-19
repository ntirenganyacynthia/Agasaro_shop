from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependences import require_role
from app.schemas.sale_item import SaleItemRead
from app.services.sale_item import get_all_sale_items, get_sale_item


router = APIRouter(prefix="/sale-items", tags=["Sale Items"])
staff = require_role("admin", "cashier")


@router.get("/", response_model=list[SaleItemRead])
def read_sale_items(db: Session = Depends(get_db), current_user=Depends(staff)):
    return get_all_sale_items(db)


@router.get("/{sale_item_id}", response_model=SaleItemRead)
def read_sale_item(sale_item_id: int, db: Session = Depends(get_db), current_user=Depends(staff)):
    return get_sale_item(db, sale_item_id)
