from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    category: str = Field(min_length=1, max_length=80)
    price: float = Field(gt=0)
    stock: int = Field(ge=0)


class ProductRead(ProductCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class ProductWithRating(ProductRead):
    average_rating: float | None
    review_count: int


class ReviewCreate(BaseModel):
    user_name: str
    rating: int = Field(ge=1, le=5)
    comment: str | None = None


class ReviewRead(ReviewCreate):
    id: str
    product_id: int
    created_at: datetime
