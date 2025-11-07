from typing import List
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from ninja import Router, File
from ninja.errors import HttpError
from ninja.files import UploadedFile

from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, Address, PasswordResetToken
from .schemas import (
    UserRegisterSchema, 
    UserLoginSchema, 
    UserSchema, 
    TokenSchema,
    PasswordResetRequestSchema, 
    PasswordResetConfirmSchema,
    UserUpdateSchema, 
    AddressCreateSchema, 
    AddressSchema, 
    MessageSchema, 
    ChangePasswordSchema,
    AuthSchema  # ✅ Added
)
from .auth import (
    authenticate_user, create_access_token, create_refresh_token,
    get_password_hash, AuthBearer
)
from .emails import send_welcome_email, send_password_reset_email  # ✅ Changed from tasks to emails


router = Router(tags=['Authentication'])
auth = AuthBearer()


@router.post("/register", response=AuthSchema)
def register(request, data: UserRegisterSchema):
    """Register new user"""
    # Check if email already exists
    if User.objects.filter(email=data.email).exists():
        raise HttpError(400, "Email already registered")
    
    # Create user
    user = User.objects.create_user(
        email=data.email,
        password=data.password,
        first_name=data.first_name,
        last_name=data.last_name,
        phone=data.phone
    )
    
    # ✅ Generate JWT tokens
    refresh = RefreshToken.for_user(user)
    access = refresh.access_token
    
    # Send welcome email
    try:
        send_welcome_email(user)
    except Exception as e:
        print(f"Failed to send welcome email: {e}")
    
    # ✅ Convert user to UserSchema
    user_data = UserSchema.from_orm(user)
    
    return {
        'access': str(access),
        'refresh': str(refresh),
        'user': user_data
    }


@router.post("/login", response=TokenSchema)
def login(request, data: UserLoginSchema):
    """User login"""
    
    user = authenticate_user(data.email, data.password)
    
    if not user:
        raise HttpError(401, "Invalid email or password")
    
    # Update last login
    user.last_login = timezone.now()
    user.save(update_fields=['last_login'])
    
    # Generate tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.get("/me", response=UserSchema, auth=auth)
def get_current_user(request):
    """Get current user profile"""
    try:
        user = request.auth
        print(f"✅ Authenticated user: {user.email}")
        return user
    except Exception as e:
        print(f"❌ Error in /me endpoint: {e}")
        import traceback
        traceback.print_exc()
        raise


@router.put("/me", response=UserSchema, auth=auth)
def update_current_user(request, data: UserUpdateSchema):
    """Update current user profile"""
    
    user = request.auth
    
    for field, value in data.dict(exclude_unset=True).items():
        setattr(user, field, value)
    
    user.save()
    return user


@router.post("/password-reset/request", response=MessageSchema)
def request_password_reset(request, data: PasswordResetRequestSchema):
    """Request password reset"""
    
    try:
        user = User.objects.get(email=data.email, is_active=True)
        
        # Create reset token
        reset_token = PasswordResetToken.objects.create(
            user=user,
            expires_at=timezone.now() + timedelta(hours=1)
        )
        
        # Generate reset URL
        reset_url = f"http://127.0.0.1:8000/password-reset/{reset_token.token}/"
        
        # Send reset email
        send_password_reset_email(user, reset_url)
        
    except User.DoesNotExist:
        pass  # Don't reveal if email exists
    
    return {
        "message": "If your email is registered, you will receive a password reset link",
        "success": True
    }


@router.post("/password-reset/confirm", response=MessageSchema)
def confirm_password_reset(request, data: PasswordResetConfirmSchema):
    """Confirm password reset"""
    
    try:
        reset_token = PasswordResetToken.objects.get(token=data.token)
        
        if not reset_token.is_valid:
            raise HttpError(400, "Invalid or expired reset token")
        
        # Update password
        user = reset_token.user
        user.set_password(data.new_password)
        user.save()
        
        # Mark token as used
        reset_token.used = True
        reset_token.save()
        
        return {"message": "Password reset successful", "success": True}
        
    except PasswordResetToken.DoesNotExist:
        raise HttpError(400, "Invalid or expired reset token")


