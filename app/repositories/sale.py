from sqlalchemy.orm import Session
from app.models.sale import Sale
class SaleRepository:

    def get_all(self, db: Session):
        return db.query(Sale).all()

    def get_by_id(
        self,
        db: Session,
        sale_id: int
    ):
        return (
            db.query(Sale)
            .filter(Sale.sale_id == sale_id)
            .first()
        )

    def create(
        self,
        db: Session,
        data: dict,
        commit: bool = True
    ):
        sale = Sale(**data)

        db.add(sale)

        if commit:
            db.commit()
            db.refresh(sale)
        else:
            db.flush()

        return sale

    def update(
        self,
        db: Session,
        sale: Sale,
        data: dict,
        commit: bool = True
    ):
        for field, value in data.items():
            setattr(sale, field, value)

        if commit:
            db.commit()
            db.refresh(sale)
        else:
            db.flush()

        return sale

    def delete(
        self,
        db: Session,
        sale: Sale,
        commit: bool = True
    ):
        db.delete(sale)

        if commit:
            db.commit()


sale_repository = SaleRepository()