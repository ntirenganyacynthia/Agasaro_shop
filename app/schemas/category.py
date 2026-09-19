from pydantic import BaseModel


class CategoryBase(BaseModel):
    category_name: str
    category_description: str | None = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    category_name: str | None = None
    category_description: str | None = None


class CategoryRead(CategoryBase):
    category_id: int

    class Config:
        from_attributes = True