from sqlalchemy.orm import Session
from app.models.payment import Payment
class PaymentRepository:

    def get_all(self, db: Session):
        return db.query(Payment).all()

    def get_by_id(
        self,
        db: Session,
        payment_id: int
    ):
        return (
            db.query(Payment)
            .filter(
                Payment.payment_id == payment_id
            )
            .first()
        )

    def create(
        self,
        db: Session,
        data: dict,
        commit: bool = True
    ):
        payment = Payment(**data)

        db.add(payment)

        if commit:
            db.commit()
            db.refresh(payment)
        else:
            db.flush()

        return payment

    def update(
        self,
        db: Session,
        payment: Payment,
        data: dict,
        commit: bool = True
    ):
        for field, value in data.items():
            setattr(payment, field, value)

        if commit:
            db.commit()
            db.refresh(payment)
        else:
            db.flush()

        return payment

    def delete(
        self,
        db: Session,
        payment: Payment,
        commit: bool = True
    ):
        db.delete(payment)

        if commit:
            db.commit()


payment_repository = PaymentRepository()