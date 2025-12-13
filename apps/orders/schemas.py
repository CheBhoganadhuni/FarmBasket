from typing import Optional, List
from pydantic import BaseModel, Field, validator
from datetime import datetime
from uuid import UUID
from decimal import Decimal


# ===== INPUT SCHEMAS =====

class CheckoutAddressSchema(BaseModel):
    """Schema for delivery address during checkout"""
    address_id: Optional[str] = None  # Use existing address
    name: str = Field(..., min_length=2, max_length=200)
    phone: str = Field(..., max_length=20)  # Relaxed validation
    address: str = Field(..., min_length=5) # Relaxed
    city: str = Field(..., min_length=2, max_length=100)
    state: str = Field(..., min_length=2, max_length=100)
    postal_code: str = Field(..., max_length=10) # Relaxed
    landmark: str = Field(default='', max_length=200)


class CreateOrderSchema(BaseModel):
    """Schema for creating an order"""
    delivery_address: CheckoutAddressSchema
    payment_method: str = Field(..., pattern='^(RAZORPAY|COD)$')
    order_notes: str = Field(default='', max_length=500)
    use_wallet: bool = False  # ✅ For ₹1 test payments
    payable_amount: Decimal

class VerifyPaymentSchema(BaseModel):
    """Schema for verifying Razorpay payment"""
    order_id: str
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str


# ===== OUTPUT SCHEMAS =====

class OrderItemSchema(BaseModel):
    """Schema for order item output"""
    id: str
    product_id: Optional[str]
    product_slug: Optional[str]
    product_name: str
    product_image: str
    unit_price: Decimal
    quantity: int
    total_price: Decimal
    
    class Config:
        from_attributes = True
    
    @validator('id', 'product_id', pre=True)
    def convert_uuid_to_str(cls, v):
        if v and isinstance(v, UUID):
            return str(v)
        return v if v else None


class OrderSchema(BaseModel):
    """Schema for order output"""
    id: str
    order_number: str
    status: str
    status_display: str
    
    # Delivery info
    delivery_name: str
    delivery_phone: str
    delivery_address: str
    delivery_city: str
    delivery_state: str
    delivery_postal_code: str
    delivery_postal_code: str
    delivery_landmark: str
    
    # Extra
    order_notes: Optional[str] = ''
    
    # Pricing
    subtotal: Decimal
    delivery_charge: Decimal
    discount: Decimal
    total: Decimal
    
    # Payment
    payment_method: str
    payment_status: str
    payment_status_display: str
    
    # Items
    items: List[OrderItemSchema]
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
    
    @validator('id', pre=True)
    def convert_uuid_to_str(cls, v):
        if isinstance(v, UUID):
            return str(v)
        return v


class OrderSummarySchema(BaseModel):
    """Lightweight order schema for list view"""
    id: str
    order_number: str
    status: str
    status_display: str
    payment_status: str
    total: Decimal
    items_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True
    
    @validator('id', pre=True)
    def convert_uuid_to_str(cls, v):
        if isinstance(v, UUID):
            return str(v)
        return v


class RazorpayOrderSchema(BaseModel):
    """Schema for Razorpay order creation response"""
    razorpay_order_id: str
    amount: int  # In paise (₹1 = 100 paise)
    currency: str
    key_id: str
    order_number: str


class MessageSchema(BaseModel):
    """Generic message response"""
    message: str
    success: bool = True
    order_id: Optional[str] = None