# ===== ADDRESS ENDPOINTS =====

@router.get("/addresses", response=List[AddressSchema], auth=auth)
def get_addresses(request):
    """Get all addresses for logged-in user"""
    user = request.auth
    addresses = Address.objects.filter(user=user).order_by('-is_default', '-created_at')
    
    return [
        {
            'id': str(addr.id),
            'label': addr.label,
            'address_type': addr.address_type,
            'street_address': addr.street_address,
            'apartment': addr.apartment or '',
            'city': addr.city,
            'state': addr.state,
            'postal_code': addr.postal_code,
            'landmark': addr.landmark or '',
            'phone': addr.phone,
            'is_default': addr.is_default,
            'created_at': addr.created_at
        }
        for addr in addresses
    ]


@router.post("/addresses", response=AddressSchema, auth=auth)
def create_address(request, data: AddressCreateSchema):
    """Create a new address"""
    
    # If this is set as default, unset other defaults
    if data.is_default:
        Address.objects.filter(user=request.auth).update(is_default=False)
    
    address = Address.objects.create(
        user=request.auth,
        **data.dict()
    )
    return address


@router.put("/addresses/{address_id}", response=AddressSchema, auth=auth)
def update_address(request, address_id: str, data: AddressCreateSchema):
    """Update an address"""
    
    address = get_object_or_404(Address, id=address_id, user=request.auth)
    
    # If this is set as default, unset other defaults
    if data.is_default:
        Address.objects.filter(user=request.auth).exclude(id=address_id).update(is_default=False)
    
    for field, value in data.dict().items():
        setattr(address, field, value)
    
    address.save()
    return address


@router.delete("/addresses/{address_id}", response=MessageSchema, auth=auth)
def delete_address(request, address_id: str):
    """Delete address"""
    user = request.auth
    
    try:
        address = Address.objects.get(id=address_id, user=user)
        address.delete()
        
        return MessageSchema(
            success=True,
            message="Address deleted successfully"
        )
    except Address.DoesNotExist:
        return MessageSchema(
            success=False,
            message="Address not found"
        )


@router.post("/change-password", response=MessageSchema, auth=auth)
def change_password(request, data: ChangePasswordSchema):
    """Change password for logged-in user"""
    user = request.auth
    
    # Verify old password
    if not user.check_password(data.old_password):
        return MessageSchema(
            success=False,
            message="Current password is incorrect"
        )
    
    # Set new password
    user.set_password(data.new_password)
    user.save()
    
    return MessageSchema(
        success=True,
        message="Password changed successfully"
    )


@router.delete("/account", response=MessageSchema, auth=auth)
def delete_account(request):
    """Delete user account and all related data"""
    user = request.auth
    
    # This will cascade delete:
    # - Orders, OrderItems
    # - Cart, CartItems
    # - Wishlist
    # - Addresses
    # - Reviews
    user.delete()
    
    return MessageSchema(
        success=True,
        message="Account deleted successfully"
    )


@router.post("/upload-avatar", response=MessageSchema, auth=auth)
def upload_avatar(request, avatar: UploadedFile = File(...)):
    """Upload user avatar"""
    user = request.auth
    
    # Validate file type
    if not avatar.content_type.startswith('image/'):
        return MessageSchema(
            success=False,
            message="Invalid file type. Please upload an image."
        )
    
    # Validate file size (5MB max)
    if avatar.size > 5 * 1024 * 1024:
        return MessageSchema(
            success=False,
            message="File too large. Maximum size is 5MB."
        )
    
    # Save avatar
    import os
    from django.core.files.storage import default_storage
    from django.core.files.base import ContentFile
    
    # Generate unique filename
    ext = avatar.name.split('.')[-1]
    filename = f'avatars/{user.id}_{timezone.now().timestamp()}.{ext}'
    
    # Save file
    path = default_storage.save(filename, ContentFile(avatar.read()))
    avatar_url = default_storage.url(path)
    
    # Update user
    user.avatar = path
    user.save()
    
    return MessageSchema(
        success=True,
        message="Avatar uploaded successfully",
        avatar_url=avatar_url
    )
