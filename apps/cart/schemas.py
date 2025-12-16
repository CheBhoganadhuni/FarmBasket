from typing import Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime
from uuid import UUID
from decimal import Decimal


# ===== INPUT SCHEMAS =====

class AddToCartSchema(BaseModel):
    """Schema for adding item to cart"""
    product_id: str
    quantity: int = Field(default=1, ge=1)


class UpdateCartItemSchema(BaseModel):
    """Schema for updating cart item quantity"""
    quantity: int = Field(..., ge=0)  # 0 means remove


# ===== OUTPUT SCHEMAS =====

class CartItemSchema(BaseModel):
    """Schema for cart item output"""
    id: str
    product_id: str
    product_name: str
    product_slug: str
    product_image: Optional[str]
    unit_price: Decimal
    quantity: int
    total_price: Decimal
    in_stock: bool
    available_quantity: int
    is_selected: bool # ✅ Exposed Selection State
    
    class Config:
        from_attributes = True
    
    @validator('id', 'product_id', pre=True)
    def convert_uuid_to_str(cls, v):
        if isinstance(v, UUID):
            return str(v)
        return v

    @validator('product_image', pre=True)
    def get_image_url(cls, v):
        # Handle field file or string
        if hasattr(v, 'url'):
            if v.url and v.url.startswith('http'):
                return v.url
            if hasattr(v, 'name') and v.name:
                v = v.name
        
        if isinstance(v, str) and v:
            if v.startswith('http'):
                return v
            
            clean_id = v.replace('/media/', '').lstrip('/')
            try:
                import cloudinary.utils
                return cloudinary.utils.cloudinary_url(clean_id, secure=True, format="jpg")[0]
            except ImportError:
                return v
        return None


class CartSchema(BaseModel):
    """Schema for cart output"""
    id: str
    items: list[CartItemSchema]
    items_count: int
    subtotal: Decimal
    total: Decimal
    updated_at: datetime
    
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
    cart_count: int = 0
