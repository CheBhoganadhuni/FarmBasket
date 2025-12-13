from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
import re
from uuid import UUID 

# ===== INPUT SCHEMAS =====

class UserRegisterSchema(BaseModel):
    """Schema for user registration"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    password_confirm: str = Field(..., min_length=8)
    first_name: str = Field(..., min_length=2, max_length=50)
    last_name: str = Field(..., min_length=2, max_length=50)
    phone: Optional[str] = None
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength"""
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one number')
        return v
    
    @validator('password_confirm')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('phone')
    def validate_phone(cls, v):
        if v and not re.match(r'^\+?[1-9]\d{9,14}$', v):
            raise ValueError('Invalid phone number format')
        return v


class UserLoginSchema(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class PasswordResetRequestSchema(BaseModel):
    """Schema for password reset request"""
    email: EmailStr


class PasswordResetConfirmSchema(BaseModel):
    """Schema for password reset confirmation"""
    token: str
    new_password: str = Field(..., min_length=8)
    new_password_confirm: str = Field(..., min_length=8)
    
    @validator('new_password_confirm')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v

class ChangePasswordSchema(BaseModel):
    """Schema for changing password while logged in"""
    old_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=6)
    confirm_password: str = Field(..., min_length=6)
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v


class UserUpdateSchema(BaseModel):
    """Schema for updating user profile"""
    first_name: Optional[str] = Field(None, min_length=2, max_length=50)
    last_name: Optional[str] = Field(None, min_length=2, max_length=50)
    phone: Optional[str] = None
    email_notifications: Optional[bool] = None
    sms_notifications: Optional[bool] = None


class AddressCreateSchema(BaseModel):
    """Schema for creating an address"""
    label: str = Field(..., max_length=50)
    address_type: str = Field(default='HOME')
    street_address: str = Field(..., max_length=255)
    apartment: Optional[str] = Field(None, max_length=100)
    city: str = Field(..., max_length=100)
    state: str = Field(..., max_length=100)
    postal_code: str = Field(..., max_length=10)
    landmark: Optional[str] = Field(None, max_length=255)
    phone: str = Field(..., max_length=15)
    is_default: bool = Field(default=False)


# ===== OUTPUT SCHEMAS =====

class UserSchema(BaseModel):
    """Schema for user output"""
    id: str  # ✅ Keep as str, will be converted from UUID
    email: str
    first_name: str
    last_name: str
    full_name: str
    phone: Optional[str]
    avatar_url: str
    xp_points: int
    loyalty_tier: str
    email_notifications: bool
    sms_notifications: bool = False
    is_active: bool
    created_at: datetime
    is_staff: bool
    is_superuser: bool
    
    created_at: datetime
    is_staff: bool
    is_superuser: bool
    
    social_avatar_url: Optional[str]
    
    class Config:
        from_attributes = True
        orm_mode = True
    
    @validator('id', pre=True)
    def convert_uuid_to_str(cls, v):
        """Convert UUID to string"""
        if isinstance(v, UUID):
            return str(v)
        return v

    from django.conf import settings

    @validator('avatar_url', pre=True, check_fields=False)
    def get_image_url(cls, v, values):
        """Ensure full Cloudinary URL for avatar"""
        if not v:
            return v
        
        # If it's already a full URL, ensure HTTPS and return
        if v.startswith('http'):
            return v.replace('http:', 'https:')
            
        # If it's a relative path containing 'media/', strip it to get the clean path
        if 'media/' in v:
            v = v.split('media/')[-1]
            
        # Get cloud name from settings
        cloud_name = 'dk75bbrar' # Fallback default observed from user
        try:
            if hasattr(settings, 'CLOUDINARY_STORAGE'):
                cloud_name = settings.CLOUDINARY_STORAGE.get('CLOUD_NAME', cloud_name)
            elif hasattr(settings, 'CLOUDINARY_CLOUD_NAME'):
                cloud_name = settings.CLOUDINARY_CLOUD_NAME
        except:
            pass
            
        return f"https://res.cloudinary.com/{cloud_name}/image/upload/{v}"


class AddressSchema(BaseModel):
    """Schema for address output"""
    id: str  # ✅ Keep as str
    label: str
    address_type: str
    street_address: str
    apartment: Optional[str]
    city: str
    state: str
    postal_code: str
    landmark: Optional[str]
    phone: str
    is_default: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
    
    @validator('id', pre=True)
    def convert_uuid_to_str(cls, v):
        """Convert UUID to string"""
        if isinstance(v, UUID):
            return str(v)
        return v


class TokenSchema(BaseModel):
    """Schema for JWT tokens"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    is_staff: bool
    is_superuser: bool



class MessageSchema(BaseModel):
    """Generic message response"""
    message: str
    success: bool = True

class AuthSchema(BaseModel):
    """Schema for authentication response"""
    access: str
    refresh: str
    user: UserSchema
    
    class Config:
        from_attributes = True

from ninja import Schema

class GoogleLoginSchema(Schema):
    id_token: str
