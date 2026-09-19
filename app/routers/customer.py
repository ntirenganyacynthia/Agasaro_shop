from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependences import require_role
from app.schemas.customer import CustomerCreate, CustomerRead, CustomerUpdate
from app.services.customer import create_customer, delete_customer, get_all_customers, get_customer, update_customer


router = APIRouter(prefix="/customers", tags=["Customers"])
staff = require_role("admin", "cashier")


@router.get("/", response_model=list[CustomerRead])
def read_customers(db: Session = Depends(get_db), current_user=Depends(staff)):
    return get_all_customers(db)


@router.get("/{customer_id}", response_model=CustomerRead)
def read_customer(customer_id: int, db: Session = Depends(get_db), current_user=Depends(staff)):
    return get_customer(db, customer_id)


@router.post("/", response_model=CustomerRead, status_code=status.HTTP_201_CREATED)
def add_customer(customer: CustomerCreate, db: Session = Depends(get_db), current_user=Depends(staff)):
    return create_customer(db, customer)


@router.put("/{customer_id}", response_model=CustomerRead)
def edit_customer(customer_id: int, customer: CustomerUpdate, db: Session = Depends(get_db), current_user=Depends(staff)):
    return update_customer(db, customer_id, customer)


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_customer(customer_id: int, db: Session = Depends(get_db), current_user=Depends(require_role("admin"))):
    delete_customer(db, customer_id)
