from typing import Optional, List
from pydantic import BaseModel, Field, validator
from datetime import datetime
from uuid import UUID
from uuid import UUID
from decimal import Decimal
import os


# ===== INPUT SCHEMAS =====

class ReviewCreateSchema(BaseModel):
    """Schema for creating a review"""
    product_id: str
    rating: int = Field(..., ge=1, le=5)
    title: str = Field(None, max_length=200)
    comment: str = Field(..., min_length=10)


# ===== OUTPUT SCHEMAS =====

class CategorySchema(BaseModel):
    """Schema for category output"""
    id: str
    name: str
    slug: str
    description: str
    icon: str
    is_active: bool
    product_count: int = 0
    
    class Config:
        from_attributes = True
    
    @validator('id', pre=True)
    def convert_uuid_to_str(cls, v):
        if isinstance(v, UUID):
            return str(v)
        return v


class ProductImageSchema(BaseModel):
    """Schema for product image"""
    id: str
    image: str
    alt_text: str
    
    class Config:
        from_attributes = True
    
    @validator('id', pre=True)
    def convert_uuid_to_str(cls, v):
        if isinstance(v, UUID):
            return str(v)
        return v
    
    @validator('image', pre=True)
    def get_image_url(cls, v):
        if hasattr(v, 'url'):
            return v.url
        return str(v)


class ProductListSchema(BaseModel):
    """Schema for product list (lightweight)"""
    id: str
    name: str
    slug: str
    category_name: str
    category_icon: str = '📦'  # ✅ Add this line with default
    price: Decimal
    discount_price: Optional[Decimal]
    display_price: Decimal
    discount_percentage: int
    unit: str
    unit_value: Decimal
    featured_image: Optional[str]
    is_featured: bool
    is_organic_certified: bool
    in_stock: bool
    is_low_stock: bool
    average_rating: float
    review_count: int
    
    class Config:
        from_attributes = True

    @validator('featured_image', pre=True)
    def get_image_url(cls, v):
        if v and hasattr(v, 'url'):
            return v.url
        if isinstance(v, str) and v:
            if v.startswith('http'):
                return v
            # Generate absolute Cloudinary URL from public_id
            try:
                import cloudinary.utils
                return cloudinary.utils.cloudinary_url(v, secure=True)[0]
            except ImportError:
                return v
        return None


class ProductDetailSchema(BaseModel):
    """Schema for product detail (full info)"""
    id: str
    name: str
    slug: str
    description: str
    farm_story: str
    category: CategorySchema
    price: Decimal
    discount_price: Optional[Decimal]
    display_price: Decimal
    discount_percentage: int
    unit: str
    unit_value: Decimal
    stock_quantity: int
    is_active: bool
    is_featured: bool
    is_organic_certified: bool
    in_stock: bool
    is_low_stock: bool
    featured_image: Optional[str]
    images: List[ProductImageSchema]
    average_rating: float
    review_count: int
    views_count: int
    created_at: datetime
    similar_products: List[ProductListSchema] = []  # ✅ Added field
    
    class Config:
        from_attributes = True
    
    @validator('id', pre=True)
    def convert_uuid_to_str(cls, v):
        if isinstance(v, UUID):
            return str(v)
        return v
    
    @validator('featured_image', pre=True)
    def get_image_url(cls, v):
        if v and hasattr(v, 'url'):
            return v.url
        if isinstance(v, str) and v:
            if v.startswith('http'):
                return v
            # Generate absolute Cloudinary URL from public_id
            try:
                import cloudinary.utils
                return cloudinary.utils.cloudinary_url(v, secure=True)[0]
            except ImportError:
                return v
        return None


class ReviewSchema(BaseModel):
    """Schema for review output"""
    id: str
    user_name: str
    rating: int
    title: str
    comment: str
    created_at: datetime
    
    class Config:
        from_attributes = True
    
    @validator('id', pre=True)
    def convert_uuid_to_str(cls, v):
        if isinstance(v, UUID):
            return str(v)
        return v


class MessageSchema(BaseModel):
    """Generic message response"""
    message: str
    success: bool = True
