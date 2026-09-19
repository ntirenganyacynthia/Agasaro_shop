from sqlalchemy.orm import Session
from app.models.sale_item import SaleItem
class SaleItemRepository:

    def get_all(self, db: Session):
        return db.query(SaleItem).all()

    def get_by_id(
        self,
        db: Session,
        sale_item_id: int
    ):
        return (
            db.query(SaleItem)
            .filter(
                SaleItem.sale_item_id == sale_item_id
            )
            .first()
        )

    def create(
        self,
        db: Session,
        data: dict,
        commit: bool = True
    ):
        sale_item = SaleItem(**data)

        db.add(sale_item)

        if commit:
            db.commit()
            db.refresh(sale_item)
        else:
            db.flush()

        return sale_item

    def update(
        self,
        db: Session,
        sale_item: SaleItem,
        data: dict,
        commit: bool = True
    ):
        for field, value in data.items():
            setattr(sale_item, field, value)

        if commit:
            db.commit()
            db.refresh(sale_item)
        else:
            db.flush()

        return sale_item

    def delete(
        self,
        db: Session,
        sale_item: SaleItem,
        commit: bool = True
    ):
        db.delete(sale_item)

        if commit:
            db.commit()


sale_item_repository = SaleItemRepository()