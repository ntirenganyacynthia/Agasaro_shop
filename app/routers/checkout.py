from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependences import get_optional_current_user
from app.schemas.checkout import CheckoutCreate, CheckoutResponse, PaymentStatusResponse
from app.services.checkout import checkout, get_status_by_token


router = APIRouter(prefix="/checkout", tags=["Checkout"])


@router.post("/", response_model=CheckoutResponse, status_code=status.HTTP_201_CREATED)
def create_checkout(
    data: CheckoutCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_optional_current_user),
):
   
    return checkout(db, data, current_user)


@router.get("/status/{token}", response_model=PaymentStatusResponse)
def checkout_status(token: str, db: Session = Depends(get_db)):
    return get_status_by_token(db, token)
