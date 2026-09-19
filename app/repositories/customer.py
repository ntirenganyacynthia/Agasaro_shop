from sqlalchemy.orm import Session

from app.models.customer import Customer


class CustomerRepository:

    def get_all(self, db: Session):
        return db.query(Customer).all()

    def get_by_id(self, db: Session, customer_id: int):
        return db.query(Customer).filter(
            Customer.customer_id == customer_id
        ).first()

    def create(self, db: Session, data: dict):
        customer = Customer(**data)

        db.add(customer)
        db.commit()
        db.refresh(customer)

        return customer

    def update(self, db: Session, customer, data: dict):

        for field, value in data.items():
            setattr(customer, field, value)

        db.commit()
        db.refresh(customer)

        return customer

    def delete(self, db: Session, customer):

        db.delete(customer)
        db.commit()


customer_repository = CustomerRepository()