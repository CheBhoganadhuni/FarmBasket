from ninja import Schema
from typing import Optional

class ProductCreateUpdateSchema(Schema):
    name: str
    description: str
    category: str  # UUID string
    price: float
    discount_price: Optional[float] = None
    stock_quantity: int
    unit: str
    unit_value: Optional[float] = 1.0
    low_stock_threshold: Optional[int] = 10
    is_active: Optional[bool] = True
    is_featured: Optional[bool] = False
    is_organic_certified: Optional[bool] = True
    featured_image: Optional[str] = None  # URL or empty

class ProductCreateSchema(Schema):
    name: str
    description: str
    category: str  # Use UUID as string
    price: float
    discount_price: Optional[float]
    stock_quantity: int
    unit: str
    unit_value: Optional[float] = 1.0
    low_stock_threshold: Optional[int] = 10
    is_active: Optional[bool] = True
    is_featured: Optional[bool] = False
    is_organic_certified: Optional[bool] = True
    featured_image: Optional[str] = None  # URL or path

class ProductUpdateSchema(Schema):
    name: Optional[str]
    description: Optional[str]
    category: Optional[str]
    price: Optional[float]
    discount_price: Optional[float]
    stock_quantity: Optional[int]
    unit: Optional[str]
    unit_value: Optional[float]
    low_stock_threshold: Optional[int]
    is_active: Optional[bool]
    is_featured: Optional[bool]
    is_organic_certified: Optional[bool]
    featured_image: Optional[str]